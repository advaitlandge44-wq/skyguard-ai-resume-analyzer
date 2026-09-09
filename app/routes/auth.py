from flask import Blueprint, render_template, redirect, url_for, flash, request, session, g
from app.models import db, User, Analysis
from app.services.security import login_required, validate_email_address, validate_password_strength
from app.services.email import send_password_reset_email
from app import limiter

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("20 per minute")
def register():
    """Handles new user registration with strict validation."""
    if g.user:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validations
        if not name:
            flash('Please provide your full name.', 'danger')
            return render_template('auth/register.html', name=name, email=email)

        valid_email, normalized_or_err = validate_email_address(email)
        if not valid_email:
            flash(f'Invalid email: {normalized_or_err}', 'danger')
            return render_template('auth/register.html', name=name, email=email)
        email = normalized_or_err

        valid_pw, pw_err = validate_password_strength(password)
        if not valid_pw:
            flash(pw_err, 'danger')
            return render_template('auth/register.html', name=name, email=email)

        if password != confirm_password:
            flash('Passwords do not match. Please re-enter.', 'danger')
            return render_template('auth/register.html', name=name, email=email)

        # Check existing user
        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists. Please log in.', 'warning')
            return redirect(url_for('auth.login', email=email))

        # Create user
        try:
            new_user = User(name=name, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            # Automatic login upon successful registration
            session.clear()
            session['user_id'] = new_user.id
            flash('Account created successfully! Welcome to SkyGuard AI.', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('An unexpected error occurred during registration. Please try again.', 'danger')

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("30 per minute")
def login():
    """Handles user login with session protection."""
    if g.user:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not email or not password:
            flash('Please provide both email and password.', 'danger')
            return render_template('auth/login.html', email=email)

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            # Session fixation protection: clear session before setting user_id
            session.clear()
            session['user_id'] = user.id
            session.permanent = remember
            flash(f'Welcome back, {user.name}!', 'success')
            
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('auth/login.html', email=email)

    prefilled_email = request.args.get('email', '')
    return render_template('auth/login.html', email=prefilled_email)


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def forgot_password():
    """Handles password reset requests with anti-enumeration protection."""
    if g.user:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()

        if not email:
            flash('Please enter your email address.', 'danger')
            return render_template('auth/forgot_password.html', email=email)

        valid_email, normalized_or_err = validate_email_address(email)
        if not valid_email:
            flash(f'Invalid email: {normalized_or_err}', 'danger')
            return render_template('auth/forgot_password.html', email=email)

        email = normalized_or_err
        user = User.query.filter_by(email=email).first()

        if user:
            token = user.set_reset_token()
            db.session.commit()
            if email == 'demo@skyguard.ai':
                demo_reset_url = url_for('auth.reset_password', token=token)
                flash('Demo Mode: Live email dispatch is bypassed. You can proceed directly with the demonstration reset link below.', 'info')
                return render_template('auth/forgot_password.html', email_sent=True, email=email, is_demo_reset=True, demo_reset_url=demo_reset_url)
            
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            send_password_reset_email(user, reset_url)

        # Anti-enumeration: generic response regardless of whether account exists
        flash('If an account exists for this email, a password reset link has been sent.', 'info')
        return render_template('auth/forgot_password.html', email_sent=True, email=email)

    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
@limiter.limit("15 per minute")
def reset_password(token):
    """Handles password reset token validation and password change."""
    if g.user:
        return redirect(url_for('main.dashboard'))

    user = User.verify_reset_token(token)
    if not user:
        flash('The password reset link is invalid, expired, or has already been used. Please request a new one.', 'danger')
        return render_template('auth/reset_password.html', invalid_token=True)

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not password:
            flash('Please enter a new password.', 'danger')
            return render_template('auth/reset_password.html', token=token)

        if password != confirm_password:
            flash('Passwords do not match. Please re-enter.', 'danger')
            return render_template('auth/reset_password.html', token=token)

        valid_pw, pw_err = validate_password_strength(password)
        if not valid_pw:
            flash(pw_err, 'danger')
            return render_template('auth/reset_password.html', token=token)

        user.set_password(password)
        user.clear_reset_token()
        db.session.commit()

        flash('Password reset successful. You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """Destroys session and logs user out."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Displays user profile, analysis metrics, and allows password change."""
    user = g.user
    total_analyses = Analysis.query.filter_by(user_id=user.id).count()
    latest_analysis = Analysis.query.filter_by(user_id=user.id).order_by(Analysis.created_at.desc()).first()

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_profile':
            name = request.form.get('name', '').strip()
            if name:
                user.name = name
                db.session.commit()
                flash('Profile name updated successfully.', 'success')
            else:
                flash('Name cannot be blank.', 'danger')

        elif action == 'change_password':
            current_pw = request.form.get('current_password', '')
            new_pw = request.form.get('new_password', '')
            confirm_new_pw = request.form.get('confirm_new_password', '')

            if not user.check_password(current_pw):
                flash('Current password is incorrect.', 'danger')
            elif new_pw != confirm_new_pw:
                flash('New passwords do not match.', 'danger')
            else:
                valid_pw, pw_err = validate_password_strength(new_pw)
                if not valid_pw:
                    flash(pw_err, 'danger')
                else:
                    user.set_password(new_pw)
                    db.session.commit()
                    flash('Password changed successfully.', 'success')

    return render_template(
        'auth/profile.html',
        user=user,
        total_analyses=total_analyses,
        latest_analysis=latest_analysis
    )
