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
    assert 'Official Career Diagnostic Report' in export_html
    print('[OK] 8. Printable / PDF Export View verified (HTTP 200)')

    print('\n' + '='*50)
    print('ALL LIVE SERVER END-TO-END TESTS PASSED WITH 100% SUCCESS!')
    print('='*50)

if __name__ == '__main__':
    run_live_verification()
