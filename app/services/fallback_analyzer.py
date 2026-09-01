import re
from typing import Dict, Any, List

# Standard role skill requirements taxonomy
ROLE_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "python developer": {
        "core_skills": ["python", "flask", "django", "fastapi", "sql", "postgresql", "git", "rest api", "unit testing", "docker"],
        "bonus_skills": ["redis", "celery", "aws", "pytest", "graphql", "ci/cd", "linux", "nosql", "mongodb", "microservices"],
        "description": "Python Software Development, Backend Architecture, and RESTful APIs"
    },
    "full stack developer": {
        "core_skills": ["javascript", "react", "node.js", "html5", "css3", "python", "sql", "git", "rest api", "typescript"],
        "bonus_skills": ["next.js", "tailwind css", "docker", "mongodb", "postgresql", "aws", "redux", "ci/cd", "vue.js", "graphql"],
        "description": "Frontend, Backend, and Database Web Application Development"
    },
    "backend developer": {
        "core_skills": ["python", "java", "node.js", "sql", "rest api", "postgresql", "docker", "git", "microservices", "redis"],
        "bonus_skills": ["kubernetes", "aws", "kafka", "ci/cd", "grpc", "system design", "linux", "mongodb", "elasticsearch"],
        "description": "Server-side logic, database performance, microservices, and API integrations"
    },
    "data analyst": {
        "core_skills": ["python", "sql", "excel", "tableau", "power bi", "pandas", "numpy", "data visualization", "statistics", "eda"],
        "bonus_skills": ["r", "machine learning", "bigquery", "snowflake", "matplotlib", "seaborn", "scikit-learn", "git", "etl"],
        "description": "Data modeling, statistical analysis, dashboard reporting, and business intelligence"
    },
    "data scientist": {
        "core_skills": ["python", "machine learning", "pandas", "numpy", "scikit-learn", "sql", "deep learning", "statistics", "data analysis"],
        "bonus_skills": ["tensorflow", "pytorch", "nlp", "computer vision", "aws", "docker", "mlops", "spark", "tableau"],
        "description": "Machine learning modeling, statistical inference, algorithms, and predictive analytics"
    },
    "software engineer": {
        "core_skills": ["python", "java", "c++", "data structures", "algorithms", "git", "sql", "system design", "oop", "testing"],
        "bonus_skills": ["docker", "linux", "ci/cd", "rest api", "cloud computing", "agile", "microservices", "design patterns"],
        "description": "General software engineering, data structures, algorithms, and scalable design"
    },
    "web developer": {
        "core_skills": ["html5", "css3", "javascript", "react", "responsive design", "git", "rest api", "bootstrap", "dom manipulation"],
        "bonus_skills": ["typescript", "tailwind css", "node.js", "seo", "webpack", "sass", "accessibility", "vue.js"],
        "description": "Client-side and full web interfaces, responsive styling, and modern UI engineering"
    },
    "devops engineer": {
        "core_skills": ["docker", "kubernetes", "linux", "ci/cd", "git", "aws", "terraform", "bash", "python", "jenkins"],
        "bonus_skills": ["ansible", "prometheus", "grafana", "azure", "gcp", "helm", "networking", "security"],
        "description": "Cloud infrastructure automation, container orchestration, and CI/CD pipelines"
    }
}

ALL_RECOGNIZED_SKILLS = [
    "python", "flask", "django", "fastapi", "java", "spring boot", "c++", "c#", ".net",
    "javascript", "typescript", "react", "vue.js", "angular", "node.js", "express", "next.js",
    "html", "html5", "css", "css3", "tailwind css", "bootstrap", "sass",
    "sql", "mysql", "postgresql", "sqlite", "mongodb", "redis", "elasticsearch", "cassandra",
    "git", "github", "gitlab", "docker", "kubernetes", "jenkins", "ci/cd", "linux", "bash",
    "aws", "azure", "gcp", "terraform", "ansible",
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn",
    "tableau", "power bi", "excel", "rest api", "graphql", "grpc", "microservices", "unit testing", "pytest", "jest", "agile", "scrum", "system design"
]

ACTION_VERBS = [
    "developed", "built", "engineered", "implemented", "designed", "created", "architected",
    "optimized", "enhanced", "streamlined", "deployed", "spearheaded", "orchestrated",
    "automated", "integrated", "managed", "led", "reduced", "increased", "generated"
]


def extract_skills_from_text(text: str) -> List[str]:
    """Finds all recognized technical skills inside a text string."""
    text_lower = text.lower()
    found_skills = []
    
    # Check boundary-matched skills
    for skill in ALL_RECOGNIZED_SKILLS:
        pattern = r'(?:\b|_)' + re.escape(skill) + r'(?:\b|_)'
        if re.search(pattern, text_lower):
            found_skills.append(skill.title() if len(skill) > 4 else skill.upper())
            
    return list(dict.fromkeys(found_skills))  # preserve order & unique


def analyze_ats_compliance(text: str) -> Dict[str, Any]:
    """Evaluates ATS structural compatibility, section headers, contact info, and formatting."""
    text_lower = text.lower()
    ats_score = 70
    good_points = []
    improvement_points = []
    
    # 1. Contact Information Checks
    has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text))
    has_phone = bool(re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text))
    has_linkedin = "linkedin.com" in text_lower or "linkedin" in text_lower
    has_github = "github.com" in text_lower or "github" in text_lower

    if has_email:
        ats_score += 5
        good_points.append("✓ Professional email address detected")
    else:
        ats_score -= 10
        improvement_points.append("⚠ Add a clear email address in your contact header")

    if has_phone:
        ats_score += 5
        good_points.append("✓ Phone number detected")
    else:
        ats_score -= 5
        improvement_points.append("⚠ Add a phone number in your header for recruiter contact")

    if has_linkedin or has_github:
        ats_score += 5
        good_points.append("✓ Online profile link (LinkedIn/GitHub) present")
    else:
        improvement_points.append("⚠ Add clickable LinkedIn and GitHub profile URLs")

    # 2. Section Header Checks
    sections = {
        "experience": ["experience", "work history", "employment", "internship", "professional experience"],
        "education": ["education", "academic", "university", "college", "degree", "bachelor", "master"],
        "projects": ["projects", "personal projects", "academic projects", "key projects"],
        "skills": ["skills", "technical skills", "technologies", "core competencies", "tools"]
    }

    for sec, keywords in sections.items():
        if any(kw in text_lower for kw in keywords):
            ats_score += 4
            good_points.append(f"✓ Standard '{sec.title()}' section heading detected")
        else:
            ats_score -= 6
            improvement_points.append(f"⚠ Missing or unclear '{sec.title()}' section heading")

    # 3. Action Verbs & Metrics
    verb_count = sum(1 for verb in ACTION_VERBS if re.search(r'\b' + verb + r'\b', text_lower))
    if verb_count >= 5:
        ats_score += 5
        good_points.append("✓ Strong action verbs used across project and work descriptions")
    else:
        ats_score -= 5
        improvement_points.append("⚠ Incorporate more proactive action verbs (e.g., Developed, Engineered, Optimized)")

    has_metrics = bool(re.search(r'\b\d+%\b|\$\d+|\b\d+x\b|\b\d+\+?\s*(users|clients|requests|ms|seconds|hours)', text_lower))
    if has_metrics:
        ats_score += 5
        good_points.append("✓ Quantifiable metrics or impact numbers detected")
    else:
        ats_score -= 5
        improvement_points.append("⚠ Include quantifiable achievements (e.g., 'improved performance by 25%', 'served 1,000+ users')")

    ats_score = max(35, min(96, ats_score))
    return {
        "ats_score": ats_score,
        "good_points": good_points,
        "improvement_points": improvement_points
    }


def generate_fallback_analysis(resume_text: str, target_role: str, job_description: str = "") -> Dict[str, Any]:
    """
    Performs comprehensive heuristic & deterministic NLP analysis of the resume.
    Ensures 100% adherence to the structured JSON schema.
    """
    role_key = target_role.strip().lower()
    matched_role_config = None
    
    # Try finding closest role template
    for key, config in ROLE_TAXONOMY.items():
        if key in role_key or role_key in key:
            matched_role_config = config
            break
            
    if not matched_role_config:
        # Default to software engineer taxonomy
        matched_role_config = ROLE_TAXONOMY["software engineer"]

    # Extract detected skills from resume
    detected_skills = extract_skills_from_text(resume_text)
    
    # Determine target skills from taxonomy and/or job description
    target_skills_raw = list(matched_role_config["core_skills"] + matched_role_config["bonus_skills"][:4])
    if job_description:
        jd_skills = extract_skills_from_text(job_description)
        if jd_skills:
            target_skills_raw = [s.lower() for s in jd_skills]

    # Normalize comparison
    detected_lower = {s.lower() for s in detected_skills}
    matching_skills = []
    missing_skills = []

    for req in target_skills_raw:
        clean_req = req.lower()
        if any(clean_req in det or det in clean_req for det in detected_lower):
            matching_skills.append(clean_req.title() if len(clean_req) > 4 else clean_req.upper())
        else:
            missing_skills.append(clean_req.title() if len(clean_req) > 4 else clean_req.upper())

    matching_skills = list(dict.fromkeys(matching_skills))
    missing_skills = list(dict.fromkeys(missing_skills))

    # Calculate ATS score
    ats_result = analyze_ats_compliance(resume_text)
    ats_score = ats_result["ats_score"]

    # Calculate Job Match score
    total_req_count = len(matching_skills) + len(missing_skills)
    if total_req_count > 0:
        match_ratio = len(matching_skills) / total_req_count
        job_match_score = int(40 + (match_ratio * 55))
    else:
        job_match_score = 70
    job_match_score = max(30, min(95, job_match_score))

    # Calculate Overall score
    overall_score = int((ats_score * 0.45) + (job_match_score * 0.55))
    overall_score = max(40, min(98, overall_score))

    # Generate Learning Roadmap
    learning_roadmap = []
    top_missing = missing_skills[:5] if missing_skills else ["Docker", "CI/CD Pipelines", "System Design", "Unit Testing", "Cloud Architecture"]
    
    order_labels = ["Week 1-2 (Foundation)", "Week 3 (Core Integration)", "Week 4 (Architecture & Scale)", "Week 5 (Testing & Quality)", "Week 6 (Deployment & Cloud)"]
    project_ideas = [
        "Build a dedicated REST API service showcasing clean repository architecture.",
        "Containerize your backend application with multi-stage Docker builds.",
        "Implement automated CI/CD workflows with GitHub Actions.",
        "Add unit and integration test suites with 80%+ code coverage.",
        "Deploy the application to AWS/GCP with secure secrets management."
    ]

    for idx, skill in enumerate(top_missing):
        learning_roadmap.append({
            "week": f"Phase {idx + 1}",
            "order": order_labels[idx] if idx < len(order_labels) else f"Phase {idx + 1}",
            "skill": skill,
            "why": f"Crucial for modern {target_role.title()} positions to handle production-scale workloads.",
            "project_idea": project_ideas[idx] if idx < len(project_ideas) else f"Develop a capstone project utilizing {skill}."
        })

    # Recommended job roles comparison
    recommended_roles = []
    for role_name, config in ROLE_TAXONOMY.items():
        core = [s.lower() for s in config["core_skills"]]
        matches = sum(1 for c in core if any(c in d for d in detected_lower))
        score = int((matches / max(1, len(core))) * 90) + 10
        score = min(95, max(45, score))
        recommended_roles.append({
            "role": role_name.title(),
            "match_percentage": score,
            "explanation": f"Matches {matches} out of {len(core)} core competencies in {config['description']}."
        })
    recommended_roles = sorted(recommended_roles, key=lambda x: x["match_percentage"], reverse=True)[:5]

    # Keyword Suggestions
    keyword_suggestions = [
        {"keyword": s, "category": "Technical Skill", "importance": "High"} for s in missing_skills[:6]
    ]
    if not keyword_suggestions:
        keyword_suggestions = [
            {"keyword": "RESTful APIs", "category": "Backend", "importance": "High"},
            {"keyword": "CI/CD Automation", "category": "DevOps", "importance": "Medium"},
            {"keyword": "Performance Optimization", "category": "Engineering", "importance": "High"}
        ]

    # Strengths and Weaknesses
    strengths = [
        f"Demonstrates practical knowledge in key tools: {', '.join(detected_skills[:5])}" if detected_skills else "Clear educational and project background provided.",
        "Contains relevant project experience aligning with software engineering principles.",
        f"Well-structured resume sections with an ATS readability score of {ats_score}/100."
    ]

    weaknesses = [
        f"Skill gap identified in target role competencies: {', '.join(missing_skills[:4])}" if missing_skills else "Could expand on production cloud deployments.",
        "Project descriptions could benefit from more quantifiable business/performance impact numbers.",
        "ATS formatting can be enhanced by aligning keywords more closely with target job requirements."
    ]

    # Summary
    summary = (
        f"Candidate possesses a solid foundation with skills in {', '.join(detected_skills[:4]) if detected_skills else 'core software development'}. "
        f"For the target role of '{target_role.title()}', the profile demonstrates a {job_match_score}% alignment. "
        f"Addressing key missing competencies such as {', '.join(missing_skills[:3]) if missing_skills else 'cloud and CI/CD'} will significantly enhance competitiveness."
    )

    return {
        "overall_score": overall_score,
        "ats_score": ats_score,
        "job_match_score": job_match_score,
        "summary": summary,
        "existing_skills": detected_skills if detected_skills else ["Python", "Git", "Problem Solving", "Object-Oriented Programming"],
        "missing_skills": missing_skills if missing_skills else ["Docker", "Cloud (AWS/GCP)", "CI/CD", "Automated Testing"],
        "strengths": strengths,
        "weaknesses": weaknesses,
        "experience_feedback": [
            "Use the STAR method (Situation, Task, Action, Result) for each experience entry.",
            "Quantify achievements with percentages, latency reductions, or user metrics."
        ],
        "project_feedback": [
            "Highlight modern frameworks, database designs, and authentication methods used.",
            "Include live demo links or public GitHub repository URLs for verification."
        ],
        "education_feedback": [
            "List relevant coursework, honors, or academic achievements prominently.",
            "Include graduation timeline and major field of study clearly."
        ],
        "formatting_feedback": ats_result["improvement_points"] if ats_result["improvement_points"] else ["Formatting is clean and adheres to standard ATS layouts."],
        "keyword_suggestions": keyword_suggestions,
        "improvement_suggestions": [
            f"Incorporate missing high-demand skills ({', '.join(missing_skills[:3])}) into project bullet points.",
            "Add quantifiable metrics to at least 3 project descriptions.",
            "Tailor the resume headline and summary to specifically reference " + target_role.title() + "."
        ],
        "learning_roadmap": learning_roadmap,
        "recommended_job_roles": recommended_roles
    }
