from flask import Blueprint, request, jsonify, g
from app.models import db, Analysis, ChatMessage
from app.services.security import login_required, sanitize_text
from app.services.openai_service import ask_resume_assistant, improve_resume_bullet
from app import limiter

api_bp = Blueprint('api', __name__)


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
        # Load conversation history for this analysis
        past_messages = ChatMessage.query.filter_by(analysis_id=analysis.id).order_by(ChatMessage.created_at.asc()).all()
        history = [{'role': m.role, 'content': m.content} for m in past_messages]

        # Call AI assistant with parsed analysis data context
        reply = ask_resume_assistant(
            chat_history=history,
            user_message=user_message,
            analysis_summary=analysis.summary or f"Resume analyzed for role {analysis.target_role}",
            target_role=analysis.target_role,
            analysis_data=analysis.parsed_data
        )

        # Persist messages in database
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
