import json
from app.models import db, User, Resume, Analysis, ChatMessage
from app.services.security import sanitize_text


def test_unauthorized_routes_redirect_to_login(client):
    """Ensure protected routes reject unauthenticated sessions."""
    routes = ['/dashboard', '/history', '/resume/upload', '/profile', '/analysis/results/1', '/my-resumes', '/roadmap']
    for r in routes:
        response = client.get(r, follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.headers['Location']


def test_cross_user_isolation(client, app):
    """Ensure User A cannot view or delete User B's analysis records (IDOR Protection)."""
    with app.app_context():
        # Create User A
        user_a = User(name="User Alpha", email="alpha@test.com")
        user_a.set_password("PasswordAlpha123!")
        db.session.add(user_a)
        
        # Create User B
        user_b = User(name="User Beta", email="beta@test.com")
        user_b.set_password("PasswordBeta123!")
        db.session.add(user_b)
        db.session.flush()

        # Create resume and analysis for User B
        resume_b = Resume(
            user_id=user_b.id,
            filename="beta_resume.pdf",
            stored_filename="beta_resume_uuid.pdf",
            extracted_text="Beta resume text content."
        )
        db.session.add(resume_b)
        db.session.flush()

        analysis_b = Analysis(
            user_id=user_b.id,
            resume_id=resume_b.id,
            target_role="Full Stack Developer",
            overall_score=85,
            ats_score=88,
            job_match_score=80,
            analysis_json=json.dumps({"summary": "Beta analysis"})
        )
        db.session.add(analysis_b)
        db.session.commit()
        analysis_b_id = analysis_b.id
        resume_b_id = resume_b.id
        user_a_id = user_a.id

    # Log in as User A
    with client.session_transaction() as sess:
        sess['user_id'] = user_a_id

    # User A tries to view User B's analysis -> must return 403 Forbidden
    response = client.get(f'/analysis/results/{analysis_b_id}')
    assert response.status_code == 403

    # User A tries to view User B's resume -> must return 403 Forbidden
    resume_view_resp = client.get(f'/resume/view/{resume_b_id}')
    assert resume_view_resp.status_code == 403

    # User A tries to delete User B's analysis -> must return 403 Forbidden
    delete_response = client.post(f'/analysis/delete/{analysis_b_id}')
    assert delete_response.status_code == 403

    # User A tries to post chat message to User B's analysis -> must return 404/403
    chat_response = client.post(f'/api/chat/{analysis_b_id}', json={'message': 'Unauthorized chat attempt'})
    assert chat_response.status_code in [403, 404]

    # Verify User B's analysis and resume are still safe in the database
    with app.app_context():
        assert db.session.get(Analysis, analysis_b_id) is not None
        assert db.session.get(Resume, resume_b_id) is not None


def test_sql_injection_defense_in_login(client, app):
    """Ensure SQL injection payloads in login form do not authenticate or crash."""
    with app.app_context():
        user = User(name="Legitimate User", email="legit@test.com")
        user.set_password("LegitPassword123!")
        db.session.add(user)
        db.session.commit()

    sqli_payloads = [
        "' OR '1'='1",
        "' OR 1=1 --",
        "admin' --",
        "' UNION SELECT * FROM users --",
        "1' OR '1'='1"
    ]

    for payload in sqli_payloads:
        resp = client.post('/login', data={'email': payload, 'password': 'Password123!'}, follow_redirects=True)
        assert resp.status_code == 200
        assert b"Invalid email or password" in resp.data
        # Ensure session was not created
        with client.session_transaction() as sess:
            assert 'user_id' not in sess


def test_sql_injection_defense_in_search(client, app):
    """Ensure SQL injection in search parameters does not crash or leak data."""
    with app.app_context():
        user = User(name="Search Tester", email="search@test.com")
        user.set_password("SearchPassword123!")
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    with client.session_transaction() as sess:
        sess['user_id'] = user_id

    sqli_search_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "1' UNION SELECT 1,2,3,4,5,6,7,8,9,10 --"
    ]

    for payload in sqli_search_payloads:
        resp = client.get(f'/history?q={payload}')
        assert resp.status_code == 200
        assert b"Analysis History" in resp.data


def test_password_hashing(app):
    """Ensure plain-text passwords are never stored in the database."""
    with app.app_context():
        plain_pw = "SuperSecretPlainText123"
        user = User(name="Security Test", email="sec@test.com")
        user.set_password(plain_pw)
        
        assert user.password_hash != plain_pw
        assert user.password_hash.startswith("scrypt:") or user.password_hash.startswith("pbkdf2:")
        assert user.check_password(plain_pw)
        assert not user.check_password("WrongPassword")


def test_sanitize_text_null_bytes():
    """Ensure null bytes and oversized payloads are stripped."""
    malicious = "Hello\x00World\x00Inject"
    cleaned = sanitize_text(malicious)
    assert "\x00" not in cleaned
    assert cleaned == "HelloWorldInject"
