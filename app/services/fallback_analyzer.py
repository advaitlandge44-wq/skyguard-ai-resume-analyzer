import re
from typing import Dict, Any, List
from app.services.career_roadmap_engine import (
    ROLE_MATRICES,
    TARGET_JOB_ROLES,
    SKILL_ALIASES,
    normalize_skill_name,
    get_role_configuration,
    analyze_skills_against_role,
    resolve_skill_learning_resources
)

# Backwards compatibility reference to taxonomy
ROLE_TAXONOMY = ROLE_MATRICES

ALL_RECOGNIZED_SKILLS = list(dict.fromkeys(list(SKILL_ALIASES.values())))

ACTION_VERBS = [
    "developed", "built", "engineered", "implemented", "designed", "created", "architected",
    "optimized", "enhanced", "streamlined", "deployed", "spearheaded", "orchestrated",
    "automated", "integrated", "managed", "led", "reduced", "increased", "generated"
]


def extract_skills_from_text(text: str) -> List[str]:
    """Finds all recognized technical skills inside a text string using alias dictionary."""
    text_lower = text.lower()
    found_skills = []
    
    for alias_key, canonical_name in SKILL_ALIASES.items():
        pattern = r'(?:\b|_)' + re.escape(alias_key) + r'(?:\b|_)'
        if re.search(pattern, text_lower):
            if canonical_name not in found_skills:
                found_skills.append(canonical_name)
            
    return found_skills


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
    Performs comprehensive heuristic & deterministic NLP analysis of the resume
    using the role-aware skill matrix across 25 target job roles.
    """
    # Role-aware skill matrix analysis
    skill_analysis = analyze_skills_against_role(
        resume_text=resume_text,
        target_role=target_role,
        job_description=job_description
    )

    canonical_role_title = skill_analysis["target_role"]
    matched_skills = skill_analysis["matched_skills"]
    weak_skills = skill_analysis["weak_skills"]
    missing_skills = skill_analysis["missing_skills"]
    learning_resources = skill_analysis["learning_resources"]
    learning_roadmap = skill_analysis["learning_roadmap"]

    # Calculate ATS score
    ats_result = analyze_ats_compliance(resume_text)
    ats_score = ats_result["ats_score"]

    # Calculate Job Match score with JD priority
    total_req_count = len(matched_skills) + len(weak_skills) + len(missing_skills)
    if total_req_count > 0:
        # Full weight for matched, partial weight (0.5) for weak
        effective_matched = len(matched_skills) + (0.5 * len(weak_skills))
        match_ratio = effective_matched / total_req_count
        job_match_score = int(35 + (match_ratio * 60))
    else:
        job_match_score = 70
    job_match_score = max(30, min(95, job_match_score))

    # Calculate Overall score
    overall_score = int((ats_score * 0.45) + (job_match_score * 0.55))
    overall_score = max(40, min(98, overall_score))

    # Recommended job roles comparison across 25 roles
    detected_lower = {s.lower() for s in (matched_skills + weak_skills)}
    recommended_roles = []
    for role_name, config in ROLE_MATRICES.items():
        core = [s.lower() for s in config["core_skills"]]
        matches = sum(1 for c in core if any(c in d or d in c for d in detected_lower))
        score = int((matches / max(1, len(core))) * 88) + 12
        score = min(96, max(40, score))
        recommended_roles.append({
            "role": config["title"],
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
        f"Demonstrates practical knowledge in key tools: {', '.join(matched_skills[:5])}" if matched_skills else "Clear educational and project background provided.",
        f"Relevant competencies identified that align with standard {canonical_role_title} engineering principles.",
        f"Well-structured resume sections with an ATS readability score of {ats_score}/100."
    ]

    weaknesses = []
    if missing_skills:
        weaknesses.append(f"Skill gap identified in target role competencies: {', '.join(missing_skills[:4])}.")
    if weak_skills:
        weaknesses.append(f"Found limited project depth in secondary competencies: {', '.join(weak_skills[:3])}.")
    if not weaknesses:
        weaknesses.append("Could expand on production cloud deployments and automated monitoring.")
    weaknesses.append("Project descriptions could benefit from more quantifiable business and performance metrics (e.g. latency, user scale, % speedup).")
    weaknesses.append("ATS formatting can be enhanced by aligning keywords more closely with target job requirements.")

    # Executive Summary
    all_known_str = ', '.join(matched_skills[:4]) if matched_skills else 'core software development'
    missing_str = ', '.join(missing_skills[:3]) if missing_skills else 'cloud and CI/CD'
    summary = (
        f"Candidate possesses a solid foundation with verified skills in {all_known_str}. "
        f"For the target role of '{canonical_role_title}', the profile demonstrates a {job_match_score}% alignment. "
        f"Bridging key missing competencies such as {missing_str} through targeted hands-on projects will significantly elevate candidacy."
    )

    return {
        "overall_score": overall_score,
        "ats_score": ats_score,
        "job_match_score": job_match_score,
        "summary": summary,
        "existing_skills": matched_skills if matched_skills else ["Python", "Git", "Problem Solving", "Object-Oriented Programming"],
        "matched_skills": matched_skills if matched_skills else ["Python", "Git", "Problem Solving", "Object-Oriented Programming"],
        "weak_skills": weak_skills,
        "missing_skills": missing_skills if missing_skills else ["Docker", "AWS", "CI/CD", "Automated Testing"],
        "learning_resources": learning_resources,
        "learning_roadmap": learning_roadmap,
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
            "Tailor the resume headline and summary to specifically reference " + canonical_role_title + "."
        ],
        "recommended_job_roles": recommended_roles
    }
