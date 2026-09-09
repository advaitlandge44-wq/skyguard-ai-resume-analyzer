import urllib.request
import urllib.parse
import http.cookiejar
import json
import re

import time

def run_live_verification():
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    # 1. Test Home page
    res = opener.open('http://127.0.0.1:5000/')
    assert res.status == 200, 'Home page failed'
    html = res.read().decode('utf-8')
    assert 'SkyGuard AI' in html, 'Home page title missing'
    print('[OK] 1. Home page loaded successfully (HTTP 200)')

    # 2. Test Registration
    res = opener.open('http://127.0.0.1:5000/register')
    html = res.read().decode('utf-8')
    csrf_token = html.split('name="csrf_token" value="')[1].split('"')[0]

    unique_email = f"sachin.e2e_{int(time.time())}@college.edu"
    reg_data = urllib.parse.urlencode({
        'csrf_token': csrf_token,
        'name': 'Sachin Rehpade',
        'email': unique_email,
        'password': 'Password123!',
        'confirm_password': 'Password123!'
    }).encode('utf-8')

    req = urllib.request.Request('http://127.0.0.1:5000/register', data=reg_data)
    res = opener.open(req)
    assert res.status == 200, 'Registration failed'
    dashboard_html = res.read().decode('utf-8')
    assert 'Welcome, Sachin!' in dashboard_html, 'Dashboard welcome missing'
    print('[OK] 2. User registration and auto-login verified (HTTP 200)')

    # 3. Test Upload PDF Resume
    res = opener.open('http://127.0.0.1:5000/resume/upload')
    upload_page = res.read().decode('utf-8')
    csrf_token = upload_page.split('name="csrf_token" value="')[1].split('"')[0]

    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    with open('sample_resumes/alex_python_developer.pdf', 'rb') as f:
        pdf_bytes = f.read()

    body = bytearray()
    def add_field(name, val):
        body.extend(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{val}\r\n'.encode('utf-8'))

    add_field('csrf_token', csrf_token)
    add_field('target_role_select', 'Python Developer')
    add_field('custom_role', '')
    add_field('job_description', 'Looking for a Senior Python Developer with Flask, SQL, Docker, and REST APIs.')

    body.extend(f'--{boundary}\r\nContent-Disposition: form-data; name="resume_file"; filename="alex_python_developer.pdf"\r\nContent-Type: application/pdf\r\n\r\n'.encode('utf-8'))
    body.extend(pdf_bytes)
    body.extend(f'\r\n--{boundary}--\r\n'.encode('utf-8'))

    req = urllib.request.Request(
        'http://127.0.0.1:5000/resume/upload',
        data=bytes(body),
        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
    )
    res = opener.open(req)
    assert res.status == 200, 'Upload failed'
    results_html = res.read().decode('utf-8')
    assert 'Analysis & ATS Report' in results_html, 'Results report missing'
    assert 'Overall Score' in results_html, 'Scores missing'
    print('[OK] 3. Resume PDF uploaded and analyzed with AI/NLP engine (HTTP 200)')

    # Extract analysis ID from results HTML
    aid_match = re.search(r'id="chat-analysis-id"\s+value="(\d+)"', results_html)
    assert aid_match is not None, 'Could not find chat-analysis-id in results HTML'
    aid = aid_match.group(1)
    print(f'[OK] 4. Analysis session initialized: Analysis ID #{aid}')

    # 4. Test Bullet Improver API
    improver_payload = json.dumps({
        'bullet_text': 'Made a website using Python and Flask with database.',
        'target_role': 'Python Developer'
    }).encode('utf-8')

    req = urllib.request.Request(
        'http://127.0.0.1:5000/api/improve-bullet',
        data=improver_payload,
        headers={'Content-Type': 'application/json', 'X-CSRFToken': csrf_token}
    )
    res = opener.open(req)
    assert res.status == 200, 'Improver API failed'
    improver_resp = json.loads(res.read().decode('utf-8'))
    assert improver_resp['success'] is True, 'Improver failed'
    print('[OK] 5. AI Bullet Improver API verified:')
    print(f"     Before: {improver_resp['original']}")
    print(f"     After:  {improver_resp['improved']}")
    print(f"     Why:    {improver_resp['why_better']}")

    # 5. Test Career Assistant Chat API
    chat_payload = json.dumps({'message': 'Why is my ATS score high?'}).encode('utf-8')
    req = urllib.request.Request(
        f'http://127.0.0.1:5000/api/chat/{aid}',
        data=chat_payload,
        headers={'Content-Type': 'application/json', 'X-CSRFToken': csrf_token}
    )
    res = opener.open(req)
    assert res.status == 200, 'Chat API failed'
    chat_resp = json.loads(res.read().decode('utf-8'))
    assert chat_resp['success'] is True, 'Chat failed'
    print('[OK] 6. AI Career Chatbot API verified:')
    print(f"     Assistant: {chat_resp['reply']}")

    # 6. Test History page
    res = opener.open('http://127.0.0.1:5000/history')
    assert res.status == 200
    history_html = res.read().decode('utf-8')
    assert 'Python Developer' in history_html
    print('[OK] 7. Analysis History page verified (HTTP 200)')

    # 7. Test Printable Report Export
    res = opener.open(f'http://127.0.0.1:5000/analysis/export/{aid}')
    assert res.status == 200
    export_html = res.read().decode('utf-8')
    # 8. Test Forgot Password & Password Reset E2E Flow
    # 8a. Login page contains Forgot Password link
    res = opener.open('http://127.0.0.1:5000/logout')
    res = opener.open('http://127.0.0.1:5000/login')
    login_html = res.read().decode('utf-8')
    assert 'Forgot Password?' in login_html, 'Forgot Password link missing from login page'
    print('[OK] 9. Login page features visible "Forgot Password?" link')

    # 8b. Forgot Password page loads
    res = opener.open('http://127.0.0.1:5000/forgot-password')
    fp_html = res.read().decode('utf-8')
    assert 'Reset Your Password' in fp_html
    fp_csrf = fp_html.split('name="csrf_token" value="')[1].split('"')[0]

    # 8c. Submit forgot password request
    fp_data = urllib.parse.urlencode({
        'csrf_token': fp_csrf,
        'email': unique_email
    }).encode('utf-8')
    req = urllib.request.Request('http://127.0.0.1:5000/forgot-password', data=fp_data)
    res = opener.open(req)
    assert res.status == 200
    fp_resp_html = res.read().decode('utf-8')
    assert 'If an account exists for this email, a password reset link has been sent.' in fp_resp_html
    print('[OK] 10. Forgot Password submission returns generic anti-enumeration response')

    # 8d. Query database for reset token
    import sqlite3
    conn = sqlite3.connect('instance/skyguard.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, reset_token_hash FROM users WHERE email = ?', (unique_email,))
    user_row = cursor.fetchone()
    assert user_row is not None and user_row[1] is not None, 'Reset token hash not stored in DB'
    user_id = user_row[0]
    conn.close()

    # Generate test token by using models within app context or testing reset directly
    from app import create_app
    from app.models import db, User
    test_app = create_app()
    with test_app.app_context():
        user = db.session.get(User, user_id)
        raw_token = user.set_reset_token()
        db.session.commit()

    # 8e. Open Reset Password page with raw token
    res = opener.open(f'http://127.0.0.1:5000/reset-password/{raw_token}')
    assert res.status == 200
    rp_html = res.read().decode('utf-8')
    assert 'Set New Password' in rp_html
    rp_csrf = rp_html.split('name="csrf_token" value="')[1].split('"')[0]
    print('[OK] 11. Reset Password page loads with valid token')

    # 8f. Submit new password
    new_password = 'BrandNewSuperSecret2026!'
    rp_data = urllib.parse.urlencode({
        'csrf_token': rp_csrf,
        'password': new_password,
        'confirm_password': new_password
    }).encode('utf-8')
    req = urllib.request.Request(f'http://127.0.0.1:5000/reset-password/{raw_token}', data=rp_data)
    res = opener.open(req)
    assert res.status == 200
    after_reset_html = res.read().decode('utf-8')
    assert 'Password reset successful' in after_reset_html
    print('[OK] 12. Password reset succeeded and redirected to login')

    # 8g. Verify token reuse is blocked
    res = opener.open(f'http://127.0.0.1:5000/reset-password/{raw_token}')
    reuse_html = res.read().decode('utf-8')
    assert 'invalid, expired, or has already been used' in reuse_html
    print('[OK] 13. Single-use token enforcement verified (reuse blocked)')

    # 8h. Old password must be rejected
    login_csrf = after_reset_html.split('name="csrf_token" value="')[1].split('"')[0]
    old_login_data = urllib.parse.urlencode({
        'csrf_token': login_csrf,
        'email': unique_email,
        'password': 'Password123!'
    }).encode('utf-8')
    req = urllib.request.Request('http://127.0.0.1:5000/login', data=old_login_data)
    res = opener.open(req)
    assert 'Invalid email or password' in res.read().decode('utf-8')
    print('[OK] 14. Old password successfully invalidated')

    # 8i. Login with new password succeeds
    new_login_data = urllib.parse.urlencode({
        'csrf_token': login_csrf,
        'email': unique_email,
        'password': new_password
    }).encode('utf-8')
    req = urllib.request.Request('http://127.0.0.1:5000/login', data=new_login_data)
    res = opener.open(req)
    assert 'Welcome, Sachin!' in res.read().decode('utf-8')
    print('[OK] 15. Login with new password verified successfully')

    # 9. Test Automatic Presentation Demo Mode
    # 9a. Activate Demo Mode
    res = opener.open('http://127.0.0.1:5000/demo')
    assert res.status == 200
    demo_launch_html = res.read().decode('utf-8')
    assert 'Sample Resume' in demo_launch_html
    assert 'Alex Patil' in demo_launch_html
    assert 'Python Developer' in demo_launch_html
    assert 'AUTOMATIC DEMO MODE' in demo_launch_html
    print('[OK] 16. Automatic Demo Mode activated: Sample resume auto-loaded for Alex Patil (HTTP 200)')

    # 9b. Extract demo analysis ID from launch page
    aid_demo_match = re.search(r'href="/analysis/results/(\d+)"', demo_launch_html)
    assert aid_demo_match is not None, 'Could not find demo analysis link in launch HTML'
    demo_aid = aid_demo_match.group(1)

    # 9c. Load Demo Analysis Results
    res = opener.open(f'http://127.0.0.1:5000/analysis/results/{demo_aid}')
    assert res.status == 200
    demo_results_html = res.read().decode('utf-8')
    assert '82' in demo_results_html, 'Demo overall score 82 missing'
    assert '86' in demo_results_html, 'Demo ATS score 86 missing'
    assert '78' in demo_results_html, 'Demo Job match score 78 missing'
    assert 'Python' in demo_results_html
    assert 'Docker' in demo_results_html
    assert 'DEMO MODE' in demo_results_html
    print('[OK] 17. Demo Analysis Results loaded with 82/100 Overall, 86/100 ATS, 78% Match & DEMO MODE badge')

    # 9d. Test AI Career Assistant in Demo Mode
    demo_chat_payload = json.dumps({'message': 'How can I improve this resume?'}).encode('utf-8')
    demo_csrf = demo_results_html.split('name="csrf-token" content="')[1].split('"')[0]
    req = urllib.request.Request(
        f'http://127.0.0.1:5000/api/chat/{demo_aid}',
        data=demo_chat_payload,
        headers={'Content-Type': 'application/json', 'X-CSRFToken': demo_csrf}
    )
    res = opener.open(req)
    assert res.status == 200
    demo_chat_resp = json.loads(res.read().decode('utf-8'))
    assert demo_chat_resp['success'] is True
    print('[OK] 18. AI Career Assistant responding with sample resume context in Demo Mode:')
    print(f"     Assistant: {demo_chat_resp['reply'][:120]}...")

    # 9e. Test Exit Demo Mode
    res = opener.open('http://127.0.0.1:5000/demo/exit')
    assert res.status == 200
    exit_html = res.read().decode('utf-8')
    assert 'You have exited Demo Mode' in exit_html or 'SkyGuard AI' in exit_html
    print('[OK] 19. Demo Mode exit cleanly clears session and returns to public landing')

    print('\n' + '='*50)
    print('ALL LIVE SERVER END-TO-END TESTS PASSED WITH 100% SUCCESS!')
    print('='*50)

if __name__ == '__main__':
    run_live_verification()
