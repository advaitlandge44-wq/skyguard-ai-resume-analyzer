import io
import os
import re
import json
import pytest
from app import create_app
from app.models import db, User, Analysis


@pytest.fixture
def api_client():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_api_health_check(api_client):
    """Verify that /api/health returns 200 OK for Render health monitoring."""
    resp = api_client.get('/api/health')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'healthy'
    assert 'SkyGuard AI Backend' in data['service']


def test_api_auth_lifecycle(api_client):
    """Verify API register, me, login, and logout endpoints with session cookies."""
    # 1. Register
    reg_resp = api_client.post('/api/auth/register', json={
        'name': 'API Candidate',
        'email': 'api_candidate@example.com',
        'password': 'SecurePassword123!',
        'confirm_password': 'SecurePassword123!'
    })
    assert reg_resp.status_code == 201
    reg_data = reg_resp.get_json()
    assert reg_data['success'] is True
    assert reg_data['user']['email'] == 'api_candidate@example.com'

    # 2. Check /api/auth/me (authenticated)
    me_resp = api_client.get('/api/auth/me')
    assert me_resp.status_code == 200
    me_data = me_resp.get_json()
    assert me_data['authenticated'] is True
    assert me_data['user']['name'] == 'API Candidate'

    # 3. Logout
    logout_resp = api_client.post('/api/auth/logout')
    assert logout_resp.status_code == 200
    assert logout_resp.get_json()['success'] is True

    # Check /api/auth/me (unauthenticated)
    me_after = api_client.get('/api/auth/me')
    assert me_after.status_code == 200
    assert me_after.get_json()['authenticated'] is False

    # 4. Login
    login_resp = api_client.post('/api/auth/login', json={
        'email': 'api_candidate@example.com',
        'password': 'SecurePassword123!'
    })
    assert login_resp.status_code == 200
    assert login_resp.get_json()['success'] is True


def test_api_resume_roles(api_client):
    """Verify that /api/resume/roles returns the 25 target job roles."""
    resp = api_client.get('/api/resume/roles')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert len(data['popular_roles']) >= 25
    assert 'Software Developer' in data['popular_roles']
    assert 'Data Scientist' in data['popular_roles']
    assert 'DevOps Engineer' in data['popular_roles']


def test_api_resume_upload_and_analysis_lifecycle(api_client):
    """Verify API upload, analysis retrieval, dashboard data, and history."""
    # Register and log in
    api_client.post('/api/auth/register', json={
        'name': 'DevOps Tester',
        'email': 'devops_tester@example.com',
        'password': 'SecurePassword123!',
        'confirm_password': 'SecurePassword123!'
    })

    # Upload resume
    resume_content = (
        "ALEX MORGAN\n"
        "Senior Backend Developer\n"
        "Skills: Python, Flask, SQL, Docker, AWS, PostgreSQL, Redis, REST APIs\n"
        "Experience: Built microservices handling 25,000 requests per second with 99.99% uptime.\n"
        "Projects: Automated CI/CD deployment pipelines using GitHub Actions and Docker Compose.\n"
        "Education: Bachelor of Science in Computer Science."
    )
    upload_data = {
        'target_role_select': 'DevOps Engineer',
        'custom_role': '',
        'job_description': 'Seeking a DevOps Engineer proficient in AWS, Docker, CI/CD, and infrastructure monitoring.',
        'resume_file': (io.BytesIO(resume_content.encode('utf-8')), 'alex_devops.txt')
    }

    upload_resp = api_client.post('/api/resume/upload', data=upload_data, content_type='multipart/form-data')
    assert upload_resp.status_code == 201
    res = upload_resp.get_json()
    assert res['success'] is True
    analysis_id = res['analysis_id']

    # Retrieve analysis data
    analysis_resp = api_client.get(f'/api/analysis/{analysis_id}')
    assert analysis_resp.status_code == 200
    analysis_data = analysis_resp.get_json()
    assert analysis_data['success'] is True
    assert analysis_data['analysis']['target_role'] == 'DevOps Engineer'
    assert analysis_data['analysis']['overall_score'] > 0

    # Retrieve dashboard data
    dash_resp = api_client.get('/api/dashboard')
    assert dash_resp.status_code == 200
    dash_data = dash_resp.get_json()
    assert dash_data['success'] is True
    assert dash_data['stats']['total_analyses'] == 1
    assert len(dash_data['recent_analyses']) == 1

    # Retrieve history
    hist_resp = api_client.get('/api/history?q=DevOps')
    assert hist_resp.status_code == 200
    hist_data = hist_resp.get_json()
    assert hist_data['success'] is True
    assert hist_data['total'] == 1


def test_api_bullet_improver(api_client):
    """Verify that bullet point improver API works for authenticated users."""
    api_client.post('/api/auth/register', json={
        'name': 'Bullet User',
        'email': 'bullet_user@example.com',
        'password': 'SecurePassword123!',
        'confirm_password': 'SecurePassword123!'
    })

    resp = api_client.post('/api/improve-bullet', json={
        'bullet_text': 'I worked on writing unit tests and fixed several software bugs.',
        'target_role': 'Software Developer'
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert len(data['improved']) > 10


def test_api_demo_data(api_client):
    """Verify that /api/demo/data supplies demo user and resume analysis."""
    resp = api_client.get('/api/demo/data')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['is_demo'] is True
    assert data['user']['email'] == 'demo@skyguard.ai'
    assert data['analysis']['overall_score'] >= 70


def test_frontend_zero_secrets_and_structure():
    """Audit the frontend directory to ensure no private keys or secrets are exposed."""
    frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
    assert os.path.exists(frontend_dir), "frontend/ directory must exist"

    # Required files in frontend
    required_files = [
        'index.html', 'upload.html', 'results.html', 'dashboard.html',
        'history.html', 'roadmap.html', 'login.html', 'register.html',
        'forgot_password.html', 'reset_password.html', 'vercel.json',
        'css/variables.css', 'css/main.css', 'css/dashboard.css', 'css/results.css',
        'js/config.js', 'js/api.js', 'js/hero_3d.js', 'js/main.js',
        'js/upload.js', 'js/results.js', 'js/chat.js', 'js/improver.js'
    ]
    for rf in required_files:
        p = os.path.join(frontend_dir, rf)
        assert os.path.exists(p), f"Missing required frontend file: {rf}"

    # Secret pattern regexes
    secret_patterns = [
        re.compile(r'sk-[a-zA-Z0-9]{20,}', re.IGNORECASE),  # OpenAI API key pattern
        re.compile(r'postgres://|postgresql://', re.IGNORECASE),  # DB URL
        re.compile(r'SECRET_KEY\s*=\s*[\'"][^\'"]+[\'"]'),  # Flask SECRET_KEY
    ]

    for root, _, files in os.walk(frontend_dir):
        for f in files:
            file_path = os.path.join(root, f)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as content_file:
                content = content_file.read()
                for pattern in secret_patterns:
                    assert not pattern.search(content), f"Potential secret found in frontend file: {file_path}"


def test_render_deployment_files():
    """Verify Procfile and render.yaml exist and have correct configuration."""
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    
    procfile = os.path.join(base_dir, 'Procfile')
    assert os.path.exists(procfile)
    with open(procfile, 'r') as f:
        p_content = f.read()
        assert 'gunicorn' in p_content
        assert 'run:app' in p_content

    render_yaml = os.path.join(base_dir, 'render.yaml')
    assert os.path.exists(render_yaml)
    with open(render_yaml, 'r') as f:
        r_content = f.read()
        assert 'gunicorn run:app' in r_content
        assert '/api/health' in r_content
        assert 'FLASK_CONFIG' in r_content


def test_vercel_rewrites_and_config_fallback():
    """Verify vercel.json contains /api/(.*) rewrite and config.js has reliable Render default."""
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    vercel_json_path = os.path.join(base_dir, 'frontend', 'vercel.json')
    assert os.path.exists(vercel_json_path)
    with open(vercel_json_path, 'r') as f:
        v_data = json.load(f)
        rewrites = v_data.get('rewrites', [])
        api_rewrite = next((r for r in rewrites if '/api/' in r.get('source', '')), None)
        assert api_rewrite is not None, "vercel.json must have /api/ rewrite to Render backend"
        assert 'onrender.com' in api_rewrite.get('destination', '')

    config_js_path = os.path.join(base_dir, 'frontend', 'js', 'config.js')
    assert os.path.exists(config_js_path)
    with open(config_js_path, 'r', encoding='utf-8') as f:
        c_content = f.read()
        assert 'PRODUCTION_BACKEND_URL' in c_content
        assert 'onrender.com' in c_content

    api_js_path = os.path.join(base_dir, 'frontend', 'js', 'api.js')
    assert os.path.exists(api_js_path)
    with open(api_js_path, 'r', encoding='utf-8') as f:
        a_content = f.read()
        assert 'extractErrorMessage' in a_content
        assert '[object Object]' in a_content  # Sanitization check


def test_api_registration_validation_errors(api_client):
    """Verify that backend registration returns clean string error messages with exact HTTP status codes."""
    # 1. Missing name -> 400
    r1 = api_client.post('/api/auth/register', json={'name': '', 'email': 'test@example.com', 'password': 'Password123!', 'confirm_password': 'Password123!'})
    assert r1.status_code == 400
    assert r1.get_json()['success'] is False
    assert isinstance(r1.get_json()['error'], str)
    assert 'full name' in r1.get_json()['error'].lower()

    # 2. Invalid email -> 400
    r2 = api_client.post('/api/auth/register', json={'name': 'User', 'email': 'invalid-email', 'password': 'Password123!', 'confirm_password': 'Password123!'})
    assert r2.status_code == 400
    assert r2.get_json()['success'] is False
    assert isinstance(r2.get_json()['error'], str)

    # 3. Weak password -> 400
    r3 = api_client.post('/api/auth/register', json={'name': 'User', 'email': 'valid@example.com', 'password': 'short', 'confirm_password': 'short'})
    assert r3.status_code == 400
    assert r3.get_json()['success'] is False
    assert isinstance(r3.get_json()['error'], str)

    # 4. Mismatched passwords -> 400
    r4 = api_client.post('/api/auth/register', json={'name': 'User', 'email': 'valid@example.com', 'password': 'Password123!', 'confirm_password': 'Different123!'})
    assert r4.status_code == 400
    assert r4.get_json()['success'] is False
    assert 'match' in r4.get_json()['error'].lower()

    # 5. Success -> 201
    r5 = api_client.post('/api/auth/register', json={'name': 'Valid User', 'email': 'valid_user@example.com', 'password': 'Password123!', 'confirm_password': 'Password123!'})
    assert r5.status_code == 201
    assert r5.get_json()['success'] is True
    assert r5.get_json()['user']['email'] == 'valid_user@example.com'

    # 6. Duplicate registration -> 409
    r6 = api_client.post('/api/auth/register', json={'name': 'Valid User', 'email': 'valid_user@example.com', 'password': 'Password123!', 'confirm_password': 'Password123!'})
    assert r6.status_code == 409
    assert r6.get_json()['success'] is False
    assert 'already exists' in r6.get_json()['error'].lower()

