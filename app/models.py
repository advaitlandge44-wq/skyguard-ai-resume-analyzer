from datetime import datetime, timezone
import json
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def get_utc_now():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    reset_token_hash = db.Column(db.String(255), nullable=True, index=True)
    reset_token_expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    # Relationships with cascading delete
    resumes = db.relationship('Resume', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    analyses = db.relationship('Analysis', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    chat_messages = db.relationship('ChatMessage', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password: str):
        """Hashes and sets password using Werkzeug PBKDF2/scrypt."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Checks if provided password matches hash."""
        return check_password_hash(self.password_hash, password)

    def set_reset_token(self, raw_token: str = None, expires_in_seconds: int = 3600) -> str:
        """Generates (or uses provided) raw token, hashes with SHA-256, sets expiration, and returns raw token."""
        import hashlib
        import secrets
        from datetime import timedelta
        if not raw_token:
            raw_token = secrets.token_urlsafe(32)
        self.reset_token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
        self.reset_token_expires_at = get_utc_now() + timedelta(seconds=expires_in_seconds)
        return raw_token

    @classmethod
    def verify_reset_token(cls, raw_token: str):
        """
        Finds user by token hash and verifies validity and expiration.
        Returns User instance if valid, or None if invalid/expired.
        """
        import hashlib
        if not raw_token:
            return None

        token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
        user = cls.query.filter_by(reset_token_hash=token_hash).first()
        if not user or not user.reset_token_expires_at:
            return None

        now = get_utc_now()
        expires_at = user.reset_token_expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if now > expires_at:
            return None

        return user

    def clear_reset_token(self):
        """Clears reset token fields after single use."""
        self.reset_token_hash = None
        self.reset_token_expires_at = None

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<User {self.email}>'


class Resume(db.Model):
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    target_role = db.Column(db.String(100), nullable=True, default='')
    stored_filename = db.Column(db.String(255), nullable=False, unique=True)
    file_size = db.Column(db.Integer, nullable=False, default=0)
    file_type = db.Column(db.String(10), nullable=False, default='pdf')
    extracted_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    # Relationships with cascading delete
    analyses = db.relationship('Analysis', backref='resume', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'target_role': self.target_role,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Resume {self.filename}>'


class Analysis(db.Model):
    __tablename__ = 'analyses'
    __table_args__ = (
        db.CheckConstraint('overall_score >= 0 AND overall_score <= 100', name='check_overall_score_range'),
        db.CheckConstraint('ats_score >= 0 AND ats_score <= 100', name='check_ats_score_range'),
        db.CheckConstraint('job_match_score >= 0 AND job_match_score <= 100', name='check_job_match_score_range'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id', ondelete='CASCADE'), nullable=False, index=True)
    target_role = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text, nullable=True)
    
    # Key Scores (0 - 100)
    overall_score = db.Column(db.Integer, nullable=False, default=0)
    ats_score = db.Column(db.Integer, nullable=False, default=0)
    job_match_score = db.Column(db.Integer, nullable=False, default=0)
    
    summary = db.Column(db.Text, nullable=True)
    analysis_json = db.Column(db.Text, nullable=False)  # JSON-encoded payload
    created_at = db.Column(db.DateTime, default=get_utc_now)

    # Relationships with cascading delete
    chat_messages = db.relationship('ChatMessage', backref='analysis', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def parsed_data(self):
        """Helper to return parsed dictionary of the JSON analysis."""
        if not self.analysis_json:
            return {}
        try:
            return json.loads(self.analysis_json)
        except Exception:
            return {}

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'resume_id': self.resume_id,
            'target_role': self.target_role,
            'has_job_description': bool(self.job_description),
            'overall_score': self.overall_score,
            'ats_score': self.ats_score,
            'job_match_score': self.job_match_score,
            'summary': self.summary,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Analysis id={self.id} role="{self.target_role}" score={self.overall_score}>'


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    @property
    def message(self):
        """Property alias for content."""
        return self.content

    def to_dict(self):
        return {
            'id': self.id,
            'analysis_id': self.analysis_id,
            'role': self.role,
            'content': self.content,
            'message': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<ChatMessage id={self.id} role={self.role}>'
