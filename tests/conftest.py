import os
import tempfile
import pytest
from app import create_app
from app.models import db, User, Resume, Analysis, ChatMessage


@pytest.fixture
def app():
    """Create and configure a clean Flask application instance for testing."""
    test_upload_dir = tempfile.mkdtemp()
    
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'UPLOAD_FOLDER': test_upload_dir,
        'RATELIMIT_ENABLED': False,
        'OPENAI_API_KEY': ''
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def auth_user(app):
    """Creates a sample test user in the database."""
    with app.app_context():
        user = User(name="Test Candidate", email="candidate@university.edu")
        user.set_password("SecurePassword123!")
        db.session.add(user)
        db.session.commit()
        # Refresh from session
        user_id = user.id
        return user_id


@pytest.fixture
def authenticated_client(client, auth_user):
    """Logs the test client in with the auth_user."""
    with client.session_transaction() as sess:
        sess['user_id'] = auth_user
    return client
