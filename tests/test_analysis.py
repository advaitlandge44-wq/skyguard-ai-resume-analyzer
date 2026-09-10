from app.services.fallback_analyzer import generate_fallback_analysis, extract_skills_from_text, analyze_ats_compliance
from app.services.openai_service import validate_and_sanitize_analysis_json, improve_resume_bullet, ask_resume_assistant


def test_fallback_analyzer_schema():
    """Verify that fallback analyzer outputs all required JSON schema fields."""
    sample_text = """
    Jane Candidate
    Email: jane@candidate.org | Phone: (555) 987-6543 | LinkedIn: linkedin.com/in/janecandidate
    
    Summary:
    Results-driven Software Engineer with experience in Python, Flask, SQL, and Docker.
    
    Work Experience:
    Software Engineer | Tech Corp (2021 - 2024)
    - Developed microservices with Python, Flask, and PostgreSQL.
    - Automated deployment pipelines using Docker and Git.
    - Improved database throughput by 40% through index optimization.
    
    Education:
    B.S. in Computer Engineering (2017 - 2021)
    """

    result = generate_fallback_analysis(sample_text, "Python Developer", "Need Python, Flask, Redis, AWS")

    assert isinstance(result, dict)
    
    # Check numeric scores
    assert 0 <= result["overall_score"] <= 100
    assert 0 <= result["ats_score"] <= 100
    assert 0 <= result["job_match_score"] <= 100

    # Check lists
    assert isinstance(result["existing_skills"], list)
    assert "Python" in result["existing_skills"] or "PYTHON" in result["existing_skills"]
    assert isinstance(result["missing_skills"], list)
    assert isinstance(result["strengths"], list)
    assert isinstance(result["weaknesses"], list)
    assert isinstance(result["learning_roadmap"], list)
    assert len(result["learning_roadmap"]) > 0
    assert "skill" in result["learning_roadmap"][0]
    assert "why" in result["learning_roadmap"][0]
    assert "project_idea" in result["learning_roadmap"][0]
    assert isinstance(result["recommended_job_roles"], list)


def test_json_sanitizer_and_clamping(app):
    """Test score boundary clamping and schema normalization."""
    with app.app_context():
        corrupt_data = {
            "overall_score": 150,  # over max
            "ats_score": -20,     # under min
            "job_match_score": "not_a_number",
            "summary": "Sample summary",
            "existing_skills": "invalid_string_not_list",
            "missing_skills": ["Docker", "AWS"],
            "learning_roadmap": []
        }

        sanitized = validate_and_sanitize_analysis_json(corrupt_data, "Python Developer", "Sample resume")

        assert sanitized["overall_score"] == 100
        assert sanitized["ats_score"] == 0
        assert sanitized["job_match_score"] == 70
        assert isinstance(sanitized["existing_skills"], list)
        assert len(sanitized["learning_roadmap"]) > 0


def test_bullet_improver(app):
    """Test bullet point improvement without fabricating unearned facts."""
    with app.app_context():
        original = "Made a website using Python."
        result = improve_resume_bullet(original, "Python Developer")
        
        assert result["success"] is True
        assert result["original"] == original
        assert len(result["improved"]) > len(original)
        assert "why_better" in result


def test_career_chat_assistant(app):
    """Test contextual chat assistant answers without crashing."""
    with app.app_context():
        reply = ask_resume_assistant(
            chat_history=[],
            user_message="Why is my score 75?",
            analysis_summary="Python Developer with strong Flask skills but missing Docker.",
            target_role="Python Developer",
            analysis_data={
                "overall_score": 75,
                "ats_score": 80,
                "job_match_score": 70,
                "missing_skills": ["Docker", "Kubernetes"],
                "matched_skills": ["Python", "Flask", "SQL"],
                "weak_skills": ["PostgreSQL"]
            }
        )
        assert isinstance(reply, str)
        assert len(reply) > 10
        assert "75" in reply or "Python Developer" in reply


def test_ask_resume_assistant_openai_success(app, monkeypatch):
    """Test ask_resume_assistant returns real AI response when OpenAI call succeeds."""
    from unittest.mock import MagicMock
    import app.services.openai_service as oas

    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Master Docker and CI/CD pipelines to elevate your backend engineering profile."
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response

    monkeypatch.setattr(oas, "get_openai_client", lambda: mock_client)

    with app.app_context():
        reply = ask_resume_assistant(
            chat_history=[],
            user_message="What should I focus on?",
            analysis_summary="Python Developer missing Docker.",
            target_role="Python Developer"
        )
        assert reply == "Master Docker and CI/CD pipelines to elevate your backend engineering profile."


def test_ask_resume_assistant_openai_ratelimit_429(app, monkeypatch):
    """Test ask_resume_assistant automatically falls back to offline advisor on 429 / RateLimitError."""
    from unittest.mock import MagicMock
    from openai import RateLimitError
    import app.services.openai_service as oas

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = RateLimitError(
        message="You exceeded your current quota, please check your plan and billing details.",
        response=MagicMock(status_code=429),
        body=None
    )

    monkeypatch.setattr(oas, "get_openai_client", lambda: mock_client)

    with app.app_context():
        reply = ask_resume_assistant(
            chat_history=[],
            user_message="What skills should I learn first?",
            analysis_summary="Python Developer missing Docker, Kubernetes.",
            target_role="Python Developer",
            analysis_data={
                "missing_skills": ["Docker", "Kubernetes"],
                "matched_skills": ["Python", "Flask"]
            }
        )
        assert isinstance(reply, str)
        assert "trouble connecting" not in reply
        assert "Docker" in reply
        assert "Python Developer" in reply


def test_ask_resume_assistant_openai_auth_401(app, monkeypatch):
    """Test ask_resume_assistant automatically falls back to offline advisor on 401 / AuthenticationError."""
    from unittest.mock import MagicMock
    from openai import AuthenticationError
    import app.services.openai_service as oas

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = AuthenticationError(
        message="Incorrect API key provided.",
        response=MagicMock(status_code=401),
        body=None
    )

    monkeypatch.setattr(oas, "get_openai_client", lambda: mock_client)

    with app.app_context():
        reply = ask_resume_assistant(
            chat_history=[],
            user_message="How can I improve my resume?",
            analysis_summary="Python Developer missing Docker.",
            target_role="Python Developer",
            analysis_data={
                "overall_score": 72,
                "missing_skills": ["Docker", "AWS"],
                "matched_skills": ["Python", "Django"]
            }
        )
        assert isinstance(reply, str)
        assert "trouble connecting" not in reply
        assert "STAR" in reply or "Docker" in reply or "72" in reply


def test_ask_resume_assistant_openai_timeout_and_connection(app, monkeypatch):
    """Test ask_resume_assistant automatically falls back on timeout or connection error."""
    from unittest.mock import MagicMock
    from openai import APITimeoutError, APIConnectionError
    import app.services.openai_service as oas

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = APITimeoutError(request=MagicMock())

    monkeypatch.setattr(oas, "get_openai_client", lambda: mock_client)

    with app.app_context():
        reply = ask_resume_assistant(
            chat_history=[],
            user_message="What project should I build?",
            analysis_summary="Full Stack Developer missing React.",
            target_role="Full Stack Developer",
            analysis_data={
                "missing_skills": ["React", "TypeScript"],
                "matched_skills": ["Node.js", "Express", "MongoDB"]
            }
        )
        assert isinstance(reply, str)
        assert "trouble connecting" not in reply
        assert "Project" in reply or "Capstone" in reply or "React" in reply


def test_ask_resume_assistant_no_api_key(app, monkeypatch):
    """Test ask_resume_assistant works when no API key is provided (client is None)."""
    import app.services.openai_service as oas

    monkeypatch.setattr(oas, "get_openai_client", lambda: None)

    with app.app_context():
        reply = ask_resume_assistant(
            chat_history=[],
            user_message="Am I ready for this job?",
            analysis_summary="DevOps Engineer with 65% match.",
            target_role="DevOps Engineer",
            analysis_data={
                "job_match_score": 65,
                "matched_skills": ["Linux", "Git"],
                "missing_skills": ["Kubernetes", "Terraform"]
            }
        )
        assert isinstance(reply, str)
        assert len(reply) > 20
        assert "65%" in reply
        assert "DevOps Engineer" in reply


def test_offline_career_chat_contextual_questions(app):
    """Test all contextual offline chat question types return role-specific guidance."""
    analysis_data = {
        "overall_score": 82,
        "ats_score": 88,
        "job_match_score": 80,
        "matched_skills": ["Python", "Flask", "SQL"],
        "weak_skills": ["PostgreSQL"],
        "missing_skills": ["Docker", "AWS", "Redis"]
    }

    with app.app_context():
        # 1. Skills priority
        r1 = ask_resume_assistant([], "What skills should I learn first?", "", "Python Developer", analysis_data)
        assert "Docker" in r1
        assert "Python Developer" in r1

        # 2. Resume improvement
        r2 = ask_resume_assistant([], "How can I improve my resume?", "", "Python Developer", analysis_data)
        assert "82/100" in r2 or "STAR" in r2 or "Docker" in r2

        # 3. Job readiness
        r3 = ask_resume_assistant([], "Am I ready for this job?", "", "Python Developer", analysis_data)
        assert "80%" in r3
        assert "alignment" in r3.lower() or "competitive" in r3.lower() or "ready" in r3.lower()

        # 4. Capstone project
        r4 = ask_resume_assistant([], "What project should I build?", "", "Python Developer", analysis_data)
        assert "Project" in r4 or "Tech Stack" in r4 or "GitHub" in r4

        # 5. ATS formatting
        r5 = ask_resume_assistant([], "How is my ATS formatting?", "", "Python Developer", analysis_data)
        assert "88/100" in r5 or "ATS" in r5

        # 6. Specific skill inquiry ("why learn Docker")
        r6 = ask_resume_assistant([], "Why do I need Docker?", "", "Python Developer", analysis_data)
        assert "Docker" in r6

        # 7. Timeline / Duration
        r7 = ask_resume_assistant([], "How long will it take to finish the roadmap?", "", "Python Developer", analysis_data)
        assert "Phase" in r7 or "hours" in r7.lower()

        # 8. Interview prep
        r8 = ask_resume_assistant([], "How can I prepare for interviews?", "", "Python Developer", analysis_data)
        assert "Interview" in r8 or "STAR" in r8


def test_api_chat_endpoint_quota_fallback_integration(authenticated_client, auth_user, app, monkeypatch):
    """End-to-end test of POST /api/chat/<id> when OpenAI quota fails (429) -> HTTP 200 contextual reply."""
    import json
    from unittest.mock import MagicMock
    from openai import RateLimitError
    import app.services.openai_service as oas
    from app.models import db, User, Resume, Analysis, ChatMessage

    # Mock OpenAI client raising 429 RateLimitError
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = RateLimitError(
        message="Insufficient quota",
        response=MagicMock(status_code=429),
        body=None
    )
    monkeypatch.setattr(oas, "get_openai_client", lambda: mock_client)

    with app.app_context():
        user = db.session.get(User, auth_user)
        resume = Resume(
            user_id=user.id,
            filename="Chat_Integration_Resume.pdf",
            stored_filename="chat_integration_resume.pdf",
            target_role="Python Developer",
            extracted_text="Python developer with Flask and SQL."
        )
        db.session.add(resume)
        db.session.commit()

        analysis_dict = {
            "overall_score": 78,
            "ats_score": 82,
            "job_match_score": 75,
            "summary": "Solid Python developer with Flask experience, missing Docker.",
            "existing_skills": ["Python", "Flask", "SQL"],
            "matched_skills": ["Python", "Flask"],
            "missing_skills": ["Docker", "Kubernetes", "Redis"],
            "weak_skills": ["SQL"],
            "strengths": ["Clean modular code"],
            "weaknesses": ["Lacks containerization experience"],
            "learning_roadmap": [{"skill": "Docker", "why": "Containers", "project_idea": "Dockerize Flask app"}]
        }
        analysis = Analysis(
            user_id=user.id,
            resume_id=resume.id,
            target_role="Python Developer",
            overall_score=78,
            ats_score=82,
            job_match_score=75,
            summary=analysis_dict["summary"],
            analysis_json=json.dumps(analysis_dict)
        )
        db.session.add(analysis)
        db.session.commit()
        analysis_id = analysis.id

    # Make chat request via API
    resp = authenticated_client.post(
        f"/api/chat/{analysis_id}",
        json={"message": "What skills should I learn first?"}
    )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "reply" in data
    assert "created_at" in data
    assert "trouble connecting" not in data["reply"]
    assert "Docker" in data["reply"]
    assert "Python Developer" in data["reply"]

    # Verify message was recorded in the database
    with app.app_context():
        messages = ChatMessage.query.filter_by(analysis_id=analysis_id).all()
        assert len(messages) == 2
        assert messages[0].role == "user"
        assert messages[0].content == "What skills should I learn first?"
        assert messages[1].role == "assistant"
        assert "Docker" in messages[1].content

