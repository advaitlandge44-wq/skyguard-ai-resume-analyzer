import pytest

def test_landing_page_cinematic_sections(client):
    """Verify all 8 cinematic sections, 3D canvas container, HUD badges, and texts."""
    response = client.get('/')
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # Section 1: Hero
    assert 'Analyze Your Resume.' in html
    assert 'Build Your Career.' in html
    assert 'AI-POWERED RESUME INTELLIGENCE' in html
    assert 'Understand your resume, discover missing skills' in html
    assert 'hero-3d-visual' in html
    assert 'three.min.js' in html
    assert 'hero_3d.js' in html
    assert 'ATS SCORE' in html
    assert '86%' in html
    assert 'JOB MATCH' in html
    assert '78%' in html
    assert 'SKILLS' in html
    assert 'AI ANALYSIS' in html
    assert 'READY' in html

    # Section 2: Your Resume, Understood
    assert 'Your Resume, Understood.' in html
    assert 'Skills' in html
    assert 'Experience' in html
    assert 'Projects' in html
    assert 'Education' in html
    assert 'Keywords' in html

    # Section 3: Know Your Score
    assert 'Know Your Score' in html
    assert 'Overall Score' in html
    assert 'ATS Score' in html
    assert 'Job Match' in html
    assert 'meterGradCyan' in html

    # Section 4: Find What's Missing
    assert "Find What's Missing" in html
    assert 'Python' in html and 'SQL' in html and 'Flask' in html
    assert 'Docker' in html and 'AWS' in html and 'REST APIs' in html
    assert 'CAREER GROWTH' in html

    # Section 5: Match With Your Target Job
    assert 'Match With Your Target Job' in html
    assert '1. RESUME' in html
    assert '2. AI MATCH ENGINE' in html
    assert '3. JOB DESCRIPTION' in html
    assert '4. MATCH SCORE' in html

    # Section 6: Build Your Career Roadmap
    assert 'Build Your Career Roadmap' in html
    assert 'Current Baseline' in html
    assert 'Phase 1: REST APIs & Containerization' in html
    assert 'Phase 2: Cloud Infrastructure & Resilience' in html
    assert 'Target Role: Senior Backend Developer' in html

    # Section 7: Improve Your Resume
    assert 'Improve Your Resume' in html
    assert 'Worked on Python project.' in html
    assert 'Developed a Flask-based AI resume analysis platform' in html
    assert 'STAR Method' in html

    # Section 8: Final CTA
    assert 'Your next opportunity starts with your resume.' in html
    assert 'Analyze My Resume' in html
