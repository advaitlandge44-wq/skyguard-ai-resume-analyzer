import io
import os
import fitz
from app.services.pdf_parser import extract_resume_text, normalize_resume_text, ResumeExtractionError
from app.services.security import generate_safe_filename


def test_safe_filename_generation():
    """Test sanitization of uploaded file names."""
    display_name, stored_name, ext = generate_safe_filename("../../../malicious_file.pdf")
    assert ".." not in stored_name
    assert "/" not in stored_name
    assert "\\" not in stored_name
    assert stored_name.endswith(".pdf")
    assert ext == "pdf"


def test_text_normalization():
    """Test normalization of whitespace and unprintable characters."""
    dirty_text = "Software   Engineer\r\n\r\n\r\n\r\nSkills:\tPython,   Flask\x00"
    clean_text = normalize_resume_text(dirty_text)
    assert "\x00" not in clean_text
    assert "Software Engineer" in clean_text
    assert "\n\n\n" not in clean_text


def test_txt_upload_and_analysis_flow(authenticated_client, app):
    """Test full upload and analysis flow using a plain text resume."""
    resume_content = b"""
    John Doe
    Email: john.doe@email.com | Phone: (555) 123-4567 | LinkedIn: linkedin.com/in/johndoe
    
    Professional Summary:
    Dedicated Python Developer with 3 years of experience building scalable backend APIs.
    
    Technical Skills:
    Python, Flask, Django, SQL, PostgreSQL, Git, REST API, Docker
    
    Work Experience:
    Software Developer | Tech Solutions Inc (2022 - Present)
    - Developed and deployed high-performance REST APIs using Python and Flask.
    - Optimized PostgreSQL database queries reducing API latency by 35%.
    - Implemented secure JWT authentication and rate limiting.
    
    Education:
    Bachelor of Science in Computer Science | State University (2018 - 2022)
    
    Projects:
    E-Commerce API: Built an end-to-end backend service using Python, Flask, Redis, and Docker.
    """
    
    data = {
        'target_role_select': 'Python Developer',
        'job_description': 'Looking for a Python Developer with Flask, SQL, and Docker experience.',
        'resume_file': (io.BytesIO(resume_content), 'john_resume.txt')
    }

    response = authenticated_client.post('/resume/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert b'Analysis & ATS Report' in response.data or b'Overall Score' in response.data


def test_pdf_extraction(tmp_path):
    """Test text extraction from a valid synthetic PDF document."""
    pdf_path = str(tmp_path / "test_resume.pdf")
    
    # Create test PDF using fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Jane Doe\nEmail: jane@test.com\nSkills: Python, Flask, SQL, Git, REST APIs")
    doc.save(pdf_path)
    doc.close()

    extracted = extract_resume_text(pdf_path, 'pdf')
    assert "Jane Doe" in extracted
    assert "Python" in extracted
    assert "jane@test.com" in extracted


def test_unsupported_file_extension(authenticated_client):
    """Test rejection of unsupported file types."""
    data = {
        'target_role_select': 'Python Developer',
        'resume_file': (io.BytesIO(b"executable data"), 'virus.exe')
    }
    response = authenticated_client.post('/resume/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert b'Unsupported file type' in response.data
