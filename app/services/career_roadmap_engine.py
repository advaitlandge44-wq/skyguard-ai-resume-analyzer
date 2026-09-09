import re
import urllib.parse
from typing import Dict, Any, List, Optional, Tuple

# =====================================================================
# 1. FIXED 25 TARGET JOB ROLES
# =====================================================================

TARGET_JOB_ROLES: List[str] = [
    "Software Developer",
    "Full Stack Developer",
    "Frontend Developer",
    "Backend Developer",
    "Python Developer",
    "Java Developer",
    "JavaScript Developer",
    "React Developer",
    "Mobile App Developer",
    "Data Analyst",
    "Data Scientist",
    "Machine Learning Engineer",
    "AI Engineer",
    "Generative AI Engineer",
    "NLP Engineer",
    "DevOps Engineer",
    "Cloud Engineer",
    "Cybersecurity Analyst",
    "QA / Software Testing Engineer",
    "Database Developer / DBA",
    "UI/UX Designer",
    "Business Analyst",
    "System Administrator",
    "MLOps Engineer",
    "AI/ML Research Engineer"
]

ROLE_CATEGORIES: Dict[str, List[str]] = {
    "Software & Web Engineering": [
        "Software Developer",
        "Full Stack Developer",
        "Frontend Developer",
        "Backend Developer",
        "Python Developer",
        "Java Developer",
        "JavaScript Developer",
        "React Developer",
        "Mobile App Developer"
    ],
    "Data & Artificial Intelligence": [
        "Data Analyst",
        "Data Scientist",
        "Machine Learning Engineer",
        "AI Engineer",
        "Generative AI Engineer",
        "NLP Engineer",
        "MLOps Engineer",
        "AI/ML Research Engineer"
    ],
    "Cloud, DevOps & Systems": [
        "DevOps Engineer",
        "Cloud Engineer",
        "System Administrator",
        "Database Developer / DBA"
    ],
    "Security, Quality & Analysis": [
        "Cybersecurity Analyst",
        "QA / Software Testing Engineer",
        "Business Analyst",
        "UI/UX Designer"
    ]
}

# =====================================================================
# 2. CURATED 25 MASTER AI LEARNING RESOURCES (Divyam Dawar Library)
# =====================================================================

CURATED_LEARNING_LIBRARY: Dict[str, Dict[str, str]] = {
    "python": {
        "title": "Python Complete Masterclass & Projects",
        "url": "https://youtube.com/playlist?list=PLKnIA16_Rmvb1RYR-iTA_hzckhdONtSW4&si=iFUVwQ-i9arYMjEz",
        "language": "English",
        "format": "Curated Course Playlist"
    },
    "data analyst bootcamp": {
        "title": "Data Analyst Zero to Hero Bootcamp",
        "url": "https://youtu.be/PSNXoAs2FtQ?si=f9h-4FP2dONbqhYg",
        "language": "English",
        "format": "Masterclass Video"
    },
    "machine learning": {
        "title": "Machine Learning Complete Playlist",
        "url": "https://youtube.com/playlist?list=PLKnIA16_Rmvbr7zKYQuBfsVkjoLcJgxHH&si=AQ1td8bSZbnbYibt",
        "language": "English",
        "format": "Curated Course Playlist"
    },
    "deep learning": {
        "title": "Deep Learning & Neural Networks Architecture",
        "url": "https://youtube.com/playlist?list=PLKnIA16_RmvYuZauWaPlRTC54KxSNLtNn&si=TtWtWq-6UI2UCFij",
        "language": "English",
        "format": "Curated Course Playlist"
    },
    "generative ai": {
        "title": "Generative AI Masterclass & LLM Architecture",
        "url": "https://youtube.com/playlist?list=PLKnIA16_RmvaTbihpo4MtzVm4XOQa0ER0&si=oAEAd_fii3ECytsQ",
        "language": "English",
        "format": "Curated Course Playlist"
    },
    "nlp and transformer architecture": {
        "title": "NLP & Transformer Architecture Deep Dive",
        "url": "https://youtu.be/3bPhDUSAUYI?si=rYlwxp4SY0Y3rTcG",
        "language": "English",
        "format": "Masterclass Video"
    },
    "agentic ai": {
        "title": "Agentic AI & Multi-Agent Systems Playlist",
        "url": "https://youtube.com/playlist?list=PLKnIA16_RmvYsvB8qkUQuJmJNuiCUJFPL&si=fL8A99RLb0n7FRE5",
        "language": "English",
        "format": "Curated Course Playlist"
    },
    "practical ai projects": {
        "title": "Practical End-to-End AI Projects",
        "url": "https://youtu.be/pEiq3sI8dYQ?si=AWAy0qw4yvHqeTW3",
        "language": "English",
        "format": "Masterclass Video"
    },
    "agentic coding with claude code": {
        "title": "Agentic Coding with Claude Code",
        "url": "https://youtu.be/K_KIQA849cs?si=ThscjLhxzB7pjblJ",
        "language": "English",
        "format": "Masterclass Video"
    },
    "mcp": {
        "title": "Model Context Protocol (MCP) Implementation",
        "url": "https://youtube.com/playlist?list=PLKnIA16_Rmva_oZ9F4ayUu9qcWgF7Fyc0&si=pzylTHxyGEh8OK29",
        "language": "English",
        "format": "Curated Course Playlist"
    },
    "build gpt from scratch": {
        "title": "Build GPT Architecture from Scratch",
        "url": "https://youtu.be/kCc8FmEb1nY?si=f09rOawS2c49yRdz",
        "language": "English",
        "format": "Masterclass Video"
    },
    "rag": {
        "title": "Retrieval-Augmented Generation (RAG) Architecture",
        "url": "https://youtu.be/X0btK9X0Xnk?si=oG0-zvPapp63NuFK",
        "language": "English",
        "format": "Masterclass Video"
    },
    "rag frameworks": {
        "title": "Top RAG Frameworks on GitHub by Stars Guide",
        "url": "https://florinelchis.medium.com/top-10-rag-frameworks-on-github-by-stars-january-2026-e6edff1e0d91",
        "language": "English",
        "format": "Architecture Guide"
    },
    "fastapi": {
        "title": "FastAPI Modern High-Performance APIs",
        "url": "https://youtube.com/playlist?list=PLKnIA16_RmvZ41tjbKB2ZnwchfniNsMuQ&si=TYjhduFy1avM6v05",
        "language": "English",
        "format": "Curated Course Playlist"
    },
    "llm evaluation": {
        "title": "LLM Evaluation Frameworks & Benchmarking",
        "url": "https://youtu.be/6W92_t9FveA?si=aQ6HcDuRmLApEw1L",
        "language": "English",
        "format": "Masterclass Video"
    },
    "llmops": {
        "title": "LLMOps Production Pipeline & Deployment",
        "url": "https://youtu.be/NuWRAiYnjxw?si=-7BTIv-CX4pkCCYH",
        "language": "English",
        "format": "Masterclass Video"
    },
    "litellm": {
        "title": "LiteLLM Multi-Model Gateway & Routing",
        "url": "https://youtu.be/RN3baOpNA6w?si=CCzGqonE9FnFVswp",
        "language": "English",
        "format": "Masterclass Video"
    },
    "mesh api": {
        "title": "Mesh API & Distributed AI Systems",
        "url": "https://youtu.be/yAczx0_NtyU?si=X1YsCaaEjYGjSkaG",
        "language": "English",
        "format": "Masterclass Video"
    },
    "ai guardrails / security": {
        "title": "AI Guardrails, Safety & Prompt Security",
        "url": "https://youtu.be/rQE3w8Qjx98?si=5x9gCpgAzcw8vihT",
        "language": "English",
        "format": "Masterclass Video"
    },
    "arize tracing / observability": {
        "title": "Arize AI Tracing, Monitoring & Observability",
        "url": "https://youtu.be/fHGSxOhWO-g?si=axuOUf8t1GIGWBhl",
        "language": "English",
        "format": "Masterclass Video"
    },
    "loop / harness engineering": {
        "title": "Loop & Harness Engineering for Autonomous Agents",
        "url": "https://youtu.be/3uO6V05LBjU?si=a3QEvjOF6wffIDoe",
        "language": "English",
        "format": "Masterclass Video"
    },
    "fde roadmap": {
        "title": "Forward Deployed AI Engineering Roadmap",
        "url": "https://youtu.be/SOU28VT-Ns4?si=9TyREkV0S7G72Q0p",
        "language": "English",
        "format": "Masterclass Video"
    },
    "gcp zero to hero": {
        "title": "Google Cloud Platform (GCP) Zero to Hero",
        "url": "https://youtu.be/N5rXROueKhw?si=S6A8Ruq238LxCGGz",
        "language": "English",
        "format": "Masterclass Video"
    },
    "azure zero to hero": {
        "title": "Microsoft Azure Cloud Zero to Hero",
        "url": "https://youtu.be/10jm7Waan8M?si=cx-Uu8hxovhQaf5h",
        "language": "English",
        "format": "Masterclass Video"
    },
    "aws zero to hero": {
        "title": "Amazon Web Services (AWS) Zero to Hero",
        "url": "https://youtu.be/GkKNxyLp_V0?si=dLbrKOy-q7WaCb9A",
        "language": "English",
        "format": "Masterclass Video"
    }
}

# =====================================================================
# 3. SKILL ALIASES & NORMALIZATION DICTIONARY
# =====================================================================

SKILL_ALIASES: Dict[str, str] = {
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "py": "Python",
    "python": "Python",
    "python3": "Python",
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "react native": "React Native",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "express.js": "Express.js",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "next": "Next.js",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "angular": "Angular",
    "angularjs": "Angular",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "pgsql": "PostgreSQL",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "sqlite3": "SQLite",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "nosql": "NoSQL",
    "sql": "SQL",
    "rest": "REST API",
    "restful": "REST API",
    "rest api": "REST API",
    "restful api": "REST API",
    "rest apis": "REST API",
    "graphql": "GraphQL",
    "docker": "Docker",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "dl": "Deep Learning",
    "deep learning": "Deep Learning",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "cv": "Computer Vision",
    "computer vision": "Computer Vision",
    "genai": "Generative AI",
    "gen ai": "Generative AI",
    "generative ai": "Generative AI",
    "llm": "LLMs",
    "llms": "LLMs",
    "large language models": "LLMs",
    "rag": "RAG",
    "retrieval augmented generation": "RAG",
    "prompt engineering": "Prompt Engineering",
    "vector db": "Vector Databases",
    "vector database": "Vector Databases",
    "vector databases": "Vector Databases",
    "pinecone": "Pinecone",
    "chromadb": "ChromaDB",
    "qdrant": "Qdrant",
    "weaviate": "Weaviate",
    "langchain": "LangChain",
    "llamaindex": "LlamaIndex",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "spring": "Spring Boot",
    "spring boot": "Spring Boot",
    "springboot": "Spring Boot",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "continuous integration": "CI/CD",
    "jenkins": "Jenkins",
    "github actions": "GitHub Actions",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "linux": "Linux",
    "bash": "Bash",
    "shell": "Bash / Shell",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scikit-learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "tableau": "Tableau",
    "excel": "Excel",
    "advanced excel": "Excel",
    "eda": "Exploratory Data Analysis (EDA)",
    "data visualization": "Data Visualization",
    "statistics": "Statistics",
    "selenium": "Selenium",
    "playwright": "Playwright",
    "cypress": "Cypress",
    "postman": "Postman",
    "jira": "Jira",
    "figma": "Figma",
    "wireframing": "Wireframing",
    "prototyping": "Prototyping",
    "ux research": "UX Research",
    "ui design": "UI Design",
    "design systems": "Design Systems",
    "accessibility": "Accessibility (a11y)",
    "system design": "System Design",
    "microservices": "Microservices",
    "unit testing": "Unit Testing",
    "pytest": "PyTest",
    "junit": "JUnit",
    "jest": "Jest",
    "oop": "OOP",
    "data structures": "Data Structures & Algorithms",
    "dsa": "Data Structures & Algorithms",
    "algorithms": "Data Structures & Algorithms",
    "cybersecurity": "Cybersecurity Fundamentals",
    "security": "Cybersecurity Fundamentals",
    "siem": "SIEM Tools",
    "owasp": "OWASP Security",
    "incident response": "Incident Response",
    "network security": "Network Security",
    "dba": "Database Administration",
    "database administration": "Database Administration",
    "query optimization": "Query Optimization",
    "indexing": "Database Indexing",
    "etl": "ETL Pipelines",
    "mlops": "MLOps",
    "llmops": "LLMOps",
    "litellm": "LiteLLM",
    "mcp": "Model Context Protocol (MCP)",
    "mesh api": "Mesh API",
    "agentic ai": "Agentic AI",
    "business analysis": "Business Analysis",
    "requirements gathering": "Requirements Gathering",
    "agile": "Agile / Scrum",
    "scrum": "Agile / Scrum"
}

# =====================================================================
# 4. COMPREHENSIVE 25 ROLE SKILL MATRICES & ROADMAP BLUEPRINTS
# =====================================================================

ROLE_MATRICES: Dict[str, Dict[str, Any]] = {
    "software developer": {
        "title": "Software Developer",
        "description": "Core software engineering, algorithms, scalable application design, and clean code practices.",
        "core_skills": ["Python", "Data Structures & Algorithms", "OOP", "Git", "SQL", "REST API", "Unit Testing"],
        "important_skills": ["Docker", "Linux", "System Design", "Microservices", "CI/CD"],
        "supporting_skills": ["PostgreSQL", "Design Patterns", "Agile / Scrum", "Redis"],
        "advanced_skills": ["Cloud (AWS/GCP)", "Kubernetes", "Performance Optimization"],
        "tools": ["Git", "GitHub", "Postman", "VS Code", "PyTest"],
        "cloud_platform": ["AWS", "Linux"],
        "soft_skills": ["Problem Solving", "Code Reviews", "Technical Communication"],
        "default_phase_focus": ["Programming Foundations & DSA", "REST API & Database Layer", "Clean Code & Automated Testing", "Modular Capstone Architecture", "Containerization & CI/CD", "Technical System Design & Coding Interview"]
    },
    "full stack developer": {
        "title": "Full Stack Developer",
        "description": "End-to-end web engineering spanning reactive frontend interfaces, scalable backend services, databases, and containerized deployment.",
        "core_skills": ["JavaScript", "React", "Node.js", "HTML5", "CSS3", "REST API", "SQL", "Git"],
        "important_skills": ["TypeScript", "Next.js", "Docker", "PostgreSQL", "MongoDB", "Authentication / JWT"],
        "supporting_skills": ["Tailwind CSS", "Redux", "Express.js", "CI/CD", "Unit Testing"],
        "advanced_skills": ["AWS", "Microservices", "GraphQL", "Redis Caching"],
        "tools": ["Git", "Postman", "Docker", "VS Code", "Jest"],
        "cloud_platform": ["AWS", "Vercel / Netlify", "Docker"],
        "soft_skills": ["Full Lifecycle Ownership", "Cross-functional Collaboration", "Agile Sprints"],
        "default_phase_focus": ["Modern JavaScript & React Frontend", "Backend APIs & Database Architecture", "Authentication & State Management", "Full Stack Capstone Application", "Dockerization & Cloud CI/CD", "Full Stack System Design & Live Coding"]
    },
    "frontend developer": {
        "title": "Frontend Developer",
        "description": "Building high-performance, accessible, responsive client-side web interfaces with modern reactive JavaScript frameworks.",
        "core_skills": ["HTML5", "CSS3", "JavaScript", "React", "Responsive Design", "Git", "REST API"],
        "important_skills": ["TypeScript", "Next.js", "Tailwind CSS", "State Management (Redux/Zustand)", "DOM Manipulation"],
        "supporting_skills": ["Accessibility (a11y)", "Jest / Vitest", "Webpack / Vite", "UI Design"],
        "advanced_skills": ["Web Performance Optimization", "Micro-frontends", "PWA", "GraphQL"],
        "tools": ["VS Code", "Figma", "Chrome DevTools", "npm", "Git"],
        "cloud_platform": ["Vercel", "Netlify", "AWS S3/CloudFront"],
        "soft_skills": ["Design Empathy", "Attention to Detail", "Collaborative Prototyping"],
        "default_phase_focus": ["HTML5, Modern CSS & JS Mastery", "React Components & Hooks Architecture", "TypeScript & State Management", "Interactive Portfolio Web App", "Performance, a11y & Testing", "Frontend System Architecture & Interview Prep"]
    },
    "backend developer": {
        "title": "Backend Developer",
        "description": "Server-side logic, high-throughput microservice architecture, relational & document database tuning, and API security.",
        "core_skills": ["Python", "SQL", "REST API", "PostgreSQL", "Git", "Unit Testing", "OOP"],
        "important_skills": ["FastAPI", "Docker", "Redis", "Microservices", "System Design", "Linux"],
        "supporting_skills": ["Django", "Node.js", "CI/CD", "MongoDB", "Authentication / JWT"],
        "advanced_skills": ["Kubernetes", "AWS", "Kafka / Event Streams", "gRPC", "Distributed Caching"],
        "tools": ["Postman", "Docker", "Git", "pgAdmin", "PyTest"],
        "cloud_platform": ["AWS", "Docker", "Linux"],
        "soft_skills": ["Scalability Mindset", "API Contract Design", "Security Awareness"],
        "default_phase_focus": ["Backend Frameworks & REST Standards", "Database Schema Design & Query Tuning", "Authentication, Caching & Redis", "Microservice Capstone System", "Docker, Kubernetes & AWS Deployment", "Backend System Design & Concurrency Interviews"]
    },
    "python developer": {
        "title": "Python Developer",
        "description": "Production Python application engineering, web backend services, asynchronous architecture, and database integrations.",
        "core_skills": ["Python", "Flask", "FastAPI", "SQL", "PostgreSQL", "REST API", "Git", "OOP"],
        "important_skills": ["Django", "Docker", "PyTest", "SQLAlchemy", "Unit Testing", "Data Structures & Algorithms"],
        "supporting_skills": ["Redis", "Celery", "Linux", "CI/CD", "Pandas", "Asyncio"],
        "advanced_skills": ["AWS", "Microservices", "GraphQL", "Performance Profiling"],
        "tools": ["VS Code", "Postman", "PyTest", "Docker", "Git"],
        "cloud_platform": ["AWS", "Docker", "Linux"],
        "soft_skills": ["Clean Code Practices", "Problem Solving", "Documentation"],
        "default_phase_focus": ["Advanced Python & Async Patterns", "FastAPI / Flask Microservices & ORM", "Automated Testing & SQLAlchemy Tuning", "Enterprise Python Capstone API", "Containerization & Cloud Infrastructure", "Python Architecture & System Design"]
    },
    "java developer": {
        "title": "Java Developer",
        "description": "Enterprise software engineering with Java, Spring Boot microservices, robust object-oriented architecture, and transactional databases.",
        "core_skills": ["Java", "Spring Boot", "SQL", "PostgreSQL", "REST API", "OOP", "Git", "Unit Testing"],
        "important_skills": ["Data Structures & Algorithms", "Hibernate / JPA", "Docker", "Maven / Gradle", "Microservices"],
        "supporting_skills": ["JUnit", "MySQL", "Redis", "Linux", "CI/CD"],
        "advanced_skills": ["Kubernetes", "Kafka", "AWS", "Design Patterns", "Spring Security"],
        "tools": ["IntelliJ IDEA", "Postman", "Git", "Maven", "Docker"],
        "cloud_platform": ["AWS", "Docker", "Linux"],
        "soft_skills": ["Enterprise Architecture Mindset", "Structured Problem Solving", "Team Agile Collaboration"],
        "default_phase_focus": ["Core Java & Data Structures", "Spring Boot RESTful Services & JPA", "Spring Security & Transaction Management", "Microservices Capstone Platform", "Docker & Kubernetes Deployment", "Java Concurrency, JVM & System Design"]
    },
    "javascript developer": {
        "title": "JavaScript Developer",
        "description": "Modern asynchronous JavaScript, ESNext features, browser & server execution environments, and dynamic web application engineering.",
        "core_skills": ["JavaScript", "HTML5", "CSS3", "Node.js", "REST API", "Git", "DOM Manipulation"],
        "important_skills": ["TypeScript", "React", "Express.js", "Async / Promises", "Unit Testing"],
        "supporting_skills": ["MongoDB", "PostgreSQL", "Webpack / Vite", "Jest", "Tailwind CSS"],
        "advanced_skills": ["Next.js", "Docker", "Microservices", "WebSockets"],
        "tools": ["VS Code", "npm", "Postman", "Git", "Chrome DevTools"],
        "cloud_platform": ["Vercel", "AWS", "Docker"],
        "soft_skills": ["Rapid Prototyping", "Code Modularity", "Continuous Learning"],
        "default_phase_focus": ["Deep Modern JavaScript & Async Paradigms", "Node.js Server & Express APIs", "TypeScript Integration & Testing", "Full Stack JS Interactive Project", "State Management & Production Build Tuning", "JavaScript Engine Architecture & Interview Preparation"]
    },
    "react developer": {
        "title": "React Developer",
        "description": "Specialized single-page applications, component-driven architecture, reactive state management, and modern React ecosystems.",
        "core_skills": ["React", "JavaScript", "HTML5", "CSS3", "REST API", "Git", "Responsive Design"],
        "important_skills": ["TypeScript", "Next.js", "Redux / Zustand", "Tailwind CSS", "React Hooks"],
        "supporting_skills": ["Jest / React Testing Library", "Vite", "Accessibility (a11y)", "UI Design"],
        "advanced_skills": ["Server-Side Rendering (SSR)", "GraphQL", "Micro-frontends", "Performance Profiling"],
        "tools": ["VS Code", "Figma", "React DevTools", "Git", "npm"],
        "cloud_platform": ["Vercel", "Netlify", "AWS S3"],
        "soft_skills": ["Component Thinking", "User Experience Polish", "Technical Communication"],
        "default_phase_focus": ["React Core & Custom Hooks Mastery", "TypeScript & State Architecture", "Next.js SSR & Server Components", "Production-grade SaaS Frontend", "Automated UI Testing & Performance Tuning", "Frontend System Design & Coding Interview"]
    },
    "mobile app developer": {
        "title": "Mobile App Developer",
        "description": "Cross-platform and native mobile application engineering, responsive UI for touchscreens, mobile state management, and offline data persistence.",
        "core_skills": ["Mobile Development", "React Native", "JavaScript", "TypeScript", "REST API", "Git"],
        "important_skills": ["Flutter / Dart", "Mobile UI/UX", "State Management", "Local Storage (SQLite)", "Push Notifications"],
        "supporting_skills": ["iOS / Android Tooling", "Unit Testing", "App Store / Play Store Deployment", "Authentication / JWT"],
        "advanced_skills": ["Native Bridges", "Offline First Architecture", "CI/CD for Mobile (Fastlane)", "GraphQL"],
        "tools": ["Xcode", "Android Studio", "VS Code", "Postman", "Git"],
        "cloud_platform": ["Firebase", "AWS Amplify", "App Store Connect"],
        "soft_skills": ["Mobile UX Empathy", "Device Constraint Awareness", "Performance Tuning"],
        "default_phase_focus": ["Cross-Platform Mobile Foundations", "Navigation, State & Local Storage", "Hardware Integration & Push Notifications", "Full Featured Mobile Capstone App", "Store Release Pipelines & Optimization", "Mobile Architecture & Technical Interview"]
    },
    "data analyst": {
        "title": "Data Analyst",
        "description": "Data exploration, statistical analysis, SQL querying, dashboard storytelling, and actionable business intelligence reporting.",
        "core_skills": ["SQL", "Python", "Pandas", "NumPy", "Excel", "Tableau", "Data Visualization", "Statistics"],
        "important_skills": ["Power BI", "Exploratory Data Analysis (EDA)", "Data Cleaning", "Git", "Business Analysis"],
        "supporting_skills": ["Matplotlib / Seaborn", "PostgreSQL", "ETL Pipelines", "Metrics & KPIs"],
        "advanced_skills": ["BigQuery", "Snowflake", "Scikit-Learn", "A/B Testing"],
        "tools": ["Jupyter Notebook", "Tableau", "Power BI", "Excel", "pgAdmin"],
        "cloud_platform": ["AWS QuickSight", "Google Cloud / BigQuery"],
        "soft_skills": ["Data Storytelling", "Executive Presentation", "Business Acumen"],
        "default_phase_focus": ["Advanced SQL Queries & Window Functions", "Python Data Wrangling & Pandas/NumPy", "Interactive BI Dashboards (Tableau/Power BI)", "Comprehensive Exploratory Data Analysis Project", "Automated ETL Pipelines & Reporting", "Business Case Studies & Interview Scenarios"]
    },
    "data scientist": {
        "title": "Data Scientist",
        "description": "Predictive modeling, statistical inference, feature engineering, machine learning pipelines, and translating business problems to algorithms.",
        "core_skills": ["Python", "Machine Learning", "Pandas", "NumPy", "Scikit-Learn", "SQL", "Statistics", "Exploratory Data Analysis (EDA)"],
        "important_skills": ["Deep Learning", "Data Visualization", "Feature Engineering", "Git", "Model Evaluation"],
        "supporting_skills": ["TensorFlow / PyTorch", "PostgreSQL", "Docker", "Jupyter", "A/B Testing"],
        "advanced_skills": ["MLOps", "NLP", "LLMs", "Big Data (Spark)", "Cloud (AWS/GCP)"],
        "tools": ["Jupyter", "Git", "Scikit-Learn", "Docker", "Postman"],
        "cloud_platform": ["AWS SageMaker", "GCP Vertex AI", "Google Colab"],
        "soft_skills": ["Scientific Methodology", "Hypothesis Testing", "Cross-Functional Insights"],
        "default_phase_focus": ["Applied Statistics & Advanced Python", "Machine Learning Algorithms & Feature Engineering", "Deep Learning Fundamentals & Neural Nets", "End-to-End Predictive Modeling Project", "Model Serving & Dockerized API", "Data Science Case Studies & Algorithm Interviews"]
    },
    "machine learning engineer": {
        "title": "Machine Learning Engineer",
        "description": "Developing, training, evaluating, optimizing, and deploying production machine learning models and scalable inference APIs.",
        "core_skills": ["Python", "Machine Learning", "Scikit-Learn", "NumPy", "Pandas", "Statistics", "Model Evaluation", "Git"],
        "important_skills": ["Deep Learning", "PyTorch", "TensorFlow", "FastAPI", "Docker", "REST API"],
        "supporting_skills": ["Feature Engineering", "SQL", "Linux", "Data Structures & Algorithms", "MLOps"],
        "advanced_skills": ["Model Optimization / Quantization", "AWS SageMaker", "Kubernetes", "Vector Databases"],
        "tools": ["PyTorch", "Scikit-Learn", "Docker", "Git", "Jupyter", "Postman"],
        "cloud_platform": ["AWS", "GCP", "Docker"],
        "soft_skills": ["Engineering Rigor", "Reproducible Experiments", "Collaboration with Data Scientists"],
        "default_phase_focus": ["Mathematical Foundations & Core ML Algorithms", "Deep Learning Architecture with PyTorch", "High-Throughput Model Serving via FastAPI", "Production ML Pipeline Capstone", "Docker, Cloud Inference & Monitoring", "ML System Design & Technical Interviews"]
    },
    "ai engineer": {
        "title": "AI Engineer",
        "description": "Integrating LLMs, building Retrieval-Augmented Generation (RAG) systems, autonomous agent workflows, and production AI applications.",
        "core_skills": ["Python", "Machine Learning", "Deep Learning", "Generative AI", "LLMs", "RAG", "FastAPI", "Git"],
        "important_skills": ["Vector Databases", "Prompt Engineering", "Docker", "LangChain", "Agentic AI", "Model Context Protocol (MCP)"],
        "supporting_skills": ["PyTorch", "REST API", "SQL", "NLP", "AI Guardrails / Security"],
        "advanced_skills": ["LLMOps", "LiteLLM", "Arize Tracing / Observability", "AWS / GCP"],
        "tools": ["LangChain", "LlamaIndex", "ChromaDB/Pinecone", "Docker", "Postman", "Git"],
        "cloud_platform": ["AWS", "GCP", "OpenAI / Anthropic APIs"],
        "soft_skills": ["Rapid Technological Adaptability", "AI Ethics & Safety", "Systematic Evaluation"],
        "default_phase_focus": ["Python AI Foundations & Embedding Vectors", "RAG Systems & Vector Database Indexing", "Agentic Workflows & Multi-Agent Frameworks", "Production-Ready AI Assistant Capstone", "AI Observability, Guardrails & Cloud Deployment", "AI System Design & Applied LLM Interviews"]
    },
    "generative ai engineer": {
        "title": "Generative AI Engineer",
        "description": "Specialized LLM engineering, advanced multi-stage RAG, agentic harnesses, prompt optimization, fine-tuning, and LLMOps pipelines.",
        "core_skills": ["Python", "Generative AI", "LLMs", "RAG", "Prompt Engineering", "Vector Databases", "FastAPI", "Git"],
        "important_skills": ["Agentic AI", "Model Context Protocol (MCP)", "LLMOps", "LangChain", "AI Guardrails / Security"],
        "supporting_skills": ["LiteLLM", "Arize Tracing / Observability", "Deep Learning", "NLP", "Docker"],
        "advanced_skills": ["Model Fine-Tuning (LoRA/QLoRA)", "Build GPT from Scratch", "Mesh API", "Loop / Harness Engineering"],
        "tools": ["LangChain", "LlamaIndex", "ChromaDB/Pinecone", "Docker", "Git", "LiteLLM"],
        "cloud_platform": ["AWS", "GCP", "Hugging Face"],
        "soft_skills": ["Experimentation Mindset", "Safety & Guardrail Discipline", "Clear Prompt Architecture"],
        "default_phase_focus": ["LLM Fundamentals & Transformer Attention", "Advanced Hybrid RAG with Vector Stores", "Autonomous AI Agents & MCP Integrations", "Full-Stack Generative AI Enterprise Application", "LLMOps, Security Guardrails & Evaluation", "GenAI Architecture & Frontier LLM System Design"]
    },
    "nlp engineer": {
        "title": "NLP Engineer",
        "description": "Natural language processing pipelines, tokenization, transformer architectures, text embeddings, semantic search, and classification.",
        "core_skills": ["Python", "NLP", "Transformer Architecture", "Deep Learning", "PyTorch", "Machine Learning", "Git"],
        "important_skills": ["LLMs", "Hugging Face", "Text Classification", "RAG", "FastAPI", "Vector Databases"],
        "supporting_skills": ["Scikit-Learn", "Pandas", "NumPy", "Docker", "Spacy / NLTK"],
        "advanced_skills": ["BERT / GPT Architecture", "Semantic Search", "Fine-Tuning", "Model Quantization"],
        "tools": ["Hugging Face", "PyTorch", "Docker", "Git", "Jupyter"],
        "cloud_platform": ["AWS", "GCP", "Hugging Face Hub"],
        "soft_skills": ["Linguistic Intuition", "Analytical Precision", "Iterative Tuning"],
        "default_phase_focus": ["Text Processing & Classical NLP Foundations", "Transformer Architecture & Hugging Face", "Semantic Search & Vector Embeddings", "Custom NLP Classification & Extraction System", "Model Optimization & Inference Serving", "NLP System Design & Deep Learning Interviews"]
    },
    "devops engineer": {
        "title": "DevOps Engineer",
        "description": "Continuous integration, infrastructure as code, container orchestration, cloud automation, and operational observability.",
        "core_skills": ["Linux", "Git", "Docker", "CI/CD", "Kubernetes", "AWS", "Bash / Shell"],
        "important_skills": ["Terraform", "GitHub Actions", "Python", "Networking", "Monitoring (Prometheus/Grafana)"],
        "supporting_skills": ["Ansible", "Jenkins", "Security / IAM", "PostgreSQL", "Nginx"],
        "advanced_skills": ["Helm", "Service Mesh (Istio)", "GCP / Azure", "Site Reliability Engineering (SRE)"],
        "tools": ["Docker", "Kubernetes", "Terraform", "Git", "Prometheus", "Grafana"],
        "cloud_platform": ["AWS", "GCP", "Azure", "Linux"],
        "soft_skills": ["Automation First Mentality", "Incident Calmness", "System Reliability Focus"],
        "default_phase_focus": ["Linux Administration & Shell Scripting", "Docker Multi-stage Builds & Compose", "CI/CD Pipelines with GitHub Actions", "Kubernetes Cluster Architecture & Helm", "Infrastructure as Code with Terraform on AWS", "DevOps Architecture, SRE & Incident Response"]
    },
    "cloud engineer": {
        "title": "Cloud Engineer",
        "description": "Architecting resilient, secure, and cost-optimized cloud infrastructure, identity management, networking, and serverless compute.",
        "core_skills": ["AWS", "Cloud Fundamentals", "Linux", "Networking", "Git", "IAM Security", "Bash / Shell"],
        "important_skills": ["Terraform", "Docker", "Azure", "GCP", "Python", "Compute & Storage (EC2/S3/Lambda)"],
        "supporting_skills": ["CI/CD", "Kubernetes", "Database Services (RDS/DynamoDB)", "Monitoring (CloudWatch)"],
        "advanced_skills": ["Multi-Cloud Architecture", "Cost Optimization", "Disaster Recovery", "Zero Trust Security"],
        "tools": ["AWS Console & CLI", "Terraform", "Docker", "Git", "Bash"],
        "cloud_platform": ["AWS", "Azure", "GCP"],
        "soft_skills": ["Architecture Diagramming", "Cost Awareness", "Security Compliance"],
        "default_phase_focus": ["Cloud Core Services (Compute, VPC, Storage, IAM)", "Infrastructure as Code with Terraform", "Multi-Tier Web Application on Cloud", "High Availability & Serverless Architecture", "Security, Backups & Cost Governance", "Cloud Architecture Design & Certification Style Review"]
    },
    "cybersecurity analyst": {
        "title": "Cybersecurity Analyst",
        "description": "Vulnerability assessment, security log analysis, threat modeling, network defense, authentication security, and incident response.",
        "core_skills": ["Cybersecurity Fundamentals", "Network Security", "Linux", "OWASP Security", "Authentication / JWT", "Git"],
        "important_skills": ["SIEM Tools", "Incident Response", "Vulnerability Scanning", "Python", "Bash / Shell"],
        "supporting_skills": ["Wireshark / Packet Analysis", "Cryptography Basics", "Identity & Access Management (IAM)", "Security Compliance"],
        "advanced_skills": ["Penetration Testing", "Threat Hunting", "Cloud Security", "AI Guardrails / Security"],
        "tools": ["Wireshark", "Nmap", "Burp Suite", "Splunk / SIEM", "Linux"],
        "cloud_platform": ["AWS Security Hub", "Linux Environments"],
        "soft_skills": ["Analytical Skepticism", "Discretion & Ethics", "Crisis Communication"],
        "default_phase_focus": ["Networking Protocols & Linux Defense", "OWASP Top 10 & Web Vulnerability Analysis", "SIEM Log Monitoring & Threat Detection", "Defensive Security & Incident Response Plan", "Cloud Security & Identity Hardening", "Security Architecture & Scenario-based Interviews"]
    },
    "qa / software testing engineer": {
        "title": "QA / Software Testing Engineer",
        "description": "Automated end-to-end testing, test plan creation, regression test suites, API verification, and CI/CD quality gates.",
        "core_skills": ["Unit Testing", "Test Automation", "Selenium", "Python", "REST API", "Git", "SQL"],
        "important_skills": ["Playwright", "Postman", "PyTest", "CI/CD", "Test Case Design"],
        "supporting_skills": ["Jira", "Performance Testing", "JavaScript / Cypress", "Bug Reporting"],
        "advanced_skills": ["Load Testing (JMeter/Locust)", "Docker", "Security Testing", "BDD (Behave/Cucumber)"],
        "tools": ["Postman", "Selenium", "Playwright", "PyTest", "Git", "Jira"],
        "cloud_platform": ["GitHub Actions", "Docker", "BrowserStack"],
        "soft_skills": ["Methodical Rigor", "Defect Communication", "Quality Advocacy"],
        "default_phase_focus": ["Testing Principles & Manual Test Design", "API Testing with Postman & PyTest", "Web UI Test Automation with Playwright/Selenium", "End-to-End Automated Test Framework", "CI/CD Test Pipeline Integration", "QA Automation Architecture & Interview Prep"]
    },
    "database developer / dba": {
        "title": "Database Developer / DBA",
        "description": "Database schema modeling, complex SQL queries, index optimization, backup strategies, high availability, and replication.",
        "core_skills": ["SQL", "PostgreSQL", "MySQL", "Database Administration", "Database Indexing", "Query Optimization", "Git"],
        "important_skills": ["Database Normalization", "Stored Procedures / Triggers", "Backup & Recovery", "Linux", "Python"],
        "supporting_skills": ["NoSQL", "MongoDB", "Redis", "Data Modeling", "ETL Pipelines"],
        "advanced_skills": ["Replication & Sharding", "Cloud Databases (RDS/Aurora)", "Performance Profiling", "Security & Auditing"],
        "tools": ["pgAdmin", "MySQL Workbench", "DBeaver", "Git", "Bash"],
        "cloud_platform": ["AWS RDS", "PostgreSQL", "Linux"],
        "soft_skills": ["Data Integrity Mindset", "Zero-Downtime Planning", "Performance Troubleshooting"],
        "default_phase_focus": ["Advanced Relational Theory & SQL Indexing", "Database Administration, Backups & Security", "Stored Procedures, Triggers & Partitioning", "High Availability & Replication Setup", "Performance Tuning & Slow Query Optimization", "Database Architecture & DBA Scenario Interviews"]
    },
    "ui/ux designer": {
        "title": "UI/UX Designer",
        "description": "User research, wireframing, interactive prototyping, design systems, usability testing, and accessible visual interfaces.",
        "core_skills": ["Figma", "UI Design", "UX Research", "Wireframing", "Prototyping", "Design Systems"],
        "important_skills": ["Accessibility (a11y)", "User Testing", "Responsive Design", "HTML5", "CSS3"],
        "supporting_skills": ["Information Architecture", "User Personas", "Visual Hierarchy", "Design Tokens"],
        "advanced_skills": ["Design System Governance", "Micro-animations", "Frontend Collaboration", "Design Strategy"],
        "tools": ["Figma", "FigJam", "Adobe XD", "Miro", "Chrome DevTools"],
        "cloud_platform": ["Figma Cloud", "Zeroheight"],
        "soft_skills": ["User Empathy", "Visual Communication", "Design Critique & Rationale"],
        "default_phase_focus": ["UX Research & Information Architecture", "Wireframing & Visual Hierarchy", "Advanced Figma Components & Design Systems", "Comprehensive Product Case Study & Prototype", "Accessibility & Usability Testing", "Design Portfolio Presentation & Interview Defense"]
    },
    "business analyst": {
        "title": "Business Analyst",
        "description": "Translating stakeholder business needs into functional technical specifications, process mapping, SQL insights, and agile delivery.",
        "core_skills": ["Business Analysis", "Requirements Gathering", "SQL", "Agile / Scrum", "Data Analysis", "Excel"],
        "important_skills": ["Process Mapping", "User Stories & Acceptance Criteria", "Tableau", "Jira", "Data Visualization"],
        "supporting_skills": ["Power BI", "Stakeholder Management", "Python Basics", "System Design Basics"],
        "advanced_skills": ["Financial Modeling", "ETL Awareness", "Gap Analysis", "Product Management Basics"],
        "tools": ["Jira", "Confluence", "Excel", "Tableau", "Draw.io / Lucidchart"],
        "cloud_platform": ["Atlassian Cloud", "Tableau Online"],
        "soft_skills": ["Stakeholder Negotiation", "Requirement Clarity", "Executive Presentation"],
        "default_phase_focus": ["Requirements Gathering & User Story Formulation", "SQL for Business Data Exploration", "Process Mapping & Flowcharts", "End-to-End Business Requirement Document (BRD)", "Dashboard KPIs & Acceptance Validation", "Business Analyst Case Study & Stakeholder Interviews"]
    },
    "system administrator": {
        "title": "System Administrator",
        "description": "Server operating systems, network configuration, user identity management, backup strategies, patch maintenance, and shell automation.",
        "core_skills": ["Linux", "Bash / Shell", "Networking", "System Administration", "Git", "Security Basics"],
        "important_skills": ["User Management / LDAP / AD", "SSH / Key Management", "Virtualization / Docker", "Python Scripting", "Backup Strategies"],
        "supporting_skills": ["Nginx / Apache", "Firewalls (iptables/ufw)", "Monitoring (Prometheus/Nagios)", "Storage Management"],
        "advanced_skills": ["Ansible Automation", "Cloud Infrastructure (AWS)", "Disaster Recovery", "Zero Trust"],
        "tools": ["Linux CLI", "Bash", "SSH", "Docker", "Git"],
        "cloud_platform": ["Linux", "AWS", "VMware"],
        "soft_skills": ["Operational Resilience", "Systematic Troubleshooting", "Disaster Readiness"],
        "default_phase_focus": ["Linux Kernel & System Administration Core", "Networking Protocols, DNS & Firewalls", "Bash Automation & Python Administration", "Automated Backup & Server Hardening", "Dockerization & Virtual Infrastructure", "SysAdmin Troubleshooting & Incident Scenarios"]
    },
    "mlops engineer": {
        "title": "MLOps Engineer",
        "description": "Building continuous machine learning deployment pipelines, model tracking, feature stores, container orchestration, and drift monitoring.",
        "core_skills": ["Python", "MLOps", "Docker", "Machine Learning", "CI/CD", "Git", "FastAPI"],
        "important_skills": ["Kubernetes", "Linux", "Model Evaluation", "Cloud (AWS/GCP)", "LLMOps", "Arize Tracing / Observability"],
        "supporting_skills": ["SQL", "PyTorch / Scikit-Learn", "Terraform", "Monitoring (Prometheus)"],
        "advanced_skills": ["Feature Stores (Feast)", "Model Registry & Drift Detection", "Automated Retraining Pipelines", "GPU Optimization"],
        "tools": ["Docker", "Kubernetes", "MLflow", "GitHub Actions", "Git", "FastAPI"],
        "cloud_platform": ["AWS SageMaker", "GCP Vertex AI", "Docker"],
        "soft_skills": ["Cross-Discipline Bridge (Data Science + DevOps)", "Production Reliability", "Observability Mindset"],
        "default_phase_focus": ["ML Pipeline Fundamentals & Reproducibility", "Containerization & FastAPI Serving", "CI/CD for ML Models with GitHub Actions", "Model Registry, Drift Monitoring & Tracing", "Kubernetes Inference Deployment & Scaling", "MLOps System Architecture & Production Interviews"]
    },
    "ai/ml research engineer": {
        "title": "AI/ML Research Engineer",
        "description": "Researching novel neural architectures, benchmarking state-of-the-art models, mathematical derivation, and implementing frontier AI papers.",
        "core_skills": ["Python", "PyTorch", "Deep Learning", "Machine Learning", "Mathematics & Statistics", "Git", "Model Evaluation"],
        "important_skills": ["Transformer Architecture", "Build GPT from Scratch", "NLP", "Computer Vision", "Research Paper Implementation"],
        "supporting_skills": ["Scikit-Learn", "NumPy", "TensorFlow", "FastAPI", "Linux"],
        "advanced_skills": ["Distributed Training (DeepSpeed/Megatron)", "Custom CUDA Kernels", "Model Quantization & Pruning", "Generative AI"],
        "tools": ["PyTorch", "Jupyter", "Hugging Face", "Git", "Weights & Biases"],
        "cloud_platform": ["GPU Clusters", "AWS", "Google Colab Pro"],
        "soft_skills": ["Scientific Rigor", "Academic Paper Analysis", "Mathematical Intuition"],
        "default_phase_focus": ["Advanced Linear Algebra & Deep Learning Theory", "PyTorch Custom Layers & Optimization", "Transformer Architecture & Attention Mechanisms", "Frontier Paper Replication & Novel Architecture", "Distributed Multi-GPU Training & Benchmarking", "AI Research Defense & Technical Algorithm Interviews"]
    }
}

# =====================================================================
# 5. PRACTICAL TASKS & PROJECT IDEAS PER SKILL
# =====================================================================

SKILL_PRACTICAL_KNOWLEDGE: Dict[str, Dict[str, Any]] = {
    "python": {
        "difficulty": "Beginner",
        "est_hours": "6-12 hours",
        "why_matters": "Fundamental language for backend engineering, data science, AI pipelines, and enterprise automation.",
        "practice_task": "Write an asynchronous script using aiohttp to fetch and parse data from 5 REST API endpoints concurrently with error handling.",
        "project_idea": "Build a modular CLI & RESTful API service with Python and SQLite implementing full CRUD operations and logging.",
        "why_project": "Demonstrates mastery of modern Python object-oriented architecture, modular package design, and clean data processing.",
        "curated_key": "python"
    },
    "javascript": {
        "difficulty": "Beginner to Intermediate",
        "est_hours": "6-10 hours",
        "why_matters": "Universal programming language powering client-side web interactions, server-side Node.js, and modern full stack ecosystems.",
        "practice_task": "Create an interactive dashboard widget with vanilla JavaScript that performs asynchronous fetch, debounce filtering, and dynamic DOM updates.",
        "project_idea": "Develop a real-time event log viewer with search filters, local storage caching, and responsive UI components.",
        "why_project": "Proves deep understanding of asynchronous JavaScript, event loops, DOM performance, and clean component modularity."
    },
    "react": {
        "difficulty": "Intermediate",
        "est_hours": "8-16 hours",
        "why_matters": "Industry-standard component library for crafting declarative, reactive, high-performance web user interfaces.",
        "practice_task": "Build a reusable data table component with sorting, pagination, and multi-field search using React custom hooks and state.",
        "project_idea": "Create an interactive Candidate Analytics Dashboard with animated charts, dark mode, and REST API integration.",
        "why_project": "Highlights professional competence in component lifecycles, custom hook abstraction, performance optimization, and responsive design."
    },
    "typescript": {
        "difficulty": "Intermediate",
        "est_hours": "6-12 hours",
        "why_matters": "Adds compile-time type safety to JavaScript, drastically reducing runtime bugs in large-scale production codebases.",
        "practice_task": "Convert a standard JavaScript REST client to strict TypeScript with comprehensive interfaces, generic response wrappers, and union types.",
        "project_idea": "Build a type-safe task management Kanban board with drag-and-drop state validation in TypeScript and React.",
        "why_project": "Demonstrates enterprise-level code quality, static typing proficiency, and maintainable software architecture."
    },
    "fastapi": {
        "difficulty": "Intermediate",
        "est_hours": "6-12 hours",
        "why_matters": "High-performance, modern Python web framework based on standard type hints and OpenAPI, ideal for microservices and AI APIs.",
        "practice_task": "Create a secure FastAPI endpoint with Pydantic request validation, API key dependency injection, and automatic Swagger docs.",
        "project_idea": "Build an AI Model Inference API with rate limiting, background tasks, and structured error responses.",
        "why_project": "Proves readiness to engineer production-ready microservices adhering to modern OpenAPI specifications.",
        "curated_key": "fastapi"
    },
    "flask": {
        "difficulty": "Beginner to Intermediate",
        "est_hours": "5-10 hours",
        "why_matters": "Lightweight, flexible Python WSGI framework widely used for modular microservices, enterprise dashboards, and rapid backend development.",
        "practice_task": "Refactor a monolithic Flask application into modular Blueprints with centralized error handling and CSRF protection.",
        "project_idea": "Build a Resume & Portfolio Management Portal with user authentication, SQLAlchemy database ORM, and file uploads.",
        "why_project": "Demonstrates mastery of the Application Factory pattern, database transactions, and secure web application development."
    },
    "django": {
        "difficulty": "Intermediate",
        "est_hours": "10-18 hours",
        "why_matters": "Full-featured Python web framework providing built-in ORM, admin interfaces, authentication, and security protections for rapid enterprise scaling.",
        "practice_task": "Build a customized Django admin portal with relational query filters and model actions for user account management.",
        "project_idea": "Develop a multi-tenant corporate job portal with role-based access control, PostgreSQL backend, and REST framework APIs.",
        "why_project": "Showcases proficiency with batteries-included enterprise frameworks, database migrations, and complex authorization."
    },
    "spring boot": {
        "difficulty": "Intermediate to Advanced",
        "est_hours": "12-24 hours",
        "why_matters": "Dominant enterprise Java framework for building robust, decoupled, cloud-ready microservices and transactional systems.",
        "practice_task": "Implement a Spring Boot REST controller with Spring Data JPA repository queries, custom exception handlers, and Bean Validation.",
        "project_idea": "Engineer an enterprise inventory microservice with PostgreSQL persistence, JWT security, and Docker containerization.",
        "why_project": "Demonstrates mastery of Java enterprise architecture, dependency injection, JPA ORM, and secure API design."
    },
    "sql": {
        "difficulty": "Beginner to Intermediate",
        "est_hours": "5-10 hours",
        "why_matters": "Foundational language for querying, transforming, and managing relational databases across almost all engineering and data roles.",
        "practice_task": "Write complex SQL queries utilizing INNER/LEFT JOINs, GROUP BY aggregations, window functions (ROW_NUMBER/RANK), and CTEs on a sample sales schema.",
        "project_idea": "Design and populate a normalized relational database for an e-commerce platform with analytical reporting views.",
        "why_project": "Proves strong analytical capability, understanding of relational integrity, and optimization of business-critical queries."
    },
    "postgresql": {
        "difficulty": "Intermediate",
        "est_hours": "6-12 hours",
        "why_matters": "Advanced, highly extensible open-source object-relational database standard for production backend and AI vector applications.",
        "practice_task": "Create custom indexes (B-Tree, GIN) and analyze query execution plans with EXPLAIN ANALYZE to optimize a slow query.",
        "project_idea": "Build a high-performance transactional database backend with JSONB indexing and automated daily backup scripts.",
        "why_project": "Demonstrates deep database administration knowledge, indexing strategies, and relational performance tuning."
    },
    "docker": {
        "difficulty": "Intermediate",
        "est_hours": "4-8 hours",
        "why_matters": "Industry standard for packaging applications with all dependencies into immutable, portable containers for predictable deployment.",
        "practice_task": "Write a production multi-stage Dockerfile for a Python/Node.js web application reducing image size to under 150MB.",
        "project_idea": "Set up a complete multi-container Docker Compose environment featuring a web backend, PostgreSQL database, and Redis cache.",
        "why_project": "Proves ability to eliminate 'works on my machine' issues and standardize development and deployment environments."
    },
    "kubernetes": {
        "difficulty": "Advanced",
        "est_hours": "12-25+ hours",
        "why_matters": "Standard container orchestration system for automating application deployment, scaling, rolling updates, and self-healing in cloud infrastructure.",
        "practice_task": "Write Kubernetes Deployment, Service, and Ingress manifests with resource limits and readiness/liveness health probes.",
        "project_idea": "Deploy a containerized microservice cluster with Horizontal Pod Autoscaling (HPA) and automated rolling zero-downtime updates.",
        "why_project": "Highlights advanced cloud-native infrastructure competency, container orchestration, and high-availability architecture."
    },
    "git": {
        "difficulty": "Beginner",
        "est_hours": "3-6 hours",
        "why_matters": "Essential distributed version control system required for all collaborative software engineering and CI/CD pipelines.",
        "practice_task": "Simulate a Git feature branch workflow including branching, rebasing, resolving a merge conflict, and creating a structured pull request.",
        "project_idea": "Configure a GitHub repository with branch protection rules, semantic version tags, and automated PR quality check workflows.",
        "why_project": "Demonstrates professional version control discipline, clean commit history management, and team collaboration readiness."
    },
    "ci/cd": {
        "difficulty": "Intermediate",
        "est_hours": "4-8 hours",
        "why_matters": "Automates testing, linting, building, and deploying code on every push, ensuring software quality and rapid iteration.",
        "practice_task": "Create a GitHub Actions workflow that automatically executes linting, unit test suites, and Docker image builds on every pull request.",
        "project_idea": "Engineer an automated Continuous Deployment pipeline that tests and deploys a web application to a staging server upon merging to main.",
        "why_project": "Showcases modern DevOps lifecycle skills, test automation enforcement, and zero-touch deployment capability."
    },
    "aws": {
        "difficulty": "Intermediate to Advanced",
        "est_hours": "10-20 hours",
        "why_matters": "World's most widely adopted cloud platform powering compute, storage, databases, and enterprise AI infrastructure.",
        "practice_task": "Deploy a containerized application to AWS ECS/EC2 connected to an RDS PostgreSQL database with IAM role security and security group rules.",
        "project_idea": "Architect a scalable, serverless image processing pipeline using AWS S3 triggers, Lambda functions, and DynamoDB.",
        "why_project": "Proves ability to architect secure, scalable, highly available enterprise cloud solutions on industry-leading infrastructure.",
        "curated_key": "aws zero to hero"
    },
    "gcp": {
        "difficulty": "Intermediate",
        "est_hours": "8-16 hours",
        "why_matters": "Leading cloud platform renowned for data analytics, BigQuery, Kubernetes (GKE), and frontier AI model hosting.",
        "practice_task": "Deploy a containerized service to Google Cloud Run with custom domain mapping and Cloud Secret Manager integration.",
        "project_idea": "Build a serverless data ingestion pipeline streaming records into Google BigQuery with automated dashboard visualizations.",
        "why_project": "Demonstrates versatility across cloud providers with expertise in Google Cloud's serverless and analytics toolchain.",
        "curated_key": "gcp zero to hero"
    },
    "azure": {
        "difficulty": "Intermediate",
        "est_hours": "8-16 hours",
        "why_matters": "Primary enterprise cloud platform widely utilized across corporate IT, OpenAI service hosting, and hybrid infrastructure.",
        "practice_task": "Configure an Azure App Service with Azure SQL Database connection string secrets managed via Azure Key Vault.",
        "project_idea": "Deploy an enterprise AI application integrating Azure OpenAI Services with role-based Azure AD authentication.",
        "why_project": "Validates enterprise readiness in deploying secure Microsoft Azure infrastructure for corporate environments.",
        "curated_key": "azure zero to hero"
    },
    "machine learning": {
        "difficulty": "Intermediate",
        "est_hours": "10-20 hours",
        "why_matters": "Core predictive analytics capability transforming historical data into automated classification, regression, and ranking models.",
        "practice_task": "Train a Random Forest classifier on tabular data with Scikit-Learn, performing hyperparameter tuning via GridSearchCV and calculating ROC-AUC.",
        "project_idea": "Develop a Customer Churn Prediction & Risk Scoring system with feature importance analysis and a REST API scoring endpoint.",
        "why_project": "Demonstrates full ML lifecycle understanding from data preprocessing and cross-validation to production inference.",
        "curated_key": "machine learning"
    },
    "deep learning": {
        "difficulty": "Advanced",
        "est_hours": "12-25+ hours",
        "why_matters": "Powers computer vision, speech processing, generative models, and complex unstructured data representations using deep neural networks.",
        "practice_task": "Implement a Convolutional Neural Network (CNN) or multi-layer perceptron in PyTorch with custom loss functions and learning rate schedulers.",
        "project_idea": "Build an Image Classification & Defect Detection model using PyTorch with transfer learning on a pretrained ResNet backbone.",
        "why_project": "Proves deep understanding of backpropagation, tensor operations, neural layer design, and GPU model training.",
        "curated_key": "deep learning"
    },
    "generative ai": {
        "difficulty": "Intermediate to Advanced",
        "est_hours": "10-20 hours",
        "why_matters": "Next-generation AI paradigm revolutionizing software, content synthesis, automated reasoning, and natural language interfaces.",
        "practice_task": "Build a structured JSON extraction pipeline using OpenAI/Anthropic SDKs with strict JSON schemas and system prompts.",
        "project_idea": "Develop an Intelligent Document Synthesizer that ingests complex PDF reports and generates executive summaries and SWOT matrices.",
        "why_project": "Showcases modern GenAI application engineering, prompt design, and practical LLM integration skills.",
        "curated_key": "generative ai"
    },
    "rag": {
        "difficulty": "Intermediate to Advanced",
        "est_hours": "8-16 hours",
        "why_matters": "Grounds LLM responses in proprietary private documents, eliminating hallucinations and enabling accurate domain knowledge retrieval.",
        "practice_task": "Implement a chunking and embedding pipeline using LangChain/LlamaIndex that stores text embeddings in a local vector database.",
        "project_idea": "Build an Enterprise Policy Q&A Assistant that answers employee questions with exact source citations from internal PDF handbooks.",
        "why_project": "Highlights mastery of semantic search, chunking strategies, vector database retrieval, and context-augmented generation.",
        "curated_key": "rag"
    },
    "agentic ai": {
        "difficulty": "Advanced",
        "est_hours": "10-20 hours",
        "why_matters": "Enables LLMs to autonomously plan, use external tools, execute code, and collaborate in multi-agent workflows to solve complex goals.",
        "practice_task": "Construct a two-agent workflow where an AI Researcher gathers information and an AI Editor formats the output into a technical brief.",
        "project_idea": "Create an Autonomous Competitive Intelligence Agent that browses web content, synthesizes market trends, and outputs a formatted report.",
        "why_project": "Demonstrates leading-edge capability in autonomous agent harness engineering, tool integration, and multi-step reasoning.",
        "curated_key": "agentic ai"
    },
    "llmops": {
        "difficulty": "Advanced",
        "est_hours": "8-16 hours",
        "why_matters": "Operationalizing LLMs in production: tracking token latency, evaluation metrics, guardrail enforcement, and continuous model observability.",
        "practice_task": "Instrument an LLM API endpoint with prompt latency tracing, token cost monitoring, and fallback routing using LiteLLM.",
        "project_idea": "Build an LLM Evaluation & Guardrail Gateway that checks prompt safety, scans for PII, and logs response quality benchmarks.",
        "why_project": "Validates enterprise readiness in managing cost, safety, and reliability for production Generative AI deployments.",
        "curated_key": "llmops"
    },
    "data structures & algorithms": {
        "difficulty": "Intermediate",
        "est_hours": "10-25+ hours",
        "why_matters": "Essential foundation for efficient software development, algorithmic complexity analysis, and technical coding interviews.",
        "practice_task": "Implement a balanced Binary Search Tree or LRU Cache data structure from scratch with O(1) lookups and eviction logic.",
        "project_idea": "Build an in-memory Graph Pathfinding visualizer implementing Dijkstra's and A* search algorithms.",
        "why_project": "Proves strong computational thinking, time/space complexity optimization (Big-O), and algorithmic mastery."
    },
    "system design": {
        "difficulty": "Advanced",
        "est_hours": "12-25+ hours",
        "why_matters": "Architecting large-scale distributed systems that handle millions of requests, database scaling, caching, and fault tolerance.",
        "practice_task": "Draft an architectural diagram and API contract for a high-volume URL Shortener system with rate limiting and Redis caching.",
        "project_idea": "Design and simulate an event-driven Notification Dispatcher handling thousands of concurrent push notifications via message queues.",
        "why_project": "Demonstrates senior-level engineering maturity in handling tradeoffs, data partitioning, caching, and resiliency."
    },
    "cybersecurity fundamentals": {
        "difficulty": "Intermediate",
        "est_hours": "6-14 hours",
        "why_matters": "Protecting systems, APIs, and data against injection attacks, authentication bypasses, unauthorized data exposure, and threats.",
        "practice_task": "Audit a sample web application for OWASP Top 10 vulnerabilities (SQL Injection, XSS, CSRF) and write remediation patches.",
        "project_idea": "Build a Centralized Security Audit Logger that monitors failed authentication attempts and triggers automated IP rate limits.",
        "why_project": "Proves deep commitment to secure coding practices, vulnerability remediation, and protective defense mechanisms."
    },
    "figma": {
        "difficulty": "Beginner to Intermediate",
        "est_hours": "6-12 hours",
        "why_matters": "Industry-standard collaborative interface design and prototyping tool for modern digital product and UI/UX design teams.",
        "practice_task": "Create a responsive, accessible navigation bar and card component in Figma utilizing Auto Layout, Component Variants, and Design Tokens.",
        "project_idea": "Design an end-to-end interactive mobile app prototype for a Career Mentorship Platform with high-fidelity transitions.",
        "why_project": "Showcases visual design polish, design system governance, and interactive prototype storytelling."
    },
    "unit testing": {
        "difficulty": "Beginner to Intermediate",
        "est_hours": "4-8 hours",
        "why_matters": "Ensures software correctness, prevents regressions, and enables confident refactoring through automated test verification.",
        "practice_task": "Write comprehensive unit test suites with PyTest or Jest achieving 90%+ branch coverage with mocks and fixtures.",
        "project_idea": "Implement automated regression test suites and parameterized edge-case testing for a financial calculation engine.",
        "why_project": "Demonstrates high engineering standards, test-driven mindset, and reliable software delivery."
    }
}

# =====================================================================
# 6. RESOLVER FUNCTIONS & ENGINE CORE
# =====================================================================

def normalize_skill_name(raw_name: str) -> str:
    """Normalizes skill aliases to canonical title-cased names."""
    cleaned = raw_name.strip().lower()
    if cleaned in SKILL_ALIASES:
        return SKILL_ALIASES[cleaned]
    # Return formatted skill
    return raw_name.strip().title() if len(raw_name.strip()) > 3 else raw_name.strip().upper()


def get_role_configuration(target_role: str) -> Dict[str, Any]:
    """Retrieves or creates matching role matrix configuration for any of the 25 job roles."""
    role_clean = target_role.strip().lower()
    
    # 1. Exact match
    if role_clean in ROLE_MATRICES:
        return ROLE_MATRICES[role_clean]

    # 2. Match with normalized keys sorted by descending length (e.g. 'generative ai engineer' before 'ai engineer')
    sorted_keys = sorted(ROLE_MATRICES.keys(), key=len, reverse=True)
    for key in sorted_keys:
        if key == role_clean or key in role_clean or role_clean in key:
            return ROLE_MATRICES[key]
            
    # Default fallback to Software Developer
    return ROLE_MATRICES["software developer"]


def generate_safe_youtube_search_url(skill: str, language: str = "English") -> str:
    """Generates a 100% safe, non-hallucinated YouTube search query URL with proper URL encoding."""
    query = f"{skill} full tutorial {language}".strip()
    encoded_query = urllib.parse.quote_plus(query)
    return f"https://www.youtube.com/results?search_query={encoded_query}"


def resolve_skill_learning_resources(skill_name: str, target_role: str) -> Dict[str, Any]:
    """
    Finds exact curated library URL or safe verified fallback for both English and Hinglish/Hindi.
    NEVER fabricates or invents fake video IDs.
    """
    skill_lower = skill_name.strip().lower()
    meta = SKILL_PRACTICAL_KNOWLEDGE.get(skill_lower, {})
    
    # Check if skill matches a curated library key
    english_resource = None
    curated_key = meta.get("curated_key")
    if curated_key and curated_key in CURATED_LEARNING_LIBRARY:
        res = CURATED_LEARNING_LIBRARY[curated_key]
        english_resource = {
            "title": res["title"],
            "url": res["url"],
            "type": res["format"],
            "is_curated": True
        }
    else:
        # Check direct lookup in curated library
        for c_key, c_val in CURATED_LEARNING_LIBRARY.items():
            if c_key in skill_lower or skill_lower in c_key:
                english_resource = {
                    "title": c_val["title"],
                    "url": c_val["url"],
                    "type": c_val["format"],
                    "is_curated": True
                }
                break

    # If no curated match, provide safe search fallback
    if not english_resource:
        english_resource = {
            "title": f"{skill_name} Comprehensive Guide & Masterclass",
            "url": generate_safe_youtube_search_url(skill_name, "English"),
            "type": "Verified Search Tutorial",
            "is_curated": False
        }

    # Hinglish / Hindi Resource (Safe fallback)
    hinglish_resource = {
        "title": f"{skill_name} Tutorial in Hinglish / Hindi",
        "url": generate_safe_youtube_search_url(skill_name, "Hinglish"),
        "type": "Hinglish Masterclass Search",
        "is_curated": False
    }

    difficulty = meta.get("difficulty", "Intermediate")
    est_hours = meta.get("est_hours", "6-12 hours")
    why_matters = meta.get("why_matters", f"Crucial competency for modern {target_role} positions to handle production workloads.")
    practice_task = meta.get("practice_task", f"Build a practical hands-on module applying {skill_name} with error handling and documentation.")
    project_idea = meta.get("project_idea", f"Develop a capstone feature demonstrating {skill_name} integration in a real-world application.")
    why_project = meta.get("why_project", f"Proves practical capability in {skill_name} and strengthens your portfolio for {target_role} roles.")

    return {
        "skill": skill_name,
        "difficulty": difficulty,
        "estimated_time": est_hours,
        "why_matters": why_matters,
        "english_resource": english_resource,
        "hinglish_resource": hinglish_resource,
        "practice_task": practice_task,
        "project_idea": project_idea,
        "why_project": why_project
    }


def analyze_skills_against_role(resume_text: str, target_role: str, job_description: str = "") -> Dict[str, Any]:
    """
    Performs deterministic, role-aware skill comparison distinguishing:
    - ROLE REQUIRED
    - JD REQUIRED
    - MATCHED SKILLS
    - WEAK SKILLS
    - MISSING SKILLS
    """
    role_config = get_role_configuration(target_role)
    resume_lower = resume_text.lower()
    jd_lower = job_description.lower() if job_description else ""

    # Compile candidate detected skills
    detected_skills_set = set()
    for alias_key, canonical_name in SKILL_ALIASES.items():
        pattern = r'(?:\b|_)' + re.escape(alias_key) + r'(?:\b|_)'
        if re.search(pattern, resume_lower):
            detected_skills_set.add(canonical_name)

    # Required role skills
    core_role_skills = [normalize_skill_name(s) for s in role_config.get("core_skills", [])]
    important_role_skills = [normalize_skill_name(s) for s in role_config.get("important_skills", [])]
    supporting_role_skills = [normalize_skill_name(s) for s in role_config.get("supporting_skills", [])]
    all_role_target_skills = list(dict.fromkeys(core_role_skills + important_role_skills + supporting_role_skills[:3]))

    # JD required skills
    jd_target_skills = []
    if jd_lower:
        for alias_key, canonical_name in SKILL_ALIASES.items():
            pattern = r'(?:\b|_)' + re.escape(alias_key) + r'(?:\b|_)'
            if re.search(pattern, jd_lower):
                if canonical_name not in jd_target_skills:
                    jd_target_skills.append(canonical_name)

    # Priority blend: JD skills take precedence when present
    combined_target_skills = list(dict.fromkeys(jd_target_skills + all_role_target_skills))

    matched_skills = []
    weak_skills = []
    missing_skills = []

    for req_skill in combined_target_skills:
        req_clean = req_skill.lower()
        # Find if skill is in detected skills or directly in resume text
        is_detected = (req_skill in detected_skills_set) or bool(re.search(r'(?:\b|_)' + re.escape(req_clean) + r'(?:\b|_)', resume_lower))
        
        if is_detected:
            # Check depth: If mentioned only once briefly or without metrics/projects, flag as weak
            matches_count = len(re.findall(r'(?:\b|_)' + re.escape(req_clean) + r'(?:\b|_)', resume_lower))
            has_project_evidence = bool(re.search(r'(project|experience|developed|engineered|built|deployed).{0,100}' + re.escape(req_clean), resume_lower)) or bool(re.search(re.escape(req_clean) + r'.{0,100}(project|experience|developed|engineered|built)', resume_lower))
            
            if matches_count == 1 and not has_project_evidence and len(matched_skills) >= 4:
                weak_skills.append(req_skill)
            else:
                matched_skills.append(req_skill)
        else:
            missing_skills.append(req_skill)

    # Ensure uniqueness
    matched_skills = list(dict.fromkeys(matched_skills))
    weak_skills = list(dict.fromkeys(weak_skills))
    missing_skills = list(dict.fromkeys(missing_skills))

    # Generate personalized learning plan cards for missing & weak skills
    prioritized_gap_skills = missing_skills[:6] + weak_skills[:3]
    if not prioritized_gap_skills:
        prioritized_gap_skills = core_role_skills[:4]

    learning_resources = [
        resolve_skill_learning_resources(skill, role_config["title"])
        for skill in prioritized_gap_skills
    ]

    # Generate customized 6-phase career roadmap
    roadmap_phases = []
    phase_titles = [
        "Phase 1 — Fundamentals & Architecture",
        "Phase 2 — Core Technologies & APIs",
        "Phase 3 — Advanced Tooling & Scale",
        "Phase 4 — Capstone Project & Portfolio",
        "Phase 5 — Cloud Infrastructure & CI/CD",
        "Phase 6 — Interview Mastery & System Design"
    ]

    # Map available gap skills into phases
    for idx, title in enumerate(phase_titles):
        phase_skill = prioritized_gap_skills[idx % len(prioritized_gap_skills)] if prioritized_gap_skills else "Core Architecture"
        res_info = resolve_skill_learning_resources(phase_skill, role_config["title"])
        
        roadmap_phases.append({
            "phase": f"Phase {idx + 1}",
            "order": title,
            "skill": phase_skill,
            "why": res_info["why_matters"],
            "time_estimate": res_info["estimated_time"],
            "difficulty": res_info["difficulty"],
            "practice_task": res_info["practice_task"],
            "project_idea": res_info["project_idea"],
            "english_url": res_info["english_resource"]["url"],
            "hinglish_url": res_info["hinglish_resource"]["url"]
        })

    return {
        "target_role": role_config["title"],
        "role_description": role_config["description"],
        "matched_skills": matched_skills,
        "weak_skills": weak_skills,
        "missing_skills": missing_skills,
        "jd_required_skills": jd_target_skills,
        "role_required_skills": core_role_skills + important_role_skills,
        "learning_resources": learning_resources,
        "learning_roadmap": roadmap_phases
    }
