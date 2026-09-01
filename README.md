# SkyGuard AI: AI Resume Analyzer & Career Assistant
> **Final Year College Engineering Project**  
> *A full-stack, secure, production-grade AI platform for ATS resume evaluation, skill gap diagnostics, and career optimization.*

---

## 📌 1. Project Overview

**SkyGuard AI Resume Analyzer & Career Assistant** is a web application designed to bridge the gap between job seekers and Applicant Tracking Systems (ATS). Built using **Python, Flask, PyMuPDF, SQLAlchemy, and OpenAI**, the system ingests resumes in PDF or TXT format, parses structure and semantics, evaluates them against specific job roles and job descriptions, detects critical skill deficiencies, and delivers step-by-step actionable learning roadmaps.

Unlike basic tutorial applications, SkyGuard is built with **enterprise security safeguards**, strict **cross-user data isolation**, **prompt injection defense**, **zero-fabrication AI bullet rewriters**, and a **deterministic local NLP engine** that guarantees seamless offline presentations even without an active OpenAI API key.

---

## ✨ 2. Key Features

- **🛡️ Advanced ATS Compatibility Audit**: Evaluates contact header presence, standard section readability, font hierarchy, and keyword density with actionable improvement checklists.
- **📊 Tri-Metric Scoring Engine**: Computes weighted scores for **Overall Resume Quality**, **ATS Compatibility**, and **Job Role Alignment**.
- **🧩 Skill Gap Matrix**: Automatically categorizes detected technical competencies against industry requirements and highlights missing high-demand tools.
- **🗺️ Step-by-Step Learning Roadmap**: Generates structured weekly learning phases complete with rationale and practical capstone project ideas (no fake course links).
- **✨ Zero-Fabrication Resume Improver**: Interactive AI bullet point rewriter using the STAR (Situation, Task, Action, Result) method and active verbs without inventing fake credentials or unearned metrics.
- **🎯 Multi-Role Matcher**: Benchmarks candidate skills against adjacent industry roles (e.g., Python Developer, Backend Engineer, Data Analyst, Cloud DevOps).
- **💬 Scoped Career Chatbot**: Context-aware assistant strictly isolated to the user's current resume session for questions, clarifications, and interview prep.
- **📄 Clean PDF / Printable Career Reports**: One-click generation of professional printable diagnostic reports.
- **🔒 Enterprise Security**: Werkzeug password hashing, CSRF token validation, session fixation protection, rate limiting with Flask-Limiter, and UUID sanitized file storage.

---

## 🛠️ 3. Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3.10+, Flask 3.x, Werkzeug, Flask-Limiter, Flask-WTF (CSRF) |
| **Database** | SQLite3, SQLAlchemy ORM |
| **Document Processing** | PyMuPDF (`fitz`), `pypdf`, UTF-8 text normalizer |
| **AI / NLP Engine** | OpenAI API (`gpt-4o-mini` / `gpt-4o`) + Deterministic Local NLP Fallback |
| **Frontend** | HTML5, Modern Vanilla CSS (Design Tokens, Glassmorphism), Vanilla JavaScript |
| **Testing** | Pytest, Pytest-Flask |

---

## 🏗️ 4. System Architecture & Flow

```text
[Candidate]
    │
    ▼
[Landing Page / Register / Login] (Werkzeug Hash + CSRF + Session Fixation Guard)
    │
    ▼
[User Dashboard] ─── (Lifetime Analytics, Recent Analyses, Quick Actions)
    │
    ▼
[Upload Resume (PDF/TXT) + Select Target Role + Optional JD]
    │
    ├─► [PyMuPDF Text Extractor & Normalizer] (Corrupt/Empty/Encrypted Checks)
    │
    ├─► [Backend AI Pipeline with Prompt Injection Delimiters]
    │       ├─ If OpenAI Key Configured: GPT-4o-mini (Structured JSON)
    │       └─ If Offline / No Key: Deterministic Heuristic NLP Engine
    │
    ▼
[Interactive Results Dashboard]
    ├── Overall Score, ATS Score, Job Match Gauge Animations
    ├── Strengths & Weaknesses Breakdown
    ├── Skill Gap Matrix (Existing vs Missing Skills)
    ├── Structured Learning Roadmap
    ├── STAR Bullet Point Rewriter
    ├── Multi-Role Suitability Percentages
    └── Scoped AI Career Chatbot
    │
    ▼
[Database Persistence] ─── (User Ownership Isolation & Full History)
```

---

## 📂 5. Project Directory Structure

```text
sky-guard/
│
├── app/
│   ├── __init__.py                # Flask app factory, extensions, rate limits & error handlers
│   ├── models.py                  # SQLAlchemy models: User, Resume, Analysis, ChatMessage
│   │
│   ├── routes/
│   │   ├── auth.py                # Register, Login, Logout, Profile management
│   │   ├── main.py                # Landing page, Dashboard, History
│   │   ├── resume.py              # Resume upload, validation, extraction
│   │   ├── analysis.py            # Results dashboard, report export, record deletion
│   │   └── api.py                 # Async endpoints: Chatbot, Bullet Improver
│   │
│   ├── services/
│   │   ├── pdf_parser.py          # PyMuPDF extraction, validation & normalizer
│   │   ├── openai_service.py      # OpenAI integration with schema validation
│   │   ├── fallback_analyzer.py   # Deterministic NLP rule-based engine (Offline demo)
│   │   └── security.py            # Password hashing, filename sanitation, CSRF
│   │
│   ├── static/
│   │   ├── css/
│   │   │   ├── variables.css      # Design tokens (colors, gradients, glassmorphism)
│   │   │   ├── main.css           # Base styles, navbar, buttons, forms, responsive
│   │   │   ├── dashboard.css      # Dashboard metric cards & history tables
│   │   │   └── results.css        # Score gauges, skills matrix, roadmap, chat widget
│   │   └── js/
│   │       ├── main.js            # CSRF helper, toast alerts, mobile nav
│   │       ├── upload.js          # Drag & drop upload + animated multi-step progress
│   │       ├── results.js         # Score gauge animations, tab switching, PDF export
│   │       ├── improver.js        # AI resume bullet improver widget
│   │       └── chat.js            # Live AI Career Assistant chatbot widget
│   │
│   └── templates/
│       ├── base.html              # Base HTML layout with CSRF meta tags
│       ├── index.html             # High-converting Landing Page
│       ├── auth/                  # Login, Register, Profile templates
│       ├── dashboard/             # Dashboard and History templates
│       ├── resume/                # Upload & Text preview templates
│       ├── analysis/              # Results dashboard & Export report templates
│       └── errors/                # Custom 400, 401, 403, 404, 413, 429, 500 error pages
│
├── instance/                      # SQLite database storage
├── uploads/                       # Secure resume storage
├── tests/                         # Automated Pytest suite
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_upload.py
│   ├── test_analysis.py
│   └── test_security.py
│
├── .env.example                   # Environment variable template
├── .gitignore                     # Git rules
├── config.py                      # Development, Testing, and Production configs
├── requirements.txt               # Application dependencies
└── run.py                         # Application entry point
```

---

## 🚀 6. Installation & Setup Guide

### Prerequisites
- **Python 3.10, 3.11, 3.12, or 3.13**
- `pip` (Python package manager)

### Step 1: Clone or Navigate to the Project Folder
```bash
cd "sky guard"
```

### Step 2: Create and Activate a Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If script execution is disabled in PowerShell, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

**On Windows (Command Prompt - CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
copy .env.example .env
```
Open `.env` and set your preferred configurations:
```ini
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-custom-secret-key-here
DATABASE_URL=sqlite:///instance/resume_analyzer.db

# OpenAI API Key (Optional: App automatically uses Local NLP Engine if empty)
OPENAI_API_KEY=your_actual_openai_key_here
OPENAI_MODEL=gpt-4o-mini
```

### Step 5: Run the Application
```bash
python run.py
```
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 🧪 7. Running Automated Tests

Run the full automated test suite using `pytest`:

```powershell
python -m pytest tests/ -v
```

### Test Coverage Highlights:
- ✅ `test_auth.py`: Registration, password hashing, duplicate email rejection, session login/logout.
- ✅ `test_upload.py`: Safe filename generation, text normalization, PDF/TXT parsing, corrupt file handling.
- ✅ `test_analysis.py`: Fallback NLP engine schema compliance, score clamping (0-100), bullet improver, chatbot assistant.
- ✅ `test_security.py`: Cross-user data isolation (403), unauthorized route blocking, input sanitization.

---

## 🛡️ 8. Security & Privacy Implementation

1. **Prompt Injection Defense**: Resume content and Job Descriptions are treated as **untrusted user data**. All user inputs are encapsulated within explicit `<UNTRUSTED_RESUME_DATA>` delimiter blocks with clear system instructions prohibiting instruction execution.
2. **Zero-Fabrication Rewrites**: The AI Bullet Improver prompt strictly restricts hallucinations, preventing the generation of unearned certifications, fake metrics, or unmentioned technologies.
3. **Password Security**: Passwords are never stored in plain text. Werkzeug PBKDF2/Scrypt salting and hashing are enforced.
4. **Data Isolation**: Strict SQLAlchemy query filtering by `user_id == g.user.id` guarantees that candidates cannot view or delete other users' resumes or analyses.
5. **Rate Limiting**: Integrated `Flask-Limiter` protects analysis and authentication endpoints against brute force and API quota exhaustion.
6. **File Upload Security**: Uploads are restricted to `.pdf` and `.txt`, validated by file header, capped at 5MB, and stored with non-guessable UUID filenames to prevent path traversal attacks.

---

## 🎓 9. Final Year Project Submission Notes

- **Designed For**: Final Year College Engineering Project / Capstone Submission.
- **Explainability**: Every score displayed by the platform is broken down into constituent factors (Skills, ATS Readability, Role Match).
- **Offline / Viva Guarantee**: Even if internet connectivity drops or OpenAI API quota is exhausted during an oral examination or evaluation, the built-in deterministic heuristic NLP analyzer seamlessly provides complete analysis without crashing.

---

## 📄 10. License

This project is developed for educational and academic submission purposes.
