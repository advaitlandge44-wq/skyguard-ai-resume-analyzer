from datetime import datetime, timedelta, timezone
import re
from app.models import User, db
from app.services.email import get_test_outbox, clear_test_outbox
from app import create_app


def test_registration_success(client, app):
    """Test successful user registration."""
    response = client.post('/register', data={
        'name': 'Alice Smith',
        'email': 'alice@example.com',
        'password': 'StrongPassword123!',
        'confirm_password': 'StrongPassword123!'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Account created successfully' in response.data or b'Welcome' in response.data

    with app.app_context():
        user = User.query.filter_by(email='alice@example.com').first()
        assert user is not None
        assert user.name == 'Alice Smith'
        assert user.check_password('StrongPassword123!')
        assert not user.check_password('WrongPassword')


def test_registration_password_mismatch(client, app):
    """Test registration failure when passwords do not match."""
    response = client.post('/register', data={
        'name': 'Bob Jones',
        'email': 'bob@example.com',
        'password': 'Password123!',
        'confirm_password': 'DifferentPassword123!'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Passwords do not match' in response.data

    with app.app_context():
        assert User.query.filter_by(email='bob@example.com').first() is None


def test_registration_duplicate_email(client, auth_user):
    """Test registration failure when email already exists."""
    response = client.post('/register', data={
        'name': 'Another Person',
        'email': 'candidate@university.edu',
        'password': 'NewPassword123!',
        'confirm_password': 'NewPassword123!'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'already exists' in response.data


def test_registration_short_password(client):
    """Test registration failure on short passwords."""
    response = client.post('/register', data={
        'name': 'Charlie',
        'email': 'charlie@example.com',
        'password': 'short',
        'confirm_password': 'short'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'at least 8 characters' in response.data


def test_login_success(client, auth_user):
    """Test user login with valid credentials."""
    response = client.post('/login', data={
        'email': 'candidate@university.edu',
        'password': 'SecurePassword123!'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Welcome back' in response.data or b'Dashboard' in response.data


def test_login_invalid_password(client, auth_user):
    """Test login failure with incorrect password."""
    response = client.post('/login', data={
        'email': 'candidate@university.edu',
        'password': 'WrongPassword123!'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Invalid email or password' in response.data


def test_logout(authenticated_client):
    """Test user logout."""
    response = authenticated_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'logged out' in response.data or b'Sign in' in response.data


def test_login_page_has_forgot_password_link(client):
    """Test that login page prominently features the Forgot Password link."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Forgot Password?' in response.data
    assert b'/forgot-password' in response.data


def test_forgot_password_page_loads(client):
    """Test that forgot password page renders properly with form fields."""
    response = client.get('/forgot-password')
    assert response.status_code == 200
    assert b'Reset Your Password' in response.data
    assert b'Send Reset Link' in response.data


def test_forgot_password_valid_email(client, app, auth_user):
    """Test requesting reset link with a valid registered email."""
    clear_test_outbox()

    response = client.post('/forgot-password', data={
        'email': 'candidate@university.edu'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'If an account exists for this email, a password reset link has been sent.' in response.data

    outbox = get_test_outbox()
    assert len(outbox) == 1
    assert outbox[0]['to'] == 'candidate@university.edu'
    assert '/reset-password/' in outbox[0]['reset_url']

    with app.app_context():
        user = db.session.get(User, auth_user)
        assert user.reset_token_hash is not None
        assert user.reset_token_expires_at is not None
        expires_at = user.reset_token_expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        assert expires_at > datetime.now(timezone.utc)


def test_forgot_password_unregistered_email_anti_enumeration(client, app):
    """Test requesting reset link with unregistered email yields identical generic response."""
    clear_test_outbox()

    response = client.post('/forgot-password', data={
        'email': 'nonexistent@company.org'
    }, follow_redirects=True)

    assert response.status_code == 200
    # Must give generic response to prevent account enumeration
    assert b'If an account exists for this email, a password reset link has been sent.' in response.data

    outbox = get_test_outbox()
    assert len(outbox) == 0


def test_forgot_password_invalid_email_format(client):
    """Test validation on invalid email address syntax."""
    response = client.post('/forgot-password', data={
        'email': 'not-a-valid-email'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Invalid email' in response.data


def test_reset_password_page_with_valid_token(client, app, auth_user):
    """Test loading reset password page with a valid token."""
    with app.app_context():
        user = db.session.get(User, auth_user)
        token = user.set_reset_token()
        db.session.commit()

    response = client.get(f'/reset-password/{token}')
    assert response.status_code == 200
    assert b'Set New Password' in response.data
    assert b'Reset Password' in response.data


def test_reset_password_invalid_token(client):
    """Test accessing reset password with an invalid token."""
    response = client.get('/reset-password/totally-invalid-random-token', follow_redirects=True)
    assert response.status_code == 200
    assert b'invalid, expired, or has already been used' in response.data
    assert b'Request New Reset Link' in response.data or b'/forgot-password' in response.data


def test_reset_password_expired_token(client, app, auth_user):
    """Test accessing reset password with an expired token."""
    with app.app_context():
        user = db.session.get(User, auth_user)
        token = user.set_reset_token()
        # Manually expire the token
        user.reset_token_expires_at = datetime.now(timezone.utc) - timedelta(minutes=10)
        db.session.commit()

    response = client.get(f'/reset-password/{token}', follow_redirects=True)
    assert response.status_code == 200
    assert b'invalid, expired, or has already been used' in response.data


def test_reset_password_mismatch(client, app, auth_user):
    """Test submitting mismatched passwords on reset."""
    with app.app_context():
        user = db.session.get(User, auth_user)
        token = user.set_reset_token()
        db.session.commit()

    response = client.post(f'/reset-password/{token}', data={
        'password': 'BrandNewPassword123!',
        'confirm_password': 'MismatchedPassword123!'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Passwords do not match' in response.data

    with app.app_context():
        user = db.session.get(User, auth_user)
        # Old password still intact
        assert user.check_password('SecurePassword123!')
        assert not user.check_password('BrandNewPassword123!')


def test_reset_password_short_password(client, app, auth_user):
    """Test submitting password that fails policy (< 8 chars)."""
    with app.app_context():
        user = db.session.get(User, auth_user)
        token = user.set_reset_token()
        db.session.commit()

    response = client.post(f'/reset-password/{token}', data={
        'password': 'short',
        'confirm_password': 'short'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'at least 8 characters' in response.data


def test_reset_password_success_and_login_flow(client, app, auth_user):
    """Full lifecycle: request reset, perform reset, verify single use, login with new and reject old."""
    clear_test_outbox()

    # Step 1: Request reset
    req_resp = client.post('/forgot-password', data={
        'email': 'candidate@university.edu'
    }, follow_redirects=True)
    assert req_resp.status_code == 200

    outbox = get_test_outbox()
    assert len(outbox) == 1
    reset_url = outbox[0]['reset_url']
    # Extract token from url
    token = reset_url.split('/reset-password/')[-1]

    # Step 2: Reset password successfully
    reset_resp = client.post(f'/reset-password/{token}', data={
        'password': 'BrandNewSecurePassword123!',
        'confirm_password': 'BrandNewSecurePassword123!'
    }, follow_redirects=True)

    assert reset_resp.status_code == 200
    assert b'Password reset successful' in reset_resp.data

    # Step 3: Single-use check (token reuse must fail)
    reuse_resp = client.get(f'/reset-password/{token}', follow_redirects=True)
    assert b'invalid, expired, or has already been used' in reuse_resp.data

    # Step 4: Login with old password must fail
    old_login_resp = client.post('/login', data={
        'email': 'candidate@university.edu',
        'password': 'SecurePassword123!'
    }, follow_redirects=True)
    assert b'Invalid email or password' in old_login_resp.data

    # Step 5: Login with new password must succeed
    new_login_resp = client.post('/login', data={
        'email': 'candidate@university.edu',
        'password': 'BrandNewSecurePassword123!'
    }, follow_redirects=True)
    assert new_login_resp.status_code == 200
    assert b'Welcome back' in new_login_resp.data or b'Dashboard' in new_login_resp.data


def test_multiple_reset_requests_invalidates_earlier_tokens(client, app, auth_user):
    """Test that requesting multiple tokens invalidates earlier tokens."""
    clear_test_outbox()

    # Request 1
    client.post('/forgot-password', data={'email': 'candidate@university.edu'})
    outbox1 = get_test_outbox()
    token1 = outbox1[-1]['reset_url'].split('/reset-password/')[-1]

    # Request 2
    client.post('/forgot-password', data={'email': 'candidate@university.edu'})
    outbox2 = get_test_outbox()
    token2 = outbox2[-1]['reset_url'].split('/reset-password/')[-1]

    assert token1 != token2

    # Earlier token should fail
    resp1 = client.get(f'/reset-password/{token1}', follow_redirects=True)
    assert b'invalid, expired, or has already been used' in resp1.data

    # Latest token should work
    resp2 = client.get(f'/reset-password/{token2}')
    assert resp2.status_code == 200
    assert b'Set New Password' in resp2.data


def test_password_reset_csrf_protection(app, auth_user):
    """Verify that CSRF protection is active when WTF_CSRF_ENABLED is True."""
    csrf_app = create_app('testing')
    csrf_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': True,
        'RATELIMIT_ENABLED': False,
        'SECRET_KEY': 'test-secret-key-csrf'
    })

    with csrf_app.app_context():
        db.create_all()
        user = User(name="CSRF Candidate", email="csrf@example.com")
        user.set_password("OldPassword123!")
        token = user.set_reset_token()
        db.session.add(user)
        db.session.commit()

        csrf_client = csrf_app.test_client()

        # POST without CSRF token should be rejected (400 Bad Request)
        post_resp = csrf_client.post(f'/reset-password/{token}', data={
            'password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!'
        })
        assert post_resp.status_code == 400

