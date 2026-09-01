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
            target_role="Python Developer"
        )
        assert isinstance(reply, str)
        assert len(reply) > 10
