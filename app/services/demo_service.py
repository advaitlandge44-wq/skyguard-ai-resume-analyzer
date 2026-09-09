import json
import logging
from datetime import datetime, timezone
from app.models import db, User, Resume, Analysis, ChatMessage
from app.services.career_roadmap_engine import resolve_skill_learning_resources

logger = logging.getLogger(__name__)

DEMO_USER_EMAIL = "demo@skyguard.ai"
DEMO_USER_NAME = "Alex Patil (Demo)"
DEMO_TARGET_ROLE = "Python Developer"
DEMO_JOB_DESCRIPTION = "We are seeking a skilled Python Developer with solid experience in Python, Flask, SQL databases, RESTful APIs, Docker containerization, and AWS cloud deployment."

SAMPLE_RESUME_TEXT = """Alex Patil
Email: alex.patil.demo@skyguard.ai | Phone: +1 (555) 019-2834 | Location: San Francisco, CA
LinkedIn: linkedin.com/in/alex-patil-demo | GitHub: github.com/alex-patil-demo

PROFESSIONAL SUMMARY
Dedicated Python Developer with 3+ years of experience engineering scalable web applications and RESTful APIs using Python, Flask, and SQL databases. Proven track record in modular backend development, relational schema design, and agile Git workflows.

TECHNICAL SKILLS
• Programming Languages: Python, JavaScript, SQL, HTML5, CSS3
• Frameworks & Libraries: Flask, SQLAlchemy, Jinja2, PyTest, Werkzeug
• Databases & Storage: PostgreSQL, SQLite, MySQL
• Developer Tools: Git, GitHub, Linux/Bash, VS Code, Postman
• Core Competencies: RESTful API Design, Object-Oriented Programming, Database Normalization, Unit Testing

PROFESSIONAL EXPERIENCE
Backend Python Developer | NovaTech Solutions (2023 – Present)
• Engineered 12+ RESTful API endpoints in Flask, processing 50,000+ daily requests with 99.9% uptime.
• Implemented SQLAlchemy ORM models and optimized complex relational database queries, improving endpoint response times by 30%.
• Developed automated unit test suites using PyTest, achieving 88% code test coverage across core modules.
• Integrated JWT-based authentication and CSRF security middleware to safeguard API transactions.

Junior Software Developer | Apex Digital (2021 – 2023)
• Built internal web dashboard tools utilizing Python and Flask with PostgreSQL database backends.
• Collaborated on Git feature branch workflows, code reviews, and weekly agile sprint releases.
• Created data ingestion scripts in Python to sanitize and transform JSON and CSV datasets.

FEATURED PROJECTS
Resume Analytics Engine (Python, Flask, SQLite)
• Designed and launched a web-based resume scoring tool with real-time text parsing and skill keyword matching.
• Built modular Flask Blueprints and dynamic UI components with responsive CSS.

TaskFlow API Microservice (Python, PostgreSQL, Postman)
• Developed a high-performance CRUD task management API with role-based access control and OpenAPI documentation.

EDUCATION
Bachelor of Science in Computer Science | State University (2017 – 2021)
"""

DEMO_ANALYSIS_DATA = {
    "overall_score": 82,
    "ats_score": 86,
    "job_match_score": 78,
    "summary": "Alex Patil shows a strong mid-level Python foundation with solid Flask and SQL database experience. Adding Docker containerization, AWS cloud deployment, and CI/CD exposure will elevate this profile to top-tier Senior Python Developer roles.",
    "existing_skills": [
        "Python",
        "Flask",
        "SQL",
        "Git",
        "REST API",
        "SQLAlchemy",
        "Unit Testing",
        "PostgreSQL",
        "OOP"
    ],
    "matched_skills": [
        "Python",
        "Flask",
        "SQL",
        "Git",
        "REST API",
        "SQLAlchemy",
        "Unit Testing",
        "PostgreSQL",
        "OOP"
    ],
    "weak_skills": [
        "Redis",
        "CI/CD"
    ],
    "missing_skills": [
        "Docker",
        "AWS",
        "Kubernetes"
    ],
    "learning_resources": [
        resolve_skill_learning_resources("Docker", "Python Developer"),
        resolve_skill_learning_resources("AWS", "Python Developer"),
        resolve_skill_learning_resources("FastAPI", "Python Developer"),
        resolve_skill_learning_resources("CI/CD", "Python Developer"),
        resolve_skill_learning_resources("Kubernetes", "Python Developer")
    ],
    "strengths": [
        "Strong core Python fundamentals and proven Flask production experience (50K+ daily requests)",
        "Excellent database design and ORM query optimization skills with PostgreSQL & SQLite",
        "High test coverage mindset with automated PyTest test suites (88% coverage)",
        "Clean single-column ATS-friendly resume formatting with clear section hierarchy"
    ],
    "weaknesses": [
        "Missing containerization and orchestration tooling (Docker, Kubernetes)",
        "Limited hands-on cloud deployment exposure on AWS or GCP",
        "Could include more metric-driven STAR bullet achievements across earlier projects"
    ],
    "experience_feedback": [
        "Strong active verbs used in NovaTech Solutions role (Engineered, Implemented, Developed).",
        "Quantified metrics (50,000+ daily requests, 30% query speedup) create strong recruiter appeal.",
        "Consider expanding Apex Digital bullets to include specific team size and business outcome metrics."
    ],
    "project_feedback": [
        "Resume Analytics Engine and TaskFlow API directly demonstrate Python/Flask competency.",
        "Recommend adding a live demo link or GitHub repository link to each project section."
    ],
    "education_feedback": [
        "B.S. in Computer Science aligns well with technical recruiter requirements."
    ],
    "formatting_feedback": [
        "Layout is 100% ATS parser compliant with standard single-column text flow.",
        "Contact info, headings, and bullet points parse cleanly with zero hidden text errors."
    ],
    "keyword_suggestions": [
        {"keyword": "Docker", "category": "DevOps", "importance": "High"},
        {"keyword": "AWS (EC2/S3)", "category": "Cloud", "importance": "High"},
        {"keyword": "RESTful API", "category": "Architecture", "importance": "High"},
        {"keyword": "CI/CD (GitHub Actions)", "category": "Automation", "importance": "Medium"},
        {"keyword": "Redis Caching", "category": "Performance", "importance": "Medium"}
    ],
    "improvement_suggestions": [
        "Containerize the TaskFlow API project using Docker and Docker Compose.",
        "Deploy a sample Flask application to AWS (EC2 or Lambda) and add it to your Technical Skills.",
        "Add continuous integration pipelines with GitHub Actions to your public repositories."
    ],
    "learning_roadmap": [
        {
            "phase": "Phase 1",
            "order": "Phase 1 — Fundamentals & Architecture",
            "skill": "Python Advanced & Asyncio",
            "why": "Master generators, decorators, asyncio, and typing for large-scale enterprise Python systems.",
            "time_estimate": "6-12 hours",
            "difficulty": "Intermediate",
            "practice_task": "Write an asynchronous script using aiohttp to fetch and parse data concurrently with error handling.",
            "project_idea": "Build an asynchronous rate-limited webhook dispatcher in Python 3.12.",
            "english_url": "https://youtube.com/playlist?list=PLKnIA16_Rmvb1RYR-iTA_hzckhdONtSW4&si=iFUVwQ-i9arYMjEz",
            "hinglish_url": "https://www.youtube.com/results?search_query=Python+advanced+tutorial+Hinglish"
        },
        {
            "phase": "Phase 2",
            "order": "Phase 2 — Core Technologies & APIs",
            "skill": "FastAPI & REST Architecture",
            "why": "Essential for designing high-throughput microservices with OpenAPI and JWT security.",
            "time_estimate": "6-12 hours",
            "difficulty": "Intermediate",
            "practice_task": "Create a secure FastAPI endpoint with Pydantic request validation and dependency injection.",
            "project_idea": "Create a fully documented RESTful inventory API with FastAPI and PostgreSQL.",
            "english_url": "https://youtube.com/playlist?list=PLKnIA16_RmvZ41tjbKB2ZnwchfniNsMuQ&si=TYjhduFy1avM6v05",
            "hinglish_url": "https://www.youtube.com/results?search_query=FastAPI+tutorial+Hinglish"
        },
        {
            "phase": "Phase 3",
            "order": "Phase 3 — Advanced Tooling & Scale",
            "skill": "Docker & Compose",
            "why": "Industry standard for packaging, testing, and shipping Python backend services.",
            "time_estimate": "4-8 hours",
            "difficulty": "Intermediate",
            "practice_task": "Write a multi-stage Dockerfile for a Python web application reducing image size to under 150MB.",
            "project_idea": "Containerize a Flask + PostgreSQL + Redis application using multi-stage Docker builds.",
            "english_url": "https://www.youtube.com/results?search_query=Docker+full+tutorial+English",
            "hinglish_url": "https://www.youtube.com/results?search_query=Docker+tutorial+Hinglish"
        },
        {
            "phase": "Phase 4",
            "order": "Phase 4 — Capstone Project & Portfolio",
            "skill": "Enterprise Backend Capstone",
            "why": "Integrates authentication, relational models, automated testing, and background workers.",
            "time_estimate": "10-18 hours",
            "difficulty": "Advanced",
            "practice_task": "Write comprehensive unit test suites with PyTest achieving 88%+ code coverage with mock fixtures.",
            "project_idea": "Deploy a containerized API to AWS ECS with RDS PostgreSQL and automated GitHub Actions CI/CD.",
            "english_url": "https://www.youtube.com/results?search_query=Python+Backend+Enterprise+Project+English",
            "hinglish_url": "https://www.youtube.com/results?search_query=Python+Backend+Project+Hinglish"
        },
        {
            "phase": "Phase 5",
            "order": "Phase 5 — Cloud Infrastructure & CI/CD",
            "skill": "AWS Cloud Infrastructure",
            "why": "High-demand skill for deploying, scaling, and monitoring production Python applications.",
            "time_estimate": "10-20 hours",
            "difficulty": "Intermediate to Advanced",
            "practice_task": "Deploy a containerized application to AWS ECS connected to RDS PostgreSQL with IAM role security.",
            "project_idea": "Deploy an automated CI/CD pipeline on AWS using ECS, ECR, and GitHub Actions.",
            "english_url": "https://youtu.be/GkKNxyLp_V0?si=dLbrKOy-q7WaCb9A",
            "hinglish_url": "https://www.youtube.com/results?search_query=AWS+Zero+to+Hero+Hinglish"
        },
        {
            "phase": "Phase 6",
            "order": "Phase 6 — Interview Mastery & System Design",
            "skill": "Interview Preparation & System Design",
            "why": "Prepare for senior-level technical interviews, system design tradeoffs, and live coding.",
            "time_estimate": "12-25+ hours",
            "difficulty": "Advanced",
            "practice_task": "Draft an architectural diagram and API contract for a high-volume URL Shortener with Redis caching.",
            "project_idea": "Design a high-throughput URL shortener with Redis caching and PostgreSQL persistence.",
            "english_url": "https://www.youtube.com/results?search_query=System+Design+Interview+Masterclass+English",
            "hinglish_url": "https://www.youtube.com/results?search_query=System+Design+Interview+Hinglish"
        }
    ],
    "recommended_job_roles": [
        {
            "role": "Python Developer",
            "match_percentage": 88,
            "explanation": "High alignment with Python, Flask, and relational database skills."
        },
        {
            "role": "Backend Developer",
            "match_percentage": 85,
            "explanation": "Direct match for RESTful endpoint development and ORM integration."
        },
        {
            "role": "Full Stack Developer",
            "match_percentage": 78,
            "explanation": "Strong backend foundation; needs minor frontend enhancement."
        }
    ]
}


def get_or_create_demo_user() -> User:
    """Finds or creates the isolated Demo user in the database."""
    user = User.query.filter_by(email=DEMO_USER_EMAIL).first()
    if not user:
        user = User(name=DEMO_USER_NAME, email=DEMO_USER_EMAIL)
        user.set_password("SkyGuardDemo2026!Secure")
        db.session.add(user)
        db.session.commit()
    return user


def get_or_create_demo_analysis(user: User) -> Analysis:
    """Ensures sample resume and analysis exist for demo presentation."""
    # Find existing analysis
    analysis = Analysis.query.filter_by(user_id=user.id, target_role=DEMO_TARGET_ROLE).first()
    if analysis:
        # Update with newest enriched data schema
        analysis.analysis_json = json.dumps(DEMO_ANALYSIS_DATA)
        db.session.commit()
        return analysis

    # Create Resume record
    resume = Resume.query.filter_by(user_id=user.id).first()
    if not resume:
        resume = Resume(
            user_id=user.id,
            filename="Alex_Patil_Python_Developer.pdf",
            stored_filename=f"demo_alex_patil_{int(datetime.now(timezone.utc).timestamp())}.pdf",
            target_role=DEMO_TARGET_ROLE,
            file_size=1048576,
            file_type="pdf",
            extracted_text=SAMPLE_RESUME_TEXT
        )
        db.session.add(resume)
        db.session.commit()

    # Create Analysis record
    analysis = Analysis(
        user_id=user.id,
        resume_id=resume.id,
        target_role=DEMO_TARGET_ROLE,
        job_description=DEMO_JOB_DESCRIPTION,
        overall_score=DEMO_ANALYSIS_DATA["overall_score"],
        ats_score=DEMO_ANALYSIS_DATA["ats_score"],
        job_match_score=DEMO_ANALYSIS_DATA["job_match_score"],
        summary=DEMO_ANALYSIS_DATA["summary"],
        analysis_json=json.dumps(DEMO_ANALYSIS_DATA)
    )
    db.session.add(analysis)
    db.session.commit()
    return analysis


def get_demo_chat_reply(user_message: str) -> str:
    """Returns deterministic, context-aware answers for the sample resume during presentation."""
    msg = user_message.lower().strip()
    
    if "first" in msg or "start" in msg or "what should i learn" in msg:
        return (
            "For Alex Patil's profile, **start with Docker containerization first!**\n\n"
            "• **Why**: Modern Python backends are expected to run in standardized containers. Mastering Docker will take approximately **4–8 hours**.\n"
            "• **Practice Task**: Write a multi-stage Dockerfile to containerize the TaskFlow API.\n"
            "• **Next Step**: Once containerized, deploy it to AWS ECS to bridge the cloud infrastructure gap!"
        )
    elif "why do i need docker" in msg or "why docker" in msg:
        return (
            "**Why Docker is essential for Python Developers:**\n\n"
            "1. **Environment Parity**: Eliminates dependencies and OS differences between local development, staging, and production.\n"
            "2. **Microservice Packaging**: Standardizes how Flask and PostgreSQL services communicate via Docker Compose.\n"
            "3. **Cloud Readiness**: AWS ECS, EKS, and GCP Cloud Run all run container images."
        )
    elif "project" in msg or "hands-on" in msg:
        return (
            "**Recommended Capstone Project for Alex Patil:**\n\n"
            "• **Title**: Containerized Microservice Deployment on AWS ECS\n"
            "• **Architecture**: Flask API + PostgreSQL + Redis caching wrapped in multi-stage Docker builds.\n"
            "• **CI/CD**: Automated GitHub Actions workflow running PyTest suites and pushing images to AWS ECR.\n"
            "• **Impact**: Directly bridges all 3 top missing skills (Docker, AWS, CI/CD) on the resume!"
        )
    elif "how long" in msg or "time" in msg or "duration" in msg:
        return (
            "**Estimated Roadmap Timeline for Alex Patil:**\n\n"
            "• **Docker & Compose**: 4–8 hours\n"
            "• **AWS Cloud Fundamentals**: 10–20 hours\n"
            "• **CI/CD Pipeline Setup**: 4–8 hours\n"
            "• **Total Estimated Time**: ~**25–35 hours** to reach full Senior Python Developer market competitiveness."
        )
    elif "improve" in msg or "how can i" in msg or "better" in msg:
        return (
            "To take Alex Patil's resume from 82 to 95+, focus on three high-impact areas:\n\n"
            "1. **Quantify Achievements**: Add metric-driven outcomes to the NovaTech Solutions bullets (e.g. 'reduced API response times by 30%').\n"
            "2. **Add Containerization**: Integrate Docker and Docker Compose into the TaskFlow API project.\n"
            "3. **Demonstrate Cloud Skills**: Deploy a Flask microservice to AWS (EC2/RDS) with GitHub Actions CI/CD to prove cloud readiness."
        )
    elif "skill" in msg or "learn" in msg or "missing" in msg:
        return (
            "Based on the Python Developer target role, the top 3 skill gaps to prioritize are:\n\n"
            "1. **Docker & Containerization**: Critical for modern microservice deployment.\n"
            "2. **AWS Cloud Infrastructure**: Essential for deploying and scaling enterprise Flask apps.\n"
            "3. **CI/CD Automation**: Implement GitHub Actions to automate linting and PyTest execution on every commit."
        )
    elif "ready" in msg or "qualification" in msg or "level" in msg:
        return (
            "**Yes, Alex Patil is well-qualified for Mid-Level Python Developer roles!**\n\n"
            "• **ATS Score**: 86% (Strong structure and keyword density)\n"
            "• **Job Match**: 78% (Covers Python, Flask, SQL, and Git)\n"
            "• **Next Step**: Adding Docker and AWS will elevate this profile to Senior Python Developer salary tiers."
        )
    elif "interview" in msg or "question" in msg or "prepare" in msg:
        return (
            "Key technical interview topics for this Python Developer profile:\n\n"
            "1. **Python Core**: Explain Python's GIL, memory management, generator functions, and decorators.\n"
            "2. **Flask Architecture**: How the Application Factory pattern, Blueprints, and request context work.\n"
            "3. **SQL & Optimization**: Indexing strategies, N+1 query problems in ORMs, and transaction isolation levels.\n"
            "4. **System Design**: Designing a resilient REST API with rate limiting and database connection pooling."
        )
    elif "hinglish" in msg or "hindi" in msg:
        return (
            "Alex Patil ke liye sabhi missing skills ke video tutorials **English aur Hinglish / Hindi** dono mein available hain. Aap Results page ke learning cards se seedha Hinglish masterclasses open kar sakte hain!"
        )
    else:
        return (
            f"Hello! I'm your AI Career Assistant for **Alex Patil's Python Developer Resume**.\n\n"
            "You can ask me about:\n"
            "• What skill to learn first (e.g. Docker, AWS)\n"
            "• Capstone project ideas to bridge missing skills\n"
            "• Realistic learning time estimates\n"
            "• Technical interview preparation questions!"
        )
