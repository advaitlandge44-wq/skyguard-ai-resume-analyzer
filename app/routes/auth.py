from flask import Blueprint, render_template, redirect, url_for, flash, request, session, g
from app.models import db, User, Analysis
from app.services.security import login_required, validate_email_address, validate_password_strength
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
