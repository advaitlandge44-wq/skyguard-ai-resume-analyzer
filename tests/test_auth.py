from app.models import User, db


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
