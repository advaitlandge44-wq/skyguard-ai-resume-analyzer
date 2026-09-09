import os
import json
import logging
from flask import Blueprint, request, jsonify, g, session, current_app, url_for
from app.models import db, User, Resume, Analysis, ChatMessage
from app.services.security import (
    login_required, sanitize_text, validate_email_address,
    validate_password_strength, generate_safe_filename
)
from app.services.pdf_parser import extract_resume_text, ResumeExtractionError
from app.services.openai_service import ask_resume_assistant, improve_resume_bullet, analyze_resume_with_ai
from app.services.career_roadmap_engine import TARGET_JOB_ROLES, ROLE_CATEGORIES
from app.services.email import send_password_reset_email
from app.services.demo_service import get_or_create_demo_user, get_or_create_demo_analysis
from app import limiter

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)


# ==============================================================================
# 1. SYSTEM & HEALTH CHECK
# ==============================================================================

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Render monitoring and deployment verification."""
    return jsonify({
        'status': 'healthy',
        'service': 'SkyGuard AI Backend',
        'version': '1.0.0'
    }), 200


# ==============================================================================
# 2. AUTHENTICATION API ENDPOINTS
# ==============================================================================

@api_bp.route('/auth/me', methods=['GET'])
def get_current_user():
    """Returns the current authenticated user profile or unauthenticated status."""
    user = getattr(g, 'user', None)
    if not user:
        return jsonify({
            'authenticated': False,
            'user': None
        }), 200

    return jsonify({
        'authenticated': True,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'is_demo': session.get('is_demo', False)
        }
    }), 200


@api_bp.route('/auth/register', methods=['POST'])
@limiter.limit("20 per minute")
def api_register():
    """API endpoint for new user registration."""
    data = request.get_json(silent=True) or request.form or {}
    name = sanitize_text(data.get('name', ''), max_length=100)
    email = sanitize_text(data.get('email', ''), max_length=120).lower()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')

    if not name:
        return jsonify({'success': False, 'error': 'Please provide your full name.'}), 400

    valid_email, normalized_or_err = validate_email_address(email)
    if not valid_email:
        return jsonify({'success': False, 'error': f'Invalid email: {normalized_or_err}'}), 400
    email = normalized_or_err

    valid_pw, pw_err = validate_password_strength(password)
    if not valid_pw:
        return jsonify({'success': False, 'error': pw_err}), 400

    if password != confirm_password:
        return jsonify({'success': False, 'error': 'Passwords do not match.'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'error': 'An account with this email already exists.'}), 409

    try:
        new_user = User(name=name, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        session.clear()
        session['user_id'] = new_user.id

        return jsonify({
            'success': True,
            'message': 'Account created successfully.',
            'user': {
                'id': new_user.id,
                'name': new_user.name,
                'email': new_user.email
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"API Registration error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Failed to create account. Please try again.'}), 500


@api_bp.route('/auth/login', methods=['POST'])
@limiter.limit("30 per minute")
def api_login():
    """API endpoint for user login with session cookie creation."""
    data = request.get_json(silent=True) or request.form or {}
    email = sanitize_text(data.get('email', ''), max_length=120).lower()
    password = data.get('password', '')
    remember = bool(data.get('remember', False))

    if not email or not password:
        return jsonify({'success': False, 'error': 'Please provide both email and password.'}), 400

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        session.clear()
        session['user_id'] = user.id
        session.permanent = remember

        return jsonify({
            'success': True,
            'message': f'Welcome back, {user.name}!',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email
            }
        }), 200

    return jsonify({'success': False, 'error': 'Invalid email or password.'}), 401


@api_bp.route('/auth/logout', methods=['POST', 'GET'])
def api_logout():
    """API endpoint to destroy session and log out."""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully.'}), 200


@api_bp.route('/auth/forgot-password', methods=['POST'])
@limiter.limit("10 per minute")
def api_forgot_password():
    """API endpoint for password reset request."""
    data = request.get_json(silent=True) or request.form or {}
    email = sanitize_text(data.get('email', ''), max_length=120).lower()

    if not email:
        return jsonify({'success': False, 'error': 'Please provide an email address.'}), 400

    valid_email, normalized_or_err = validate_email_address(email)
    if not valid_email:
        return jsonify({'success': False, 'error': f'Invalid email: {normalized_or_err}'}), 400
    email = normalized_or_err

    user = User.query.filter_by(email=email).first()
    if user:
        token = user.set_reset_token()
        db.session.commit()

        if email == 'demo@skyguard.ai':
            return jsonify({
                'success': True,
                'is_demo_reset': True,
                'demo_reset_url': url_for('auth.reset_password', token=token),
                'message': 'Demo mode: password reset token generated.'
            }), 200

        reset_url = url_for('auth.reset_password', token=token, _external=True)
        send_password_reset_email(user, reset_url)

    # Anti-enumeration response
    return jsonify({
        'success': True,
        'message': 'If an account exists for this email, a password reset link has been dispatched.'
    }), 200


@api_bp.route('/auth/reset-password/<token>', methods=['POST'])
@limiter.limit("15 per minute")
def api_reset_password(token: str):
    """API endpoint for setting new password with token."""
    user = User.verify_reset_token(token)
    if not user:
        return jsonify({'success': False, 'error': 'Invalid or expired password reset token.'}), 400

    data = request.get_json(silent=True) or request.form or {}
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')

    if not password:
        return jsonify({'success': False, 'error': 'Please provide a new password.'}), 400

    if password != confirm_password:
        return jsonify({'success': False, 'error': 'Passwords do not match.'}), 400

    valid_pw, pw_err = validate_password_strength(password)
    if not valid_pw:
        return jsonify({'success': False, 'error': pw_err}), 400

    user.set_password(password)
    user.clear_reset_token()
    db.session.commit()

    return jsonify({'success': True, 'message': 'Password has been reset successfully. You can now log in.'}), 200


# ==============================================================================
# 3. RESUME & ANALYSIS API ENDPOINTS
# ==============================================================================

@api_bp.route('/resume/roles', methods=['GET'])
def get_job_roles():
    """Returns the list of 25 popular target job roles and their categories."""
    return jsonify({
        'success': True,
        'popular_roles': TARGET_JOB_ROLES,
        'categories': ROLE_CATEGORIES
    }), 200


@api_bp.route('/resume/upload', methods=['POST'])
@login_required
@limiter.limit("15 per minute")
def api_upload_resume():
    """API endpoint for uploading resume and executing AI analysis."""
    target_role_select = request.form.get('target_role_select', '').strip()
    custom_role = request.form.get('custom_role', '').strip()
    job_description = request.form.get('job_description', '').strip()
    target_role = custom_role if custom_role else target_role_select

    if not target_role:
        return jsonify({'success': False, 'error': 'Please select or enter a target job role.'}), 400

    if 'resume_file' not in request.files:
        return jsonify({'success': False, 'error': 'No resume file uploaded.'}), 400

    file = request.files['resume_file']
    if not file or file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected. Please select a PDF or TXT resume.'}), 400

    clean_display_name, stored_filename, ext = generate_safe_filename(file.filename)

    if ext not in current_app.config['ALLOWED_EXTENSIONS']:
        return jsonify({'success': False, 'error': f"Unsupported file extension (.{ext}). Only .pdf and .txt files are accepted."}), 400

    save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], stored_filename)
    try:
        file.save(save_path)
        file_size = os.path.getsize(save_path)

        if file_size == 0:
            if os.path.exists(save_path):
                os.remove(save_path)
            return jsonify({'success': False, 'error': 'The uploaded file is empty.'}), 400

        if file_size > current_app.config['MAX_CONTENT_LENGTH']:
            if os.path.exists(save_path):
                os.remove(save_path)
            return jsonify({'success': False, 'error': 'File exceeds maximum size limit (5MB).'}), 413

        extracted_text = extract_resume_text(save_path, ext)
        sanitized_text = sanitize_text(extracted_text)

    except ResumeExtractionError as e:
        if os.path.exists(save_path):
            try:
                os.remove(save_path)
            except OSError:
                pass
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        if os.path.exists(save_path):
            try:
                os.remove(save_path)
            except OSError:
                pass
        logger.error(f"Upload text extraction error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Failed to process document content.'}), 500

    try:
        resume = Resume(
            user_id=g.user.id,
            filename=clean_display_name,
            target_role=target_role,
            stored_filename=stored_filename,
            file_size=file_size,
            file_type=ext,
            extracted_text=sanitized_text
        )
        db.session.add(resume)
        db.session.flush()

        analysis_data = analyze_resume_with_ai(
            resume_text=sanitized_text,
            target_role=target_role,
            job_description=sanitize_text(job_description, max_length=5000)
        )

        analysis = Analysis(
            user_id=g.user.id,
            resume_id=resume.id,
            target_role=target_role,
            job_description=job_description if job_description else None,
            overall_score=analysis_data.get('overall_score', 75),
            ats_score=analysis_data.get('ats_score', 75),
            job_match_score=analysis_data.get('job_match_score', 70),
            summary=analysis_data.get('summary', ''),
            analysis_json=json.dumps(analysis_data)
        )
        db.session.add(analysis)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Resume analyzed successfully.',
            'analysis_id': analysis.id,
            'target_role': target_role,
            'overall_score': analysis.overall_score,
            'ats_score': analysis.ats_score,
            'job_match_score': analysis.job_match_score
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Analysis storage error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Failed to complete analysis. Please try again.'}), 500


@api_bp.route('/analysis/<int:analysis_id>', methods=['GET'])
@login_required
def get_analysis_data(analysis_id: int):
    """Returns full analysis report, metrics, and roadmap data as JSON."""
    analysis = Analysis.query.get_or_404(analysis_id)
    if analysis.user_id != g.user.id:
        return jsonify({'success': False, 'error': 'Unauthorized access.'}), 403

    chat_messages = ChatMessage.query.filter_by(analysis_id=analysis.id).order_by(ChatMessage.created_at.asc()).all()

    return jsonify({
        'success': True,
        'analysis': {
            'id': analysis.id,
            'target_role': analysis.target_role,
            'created_at': analysis.created_at.isoformat() if analysis.created_at else None,
            'overall_score': analysis.overall_score,
            'ats_score': analysis.ats_score,
            'job_match_score': analysis.job_match_score,
            'summary': analysis.summary,
            'data': analysis.parsed_data,
            'chat_history': [
                {
                    'id': m.id,
                    'role': m.role,
                    'content': m.content,
                    'created_at': m.created_at.strftime('%I:%M %p') if m.created_at else ''
                } for m in chat_messages
            ]
        }
    }), 200


@api_bp.route('/analysis/<int:analysis_id>/delete', methods=['POST', 'DELETE'])
@login_required
def api_delete_analysis(analysis_id: int):
    """Deletes an analysis session and linked chat history."""
    analysis = Analysis.query.get_or_404(analysis_id)
    if analysis.user_id != g.user.id:
        return jsonify({'success': False, 'error': 'Unauthorized access.'}), 403

    try:
        db.session.delete(analysis)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Analysis deleted successfully.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to delete analysis record.'}), 500


# ==============================================================================
# 4. DASHBOARD & HISTORY API ENDPOINTS
# ==============================================================================

@api_bp.route('/dashboard', methods=['GET'])
@login_required
def get_dashboard_data():
    """Returns user stats, score averages, and recent analyses list."""
    user = g.user
    user_analyses = Analysis.query.filter_by(user_id=user.id).order_by(Analysis.created_at.desc())
    total_analyses = user_analyses.count()
    recent = user_analyses.limit(5).all()

    if total_analyses > 0:
        all_records = user_analyses.all()
        avg_resume = int(sum(a.overall_score for a in all_records) / total_analyses)
        avg_ats = int(sum(a.ats_score for a in all_records) / total_analyses)
        avg_match = int(sum(a.job_match_score for a in all_records) / total_analyses)
    else:
        avg_resume = avg_ats = avg_match = 0

    latest_analysis = recent[0] if recent else None

    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email
        },
        'stats': {
            'total_analyses': total_analyses,
            'avg_resume_score': avg_resume,
            'avg_ats_score': avg_ats,
            'avg_match_score': avg_match
        },
        'latest_analysis': {
            'id': latest_analysis.id,
            'target_role': latest_analysis.target_role,
            'overall_score': latest_analysis.overall_score,
            'ats_score': latest_analysis.ats_score,
            'job_match_score': latest_analysis.job_match_score,
            'summary': latest_analysis.summary,
            'created_at': latest_analysis.created_at.strftime('%b %d, %Y') if latest_analysis.created_at else ''
        } if latest_analysis else None,
        'recent_analyses': [
            {
                'id': a.id,
                'target_role': a.target_role,
                'overall_score': a.overall_score,
                'ats_score': a.ats_score,
                'job_match_score': a.job_match_score,
                'created_at': a.created_at.strftime('%b %d, %Y') if a.created_at else ''
            } for a in recent
        ]
    }), 200


@api_bp.route('/history', methods=['GET'])
@login_required
def get_history_data():
    """Returns full history with query filtering and sorting."""
    user = g.user
    search_query = request.args.get('q', '').strip()
    sort_key = request.args.get('sort', 'date')

    query = Analysis.query.filter_by(user_id=user.id)
    if search_query:
        query = query.filter(Analysis.target_role.ilike(f"%{search_query}%"))

    allowed_sorts = {
        'date': Analysis.created_at.desc(),
        'score': Analysis.overall_score.desc(),
        'ats': Analysis.ats_score.desc(),
        'match': Analysis.job_match_score.desc()
    }
    order_clause = allowed_sorts.get(sort_key, Analysis.created_at.desc())
    analyses = query.order_by(order_clause).all()

    return jsonify({
        'success': True,
        'total': len(analyses),
        'search_query': search_query,
        'current_sort': sort_key,
        'analyses': [
            {
                'id': a.id,
                'target_role': a.target_role,
                'overall_score': a.overall_score,
                'ats_score': a.ats_score,
                'job_match_score': a.job_match_score,
                'summary': a.summary,
                'created_at': a.created_at.strftime('%b %d, %Y') if a.created_at else ''
            } for a in analyses
        ]
    }), 200


@api_bp.route('/demo/data', methods=['GET'])
def get_demo_data():
    """Returns pre-loaded demo user and analysis data."""
    demo_user = get_or_create_demo_user()
    demo_analysis = get_or_create_demo_analysis(demo_user)
    session.clear()
    session['user_id'] = demo_user.id
    session['is_demo'] = True

    return jsonify({
        'success': True,
        'is_demo': True,
        'user': {
            'id': demo_user.id,
            'name': demo_user.name,
            'email': demo_user.email
        },
        'analysis_id': demo_analysis.id,
        'analysis': {
            'id': demo_analysis.id,
            'target_role': demo_analysis.target_role,
            'overall_score': demo_analysis.overall_score,
            'ats_score': demo_analysis.ats_score,
            'job_match_score': demo_analysis.job_match_score,
            'summary': demo_analysis.summary,
            'data': demo_analysis.parsed_data
        }
    }), 200


# ==============================================================================
# 5. AI INTERACTIVE CHAT & RESUME IMPROVER
# ==============================================================================

@api_bp.route('/chat/<int:analysis_id>', methods=['POST'])
@login_required
@limiter.limit("30 per minute")
def chat_assistant(analysis_id: int):
    """Contextual AI career assistant chat endpoint scoped to specific analysis with full skill-gap context."""
    analysis = db.session.get(Analysis, analysis_id)
    if not analysis or analysis.user_id != g.user.id:
        return jsonify({'success': False, 'error': 'Analysis session not found or unauthorized.'}), 404

    data = request.get_json(silent=True) or {}
    user_message = sanitize_text(data.get('message', ''), max_length=1000)

    if not user_message:
        return jsonify({'success': False, 'error': 'Message content cannot be empty.'}), 400

    try:
        past_messages = ChatMessage.query.filter_by(analysis_id=analysis.id).order_by(ChatMessage.created_at.asc()).all()
        history = [{'role': m.role, 'content': m.content} for m in past_messages]

        reply = ask_resume_assistant(
            chat_history=history,
            user_message=user_message,
            analysis_summary=analysis.summary or f"Resume analyzed for role {analysis.target_role}",
            target_role=analysis.target_role,
            analysis_data=analysis.parsed_data
        )

        msg_user = ChatMessage(
            analysis_id=analysis.id,
            user_id=g.user.id,
            role='user',
            content=user_message
        )
        msg_assistant = ChatMessage(
            analysis_id=analysis.id,
            user_id=g.user.id,
            role='assistant',
            content=reply
        )
        db.session.add(msg_user)
        db.session.add(msg_assistant)
        db.session.commit()

        return jsonify({
            'success': True,
            'reply': reply,
            'created_at': msg_assistant.created_at.strftime('%I:%M %p')
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Chat assistant error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Failed to process chat message.'}), 500


@api_bp.route('/improve-bullet', methods=['POST'])
@login_required
@limiter.limit("30 per minute")
def improve_bullet():
    """AJAX endpoint for rewriting resume bullet points with STAR impact."""
    data = request.get_json(silent=True) or {}
    bullet_text = sanitize_text(data.get('bullet_text', ''), max_length=1500)
    target_role = sanitize_text(data.get('target_role', 'Software Engineer'), max_length=100)

    if not bullet_text or len(bullet_text.strip()) < 5:
        return jsonify({
            'success': False,
            'error': 'Please enter a bullet point or description to improve (minimum 5 characters).'
        }), 400

    result = improve_resume_bullet(bullet_text=bullet_text, target_role=target_role)
    return jsonify(result)
