import os
import json
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, g, abort, send_file
from app.models import db, Resume, Analysis
from app.services.security import login_required, generate_safe_filename, sanitize_text
from app.services.pdf_parser import extract_resume_text, ResumeExtractionError
from app.services.openai_service import analyze_resume_with_ai
from app import limiter

logger = logging.getLogger(__name__)

resume_bp = Blueprint('resume', __name__)

POPULAR_ROLES = [
    "Python Developer",
    "Full Stack Developer",
    "Backend Developer",
    "Frontend Developer",
    "Data Analyst",
    "Data Scientist",
    "Software Engineer",
    "Web Developer",
    "DevOps Engineer",
    "Machine Learning Engineer",
    "Cloud Solutions Architect",
    "Cybersecurity Analyst",
    "Product Manager",
    "QA / Test Automation Engineer"
]


@resume_bp.route('/upload', methods=['GET', 'POST'])
@login_required
@limiter.limit("15 per minute")
def upload():
    """Renders upload page and processes resume text extraction & AI analysis."""
    if request.method == 'POST':
        target_role_select = request.form.get('target_role_select', '').strip()
        custom_role = request.form.get('custom_role', '').strip()
        job_description = request.form.get('job_description', '').strip()
        
        # Determine target role
        target_role = custom_role if custom_role else target_role_select
        if not target_role:
            flash('Please select or enter a target job role.', 'danger')
            return render_template('resume/upload.html', popular_roles=POPULAR_ROLES, job_description=job_description)

        # Validate file presence
        if 'resume_file' not in request.files:
            flash('Please select a resume file (PDF or TXT) to upload.', 'danger')
            return render_template('resume/upload.html', popular_roles=POPULAR_ROLES, target_role=target_role, job_description=job_description)

        file = request.files['resume_file']
        if not file or file.filename == '':
            flash('No file selected. Please choose a PDF or TXT resume.', 'danger')
            return render_template('resume/upload.html', popular_roles=POPULAR_ROLES, target_role=target_role, job_description=job_description)

        # Validate extension
        clean_display_name, stored_filename, ext = generate_safe_filename(file.filename)

        if ext not in current_app.config['ALLOWED_EXTENSIONS']:
            flash(f"Unsupported file type (.{ext}). Only .pdf and .txt files are allowed.", 'danger')
            return render_template('resume/upload.html', popular_roles=POPULAR_ROLES, target_role=target_role, job_description=job_description)

        # Save to uploads directory
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], stored_filename)
        try:
            file.save(save_path)
            file_size = os.path.getsize(save_path)

            if file_size == 0:
                try:
                    os.remove(save_path)
                except OSError:
                    pass
                flash('The uploaded file is completely empty.', 'danger')
                return render_template('resume/upload.html', popular_roles=POPULAR_ROLES, target_role=target_role, job_description=job_description)

            if file_size > current_app.config['MAX_CONTENT_LENGTH']:
                try:
                    os.remove(save_path)
                except OSError:
                    pass
                flash('The uploaded file exceeds the 5MB maximum size limit.', 'danger')
                return render_template('resume/upload.html', popular_roles=POPULAR_ROLES, target_role=target_role, job_description=job_description)

            # Extract & normalize text from document
            extracted_text = extract_resume_text(save_path, ext)
            sanitized_text = sanitize_text(extracted_text)

        except ResumeExtractionError as e:
            if os.path.exists(save_path):
                try:
                    os.remove(save_path)
                except OSError:
                    pass
            flash(str(e), 'danger')
            return render_template('resume/upload.html', popular_roles=POPULAR_ROLES, target_role=target_role, job_description=job_description)
        except Exception as e:
            if os.path.exists(save_path):
                try:
                    os.remove(save_path)
                except OSError:
                    pass
            logger.error(f"Unexpected file extraction error: {e}", exc_info=True)
            flash('Failed to process the uploaded resume file. Please ensure it is a valid document.', 'danger')
            return render_template('resume/upload.html', popular_roles=POPULAR_ROLES, target_role=target_role, job_description=job_description)

        # Save Resume in Database
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
            db.session.flush()  # get resume.id

            # Trigger AI / Fallback Analysis
            analysis_data = analyze_resume_with_ai(
                resume_text=sanitized_text,
                target_role=target_role,
                job_description=sanitize_text(job_description, max_length=5000)
            )

            # Store Analysis record
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

            flash('Resume analyzed successfully!', 'success')
            return redirect(url_for('analysis.results', id=analysis.id))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Analysis creation error: {e}", exc_info=True)
            flash('An error occurred during analysis. Please try again.', 'danger')
            return render_template('resume/upload.html', popular_roles=POPULAR_ROLES, target_role=target_role, job_description=job_description)

    return render_template('resume/upload.html', popular_roles=POPULAR_ROLES)


@resume_bp.route('/view/<int:resume_id>')
@login_required
def view_resume(resume_id: int):
    """View extracted text of a user's resume."""
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != g.user.id:
        abort(403)
    return render_template('resume/view.html', resume=resume)
