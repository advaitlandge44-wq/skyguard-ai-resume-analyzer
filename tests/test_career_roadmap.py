import pytest
import json
import urllib.parse
from app.models import db, User, Resume, Analysis, ChatMessage
from app.services.career_roadmap_engine import (
    TARGET_JOB_ROLES,
    ROLE_CATEGORIES,
    ROLE_MATRICES,
    CURATED_LEARNING_LIBRARY,
    SKILL_ALIASES,
    normalize_skill_name,
    get_role_configuration,
    generate_safe_youtube_search_url,
    resolve_skill_learning_resources,
    analyze_skills_against_role
)
from app.services.fallback_analyzer import generate_fallback_analysis
from app.services.openai_service import ask_resume_assistant
from app.services.demo_service import (
    get_or_create_demo_user,
    get_or_create_demo_analysis,
    get_demo_chat_reply
)


def test_25_target_job_roles_completeness():
    """Verifies that exactly 25 predefined target job roles exist."""
    assert len(TARGET_JOB_ROLES) == 25
    expected_roles = [
        "Software Developer", "Full Stack Developer", "Frontend Developer",
        "Backend Developer", "Python Developer", "Java Developer",
        "JavaScript Developer", "React Developer", "Mobile App Developer",
        "Data Analyst", "Data Scientist", "Machine Learning Engineer",
        "AI Engineer", "Generative AI Engineer", "NLP Engineer",
        "DevOps Engineer", "Cloud Engineer", "Cybersecurity Analyst",
        "QA / Software Testing Engineer", "Database Developer / DBA",
        "UI/UX Designer", "Business Analyst", "System Administrator",
        "MLOps Engineer", "AI/ML Research Engineer"
    ]
    for role in expected_roles:
        assert role in TARGET_JOB_ROLES, f"Expected role {role} not found in TARGET_JOB_ROLES"


def test_25_role_matrices_defined_and_valid():
    """Verifies that every single one of the 25 roles has a rich skill matrix."""
    for role in TARGET_JOB_ROLES:
        config = get_role_configuration(role)
        assert config is not None
        assert "core_skills" in config and len(config["core_skills"]) >= 5
        assert "important_skills" in config and len(config["important_skills"]) >= 3
        assert "tools" in config and len(config["tools"]) >= 3
        assert "description" in config and len(config["description"]) > 10


def test_curated_ai_learning_library_urls_exact():
    """Verifies all 25 curated library URLs are present and unmodified."""
    assert len(CURATED_LEARNING_LIBRARY) == 25
    
    # Check Python
    assert "https://youtube.com/playlist?list=PLKnIA16_Rmvb1RYR-iTA_hzckhdONtSW4" in CURATED_LEARNING_LIBRARY["python"]["url"]
    # Check Data Analyst Bootcamp
    assert "https://youtu.be/PSNXoAs2FtQ" in CURATED_LEARNING_LIBRARY["data analyst bootcamp"]["url"]
    # Check Machine Learning
    assert "https://youtube.com/playlist?list=PLKnIA16_Rmvbr7zKYQuBfsVkjoLcJgxHH" in CURATED_LEARNING_LIBRARY["machine learning"]["url"]
    # Check Generative AI
    assert "https://youtube.com/playlist?list=PLKnIA16_RmvaTbihpo4MtzVm4XOQa0ER0" in CURATED_LEARNING_LIBRARY["generative ai"]["url"]
    # Check FastAPI
    assert "https://youtube.com/playlist?list=PLKnIA16_RmvZ41tjbKB2ZnwchfniNsMuQ" in CURATED_LEARNING_LIBRARY["fastapi"]["url"]
    # Check AWS
    assert "https://youtu.be/GkKNxyLp_V0" in CURATED_LEARNING_LIBRARY["aws zero to hero"]["url"]
    # Check RAG
    assert "https://youtu.be/X0btK9X0Xnk" in CURATED_LEARNING_LIBRARY["rag"]["url"]
    # Check MCP
    assert "https://youtube.com/playlist?list=PLKnIA16_Rmva_oZ9F4ayUu9qcWgF7Fyc0" in CURATED_LEARNING_LIBRARY["mcp"]["url"]


def test_safe_url_generation_no_fake_ids():
    """Verifies fallback YouTube URLs are safe query strings and never hallucinated IDs."""
    safe_url = generate_safe_youtube_search_url("Kubernetes", "English")
    assert safe_url.startswith("https://www.youtube.com/results?search_query=")
    assert "Kubernetes" in safe_url
    assert "English" in safe_url

    hinglish_url = generate_safe_youtube_search_url("Docker", "Hinglish")
    assert hinglish_url.startswith("https://www.youtube.com/results?search_query=")
    assert "Docker" in hinglish_url
    assert "Hinglish" in hinglish_url


def test_skill_alias_normalization():
    """Verifies common abbreviations and aliases normalize properly."""
    assert normalize_skill_name("js") == "JavaScript"
    assert normalize_skill_name("postgres") == "PostgreSQL"
    assert normalize_skill_name("k8s") == "Kubernetes"
    assert normalize_skill_name("restful api") == "REST API"
    assert normalize_skill_name("ts") == "TypeScript"
    assert normalize_skill_name("py") == "Python"
    assert normalize_skill_name("genai") == "Generative AI"
    assert normalize_skill_name("dl") == "Deep Learning"


def test_skill_analysis_for_ten_key_roles():
    """Verifies skill gap analysis for the 10 specific roles requested."""
    key_roles = [
        "Full Stack Developer",
        "Python Developer",
        "Data Analyst",
        "Machine Learning Engineer",
        "Generative AI Engineer",
        "DevOps Engineer",
        "Cloud Engineer",
        "Cybersecurity Analyst",
        "UI/UX Designer",
        "QA / Software Testing Engineer"
    ]

    sample_resume = """
    Software engineer with experience in Python, SQL, Git, and HTML/CSS.
    Built small web applications with Flask and basic databases.
    """

    for role in key_roles:
        res = analyze_skills_against_role(sample_resume, role)
        assert res["target_role"] == role or role in res["target_role"]
        assert len(res["missing_skills"]) >= 1
        assert len(res["learning_resources"]) >= 1
        assert len(res["learning_roadmap"]) == 6

        # Check resource card schema
        for rc in res["learning_resources"]:
            assert "skill" in rc
            assert "estimated_time" in rc
            assert "difficulty" in rc
            assert "practice_task" in rc and len(rc["practice_task"]) > 5
            assert "project_idea" in rc and len(rc["project_idea"]) > 5
            assert "english_resource" in rc and rc["english_resource"]["url"].startswith("http")
            assert "hinglish_resource" in rc and rc["hinglish_resource"]["url"].startswith("http")


def test_job_description_priority_weighting():
    """Verifies that Job Description requirements take high priority in skill matching."""
    resume_text = "Experienced in Python, Flask, and SQL."
    jd_text = "Must have strong experience in Docker, AWS ECS, and Redis."

    res = analyze_skills_against_role(resume_text, "Full Stack Developer", job_description=jd_text)
    assert "Docker" in res["jd_required_skills"] or "AWS" in res["jd_required_skills"] or "Redis" in res["jd_required_skills"]
    # Docker or Redis should appear in missing skills and learning resources
    gap_skills = [r["skill"] for r in res["learning_resources"]]
    assert any(s in gap_skills for s in ["Docker", "Redis", "AWS", "FastAPI", "React"])


def test_fallback_analyzer_full_schema():
    """Verifies that fallback analyzer returns full 3-way skill matrix and learning resources."""
    resume_text = """
    Software Engineer with 2 years of experience.
    Proficient in Python, Django, PostgreSQL, Git.
    Created machine learning regression pipelines using Scikit-Learn.
    """

    res = generate_fallback_analysis(resume_text, "Generative AI Engineer")
    assert res["overall_score"] > 0
    assert 0 < res["ats_score"] <= 100
    assert "Python" in res["matched_skills"] or "Python" in res["existing_skills"]
    assert "Generative AI" in res["missing_skills"] or "LLMs" in res["missing_skills"] or "RAG" in res["missing_skills"]
    assert len(res["learning_resources"]) >= 3
    assert len(res["learning_roadmap"]) == 6


def test_results_page_renders_learning_plan(authenticated_client, auth_user, app):
    """Verifies that the results page HTML renders the Personalized Learning Plan, English/Hinglish links, and 3-way badges."""
    with app.app_context():
        user = db.session.get(User, auth_user)
        resume = Resume(
            user_id=user.id,
            filename="Test_Resume.pdf",
            stored_filename="test_resume_123.pdf",
            target_role="Generative AI Engineer",
            extracted_text="Python Developer experienced in Flask and SQL."
        )
        db.session.add(resume)
        db.session.commit()

        analysis_dict = generate_fallback_analysis(resume.extracted_text, "Generative AI Engineer")
        analysis = Analysis(
            user_id=user.id,
            resume_id=resume.id,
            target_role="Generative AI Engineer",
            overall_score=analysis_dict["overall_score"],
            ats_score=analysis_dict["ats_score"],
            job_match_score=analysis_dict["job_match_score"],
            summary=analysis_dict["summary"],
            analysis_json=json.dumps(analysis_dict)
        )
        db.session.add(analysis)
        db.session.commit()
        analysis_id = analysis.id

    response = authenticated_client.get(f'/analysis/results/{analysis_id}')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Your Personalized Learning Plan" in html
    assert "Learn in English" in html
    assert "Learn in Hinglish" in html
    assert "Practice Task" in html
    assert "Portfolio Project" in html
    assert "Role Skill Matrix Diagnostic" in html
    assert "Matched Skills" in html
    assert "Missing Skills" in html


def test_dashboard_renders_learning_hub(authenticated_client, auth_user, app):
    """Verifies that the dashboard HTML renders the Learning & Career Progression Hub."""
    with app.app_context():
        user = db.session.get(User, auth_user)
        resume = Resume(
            user_id=user.id,
            filename="Test_Resume.pdf",
            stored_filename="test_resume_dash.pdf",
            target_role="Cloud Engineer",
            extracted_text="Linux administrator with Bash and Git."
        )
        db.session.add(resume)
        db.session.commit()

        analysis_dict = generate_fallback_analysis(resume.extracted_text, "Cloud Engineer")
        analysis = Analysis(
            user_id=user.id,
            resume_id=resume.id,
            target_role="Cloud Engineer",
            overall_score=analysis_dict["overall_score"],
            ats_score=analysis_dict["ats_score"],
            job_match_score=analysis_dict["job_match_score"],
            summary=analysis_dict["summary"],
            analysis_json=json.dumps(analysis_dict)
        )
        db.session.add(analysis)
        db.session.commit()

    response = authenticated_client.get('/dashboard')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Learning & Career Progression Hub" in html
    assert "Target Role: Cloud Engineer" in html
    assert "Matched Skills" in html
    assert "Missing Skills" in html


def test_roadmap_page_renders_phased_plan(authenticated_client, auth_user, app):
    """Verifies that /roadmap renders the 6-phase milestone plan with practice challenges."""
    with app.app_context():
        user = db.session.get(User, auth_user)
        resume = Resume(
            user_id=user.id,
            filename="Test_Roadmap_Resume.pdf",
            stored_filename="test_roadmap_resume.pdf",
            target_role="DevOps Engineer",
            extracted_text="Linux sysadmin with Docker and Git."
        )
        db.session.add(resume)
        db.session.commit()

        analysis_dict = generate_fallback_analysis(resume.extracted_text, "DevOps Engineer")
        analysis = Analysis(
            user_id=user.id,
            resume_id=resume.id,
            target_role="DevOps Engineer",
            overall_score=analysis_dict["overall_score"],
            ats_score=analysis_dict["ats_score"],
            job_match_score=analysis_dict["job_match_score"],
            summary=analysis_dict["summary"],
            analysis_json=json.dumps(analysis_dict)
        )
        db.session.add(analysis)
        db.session.commit()

    response = authenticated_client.get('/roadmap')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Your Career Roadmap &amp; Learning Plan" in html or "Your Career Roadmap" in html
    assert "Step-by-Step Phased Roadmap" in html


def test_ai_career_assistant_context_and_api(authenticated_client, auth_user, app):
    """Verifies the AI assistant responds knowledgeably to learning roadmap queries."""
    with app.app_context():
        user = db.session.get(User, auth_user)
        resume = Resume(
            user_id=user.id,
            filename="Assistant_Test.pdf",
            stored_filename="assistant_test_123.pdf",
            target_role="Python Developer",
            extracted_text="Python Developer experienced in Flask."
        )
        db.session.add(resume)
        db.session.commit()

        analysis_dict = generate_fallback_analysis(resume.extracted_text, "Python Developer")
        analysis = Analysis(
            user_id=user.id,
            resume_id=resume.id,
            target_role="Python Developer",
            overall_score=analysis_dict["overall_score"],
            ats_score=analysis_dict["ats_score"],
            job_match_score=analysis_dict["job_match_score"],
            summary=analysis_dict["summary"],
            analysis_json=json.dumps(analysis_dict)
        )
        db.session.add(analysis)
        db.session.commit()
        analysis_id = analysis.id

    # Test "What should I learn first?"
    response = authenticated_client.post(
        f'/api/chat/{analysis_id}',
        json={'message': 'What should I learn first?'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert len(data['reply']) > 15

    # Test "Give me a project for my missing skills"
    response2 = authenticated_client.post(
        f'/api/chat/{analysis_id}',
        json={'message': 'Give me a project for my missing skills'}
    )
    assert response2.status_code == 200
    data2 = response2.get_json()
    assert data2['success'] is True
    assert "project" in data2['reply'].lower() or "practice" in data2['reply'].lower() or "task" in data2['reply'].lower()


def test_demo_mode_career_roadmap_integration(client, app):
    """Verifies Demo Mode auto-loads sample resume with learning resources, roadmap, and AI assistant."""
    response = client.get('/demo')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "AUTOMATIC DEMO MODE" in html
    assert "Alex Patil" in html

    # Access results page in demo mode
    with app.app_context():
        demo_user = get_or_create_demo_user()
        demo_analysis = get_or_create_demo_analysis(demo_user)
        demo_analysis_id = demo_analysis.id

    results_resp = client.get(f'/analysis/results/{demo_analysis_id}')
    assert results_resp.status_code == 200
    results_html = results_resp.get_data(as_text=True)
    assert "Python Developer" in results_html
    assert "Your Personalized Learning Plan" in results_html
    assert "Learn in English" in results_html
    assert "Learn in Hinglish" in results_html

    # Test demo chat answers
    chat_reply = get_demo_chat_reply("What should I learn first?")
    assert "Docker" in chat_reply
    assert "hours" in chat_reply

    chat_reply_project = get_demo_chat_reply("Give me a project idea")
    assert "Project" in chat_reply_project or "Docker" in chat_reply_project
