import os
import re
import logging

logger = logging.getLogger(__name__)

# Try importing fitz (PyMuPDF), with pypdf as fallback
try:
    import fitz  # PyMuPDF
    HAVE_PYMUPDF = True
except ImportError:
    HAVE_PYMUPDF = False

try:
    import pypdf
    HAVE_PYPDF = True
except ImportError:
    HAVE_PYPDF = False


class ResumeExtractionError(Exception):
    """Custom exception for resume extraction failures."""
    pass


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file using PyMuPDF with pypdf fallback.
    Performs safety checks for password protection, corruption, and scanned/empty PDFs.
    """
    if not os.path.exists(file_path):
        raise ResumeExtractionError("The uploaded resume file could not be found.")

    text_content = []

    # 1. Try PyMuPDF
    if HAVE_PYMUPDF:
        try:
            with fitz.open(file_path) as doc:
                if doc.is_encrypted:
                    raise ResumeExtractionError(
                        "This PDF is password-protected. Please upload an unprotected PDF file."
                    )

                if doc.page_count == 0:
                    raise ResumeExtractionError("The uploaded PDF file contains no pages.")

                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    page_text = page.get_text("text")
                    if page_text:
                        text_content.append(page_text)
        except fitz.FileDataError:
            raise ResumeExtractionError("The uploaded PDF file is corrupted and cannot be read.")
        except ResumeExtractionError:
            raise
        except Exception as e:
            logger.warning(f"PyMuPDF extraction failed: {e}. Trying fallback if available.")
            text_content = []

    # 2. Fallback to pypdf if PyMuPDF didn't yield text or wasn't available
    if not text_content and HAVE_PYPDF:
        try:
            reader = pypdf.PdfReader(file_path)
            if reader.is_encrypted:
                raise ResumeExtractionError(
                    "This PDF is password-protected. Please upload an unprotected PDF file."
                )
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_content.append(extracted)
        except ResumeExtractionError:
            raise
        except Exception as e:
            logger.error(f"pypdf extraction error: {e}")
            raise ResumeExtractionError("Unable to extract text from the PDF. File may be corrupted.")

    combined_text = "\n".join(text_content).strip()

    # 3. Check for scanned / image-only / empty PDF
    if not combined_text or len(combined_text.strip()) < 30:
        raise ResumeExtractionError(
            "Unable to extract readable text from this resume. Please upload a text-based PDF or TXT file."
        )

    return normalize_resume_text(combined_text)


def extract_text_from_txt(file_path: str) -> str:
    """
    Extracts text from a plain text file safely handling UTF-8, Latin-1, and Windows-1252 encodings.
    """
    if not os.path.exists(file_path):
        raise ResumeExtractionError("The uploaded resume file could not be found.")

    encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    raw_content = None

    with open(file_path, 'rb') as f:
        data = f.read()

    if not data or len(data.strip()) == 0:
        raise ResumeExtractionError("The uploaded text file is empty.")

    for encoding in encodings_to_try:
        try:
            raw_content = data.decode(encoding)
            break
        except UnicodeDecodeError:
            continue

    if raw_content is None:
        raise ResumeExtractionError("Unable to decode the text file. Please ensure it is saved in UTF-8 format.")

    normalized = normalize_resume_text(raw_content)
    if not normalized or len(normalized.strip()) < 30:
        raise ResumeExtractionError(
            "The text file does not contain sufficient resume content (minimum 30 characters required)."
        )

    return normalized


def extract_resume_text(file_path: str, file_type: str) -> str:
    """
    Dispatcher function to extract and normalize text from either PDF or TXT files.
    """
    file_type = file_type.lower().strip().replace('.', '')
    if file_type == 'pdf':
        return extract_text_from_pdf(file_path)
    elif file_type == 'txt':
        return extract_text_from_txt(file_path)
    else:
        raise ResumeExtractionError(f"Unsupported file format '{file_type}'. Only PDF and TXT are supported.")


def normalize_resume_text(text: str) -> str:
    """
    Normalizes extracted resume text by cleaning unprintable characters,
    collapsing excessive whitespace, and removing null bytes.
    """
    if not text:
        return ""

    # Remove null bytes and non-printable control characters (except newline, tab, carriage return)
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)

    # Normalize line breaks
    cleaned = cleaned.replace('\r\n', '\n').replace('\r', '\n')

    # Collapse sequences of more than 2 consecutive newlines
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

    # Collapse multiple spaces and tabs into single space
    cleaned = re.sub(r'[ \t]{2,}', ' ', cleaned)

    return cleaned.strip()
