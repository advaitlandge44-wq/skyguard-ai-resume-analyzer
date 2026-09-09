import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env
load_dotenv(BASE_DIR / '.env')


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default-dev-secret-key-replace-in-production'
    
    # Database
    instance_dir = BASE_DIR / 'instance'
    os.makedirs(instance_dir, exist_ok=True)
    db_path = instance_dir / 'skyguard.db'
    
    env_db = os.environ.get('DATABASE_URL')
    if env_db and not env_db.startswith('sqlite:///instance/'):
        SQLALCHEMY_DATABASE_URI = env_db
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path.resolve()}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or str(BASE_DIR / 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 5 * 1024 * 1024))  # 5 MB
    ALLOWED_EXTENSIONS = {'pdf', 'txt'}
    ALLOWED_MIME_TYPES = {'application/pdf', 'text/plain', 'application/octet-stream'}

    # OpenAI
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '').strip()
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')

    # Security & Sessions
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() in ['true', '1', 't']
    PERMANENT_SESSION_LIFETIME = 86400 * 7  # 7 days

    # CORS & Frontend Origins
    FRONTEND_URL = os.environ.get('FRONTEND_URL', '').rstrip('/')
    cors_env = os.environ.get('CORS_ORIGINS', '')
    if cors_env:
        CORS_ORIGINS = [origin.strip() for origin in cors_env.split(',') if origin.strip()]
    else:
        # Default development & preview origins
        CORS_ORIGINS = [
            'http://localhost:3000',
            'http://127.0.0.1:3000',
            'http://localhost:5000',
            'http://127.0.0.1:5000',
            'http://localhost:5500',
            'http://127.0.0.1:5500',
            'http://localhost:8080',
            'http://127.0.0.1:8080',
            'https://*.vercel.app'
        ]
        if FRONTEND_URL and FRONTEND_URL not in CORS_ORIGINS:
            CORS_ORIGINS.append(FRONTEND_URL)

    # Rate Limiting
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', "100 per minute")
    RATELIMIT_STORAGE_URI = "memory://"

    # Email / SMTP Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or os.environ.get('MAIL_FROM') or 'noreply@skyguard.ai'
    MAIL_RESET_TOKEN_EXPIRATION_SECONDS = int(os.environ.get('MAIL_RESET_TOKEN_EXPIRATION_SECONDS', 3600))


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False
    UPLOAD_FOLDER = str(BASE_DIR / 'uploads_test')


class ProductionConfig(Config):
    """Production configuration for Render."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    # For cross-site cookie exchange between Vercel and Render in HTTPS
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'None')


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
