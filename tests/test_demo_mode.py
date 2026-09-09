import json
from app.models import User, Resume, Analysis, db
from app.services.demo_service import DEMO_USER_EMAIL, DEMO_TARGET_ROLE, SAMPLE_RESUME_TEXT


def test_try_demo_activation(client, app):
    """Test activating demo mode via /demo creates sample resume and analysis automatically."""
    response = client.get('/demo')
    assert response.status_code == 200
    assert b'Sample Resume' in response.data
    assert b'Alex Patil' in response.data
    assert b'Python Developer' in response.data
    assert b'AUTOMATIC DEMO MODE' in response.data

    with client.session_transaction() as sess:
        assert sess.get('is_demo') is True
        demo_user_id = sess.get('user_id')
        assert demo_user_id is not None

    with app.app_context():
        demo_user = db.session.get(User, demo_user_id)
        assert demo_user.email == DEMO_USER_EMAIL
        assert 'Alex Patil' in demo_user.name

        resume = Resume.query.filter_by(user_id=demo_user.id).first()
        assert resume is not None
        assert 'Alex_Patil' in resume.filename
        assert resume.target_role == DEMO_TARGET_ROLE

        analysis = Analysis.query.filter_by(user_id=demo_user.id).first()
        assert analysis is not None
        assert analysis.overall_score == 82
        assert analysis.ats_score == 86
        assert analysis.job_match_score == 78


def test_demo_results_page_content(client, app):
    """Test results page in Demo Mode shows expected demonstration metrics, skills, and roadmap."""
    # Activate demo
    client.get('/demo')

    with app.app_context():
        demo_user = User.query.filter_by(email=DEMO_USER_EMAIL).first()
        analysis = Analysis.query.filter_by(user_id=demo_user.id).first()
        analysis_id = analysis.id

    # View results page
    resp = client.get(f'/analysis/results/{analysis_id}')
    assert resp.status_code == 200
    assert b'82' in resp.data
    assert b'86' in resp.data
    assert b'78' in resp.data
    assert b'Python' in resp.data
    assert b'Flask' in resp.data
    assert b'Docker' in resp.data
    assert b'AWS' in resp.data
    assert b'DEMO MODE' in resp.data
    assert b'Alex Patil' in resp.data


def test_demo_views_navigation(client, app):
    """Test that all dashboard views work cleanly for the demo user."""
    client.get('/demo')

    # Dashboard
    dash_resp = client.get('/dashboard')
    assert dash_resp.status_code == 200
    assert b'Alex Patil' in dash_resp.data
    assert b'82' in dash_resp.data

    # History
    hist_resp = client.get('/history')
    assert hist_resp.status_code == 200
    assert b'Python Developer' in hist_resp.data

    # Roadmap
    road_resp = client.get('/roadmap')
    assert road_resp.status_code == 200
    assert b'Python Advanced' in road_resp.data
    assert b'Docker' in road_resp.data
    assert b'AWS' in road_resp.data

    # My Resumes
    res_resp = client.get('/my-resumes')
    assert res_resp.status_code == 200
    assert b'Alex_Patil' in res_resp.data


def test_demo_ai_career_assistant_chat(client, app):
    """Test AI Career Assistant responds deterministically with demo resume context."""
    client.get('/demo')

    with app.app_context():
        demo_user = User.query.filter_by(email=DEMO_USER_EMAIL).first()
        analysis = Analysis.query.filter_by(user_id=demo_user.id).first()
        analysis_id = analysis.id

    # Test improvement question
    r1 = client.post(f'/api/chat/{analysis_id}', json={'message': 'How can I improve this resume?'})
    assert r1.status_code == 200
    d1 = r1.get_json()
    assert d1['success'] is True
    assert 'NovaTech' in d1['reply'] or 'Docker' in d1['reply'] or 'AWS' in d1['reply']

    # Test skills question
    r2 = client.post(f'/api/chat/{analysis_id}', json={'message': 'What skills should I learn?'})
    assert r2.status_code == 200
    d2 = r2.get_json()
    assert 'Docker' in d2['reply']
    assert 'AWS' in d2['reply']

    # Test role readiness question
    r3 = client.post(f'/api/chat/{analysis_id}', json={'message': 'Am I ready for a Python Developer role?'})
    assert r3.status_code == 200
    d3 = r3.get_json()
    assert '86%' in d3['reply'] or 'Mid-Level' in d3['reply']

    # Test interview prep question
    r4 = client.post(f'/api/chat/{analysis_id}', json={'message': 'What interview questions should I prepare?'})
    assert r4.status_code == 200
    d4 = r4.get_json()
    assert 'Python' in d4['reply'] or 'Flask' in d4['reply']


def test_demo_bullet_improver_api(client, app):
    """Test STAR bullet improver works in demo mode."""
    client.get('/demo')

    resp = client.post('/api/improve-bullet', json={
        'bullet_text': 'Made a website using Python and Flask with database.',
        'target_role': 'Python Developer'
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert len(data['improved']) > len(data['original'])
    assert 'why_better' in data


def test_demo_exit_flow(client):
    """Test exiting demo mode clears session and returns to landing page."""
    client.get('/demo')
    with client.session_transaction() as sess:
        assert sess.get('is_demo') is True

    exit_resp = client.get('/demo/exit', follow_redirects=True)
    assert exit_resp.status_code == 200
    assert b'You have exited Demo Mode' in exit_resp.data

    with client.session_transaction() as sess:
        assert sess.get('is_demo') is None
        assert sess.get('user_id') is None


def test_demo_forgot_password_handler(client, app):
    """Test submitting demo user email on forgot password gives direct presentation reset link."""
    # Ensure demo user exists
    client.get('/demo')
    client.get('/demo/exit')

    resp = client.post('/forgot-password', data={'email': 'demo@skyguard.ai'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Demo Reset Ready' in resp.data or b'Open Demo Reset Form' in resp.data
