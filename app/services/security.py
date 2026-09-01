import os
import re
import uuid
from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify, g
from werkzeug.utils import secure_filename
import email_validator
from app.models import db, User


def login_required(f):
    """Decorator to require login for view routes or API endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'success': False, 'error': 'Authentication required. Please log in.'}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        # Verify user still exists in DB
        user = db.session.get(User, user_id)
        if not user:
            session.clear()
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'success': False, 'error': 'Invalid session. Please log in again.'}), 401
            flash('Your session has expired. Please log in again.', 'warning')
            return redirect(url_for('auth.login'))
        
        g.user = user
        return f(*args, **kwargs)
    return decorated_function


def validate_email_address(email: str) -> tuple[bool, str]:
    """Validates email format and domain structure."""
    if not email or not isinstance(email, str):
        return False, "Email address is required."
    
    email = email.strip()
    if len(email) > 120:
        return False, "Email address is too long."

    try:
        validated = email_validator.validate_email(email, check_deliverability=False)
        return True, validated.normalized
    except email_validator.EmailNotValidError as e:
        return False, str(e)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Ensures password meets minimum security standards."""
    if not password or not isinstance(password, str):
        return False, "Password is required."
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    
    if len(password) > 128:
        return False, "Password cannot exceed 128 characters."
        
    return True, ""


def generate_safe_filename(original_filename: str) -> tuple[str, str, str]:
    """
    Creates a safe, collision-resistant filename and returns:
    (sanitized_display_name, secure_storage_name, extension)
    """
    if not original_filename:
        original_filename = "resume.pdf"
    
    clean_name = secure_filename(original_filename)
    if not clean_name:
        clean_name = "resume.pdf"
    
    # Extract extension
    _, ext = os.path.splitext(clean_name)
    ext_clean = ext.lower().lstrip('.')
    
    # Storage filename with unique UUID prefix
    unique_prefix = uuid.uuid4().hex
    stored_name = f"{unique_prefix}.{ext_clean}" if ext_clean else f"{unique_prefix}.bin"
    
    return clean_name, stored_name, ext_clean


def sanitize_text(text: str, max_length: int = 100000) -> str:
    """Removes null bytes and bounds text length to prevent memory abuse."""
    if not text:
        return ""
    text = str(text).replace('\x00', '')
    if len(text) > max_length:
        text = text[:max_length]
    return text.strip()
