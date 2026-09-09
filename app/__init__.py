import os
import logging
from flask import Flask, render_template, request, jsonify, session, g
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

try:
    from flask_cors import CORS
    cors = CORS()
except ImportError:
    cors = None

from config import config_by_name
from app.models import db, User

# Initialize extensions
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["120 per minute"]
)


def create_app(config_name='default'):
    """Application factory for SkyGuard AI Resume Analyzer."""
    app = Flask(__name__)
    
    # Load configuration
    config_obj = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(config_obj)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )

    # Ensure required runtime directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.root_path, '..', 'instance'), exist_ok=True)

    # Initialize extensions with app
    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    
    # Configure CORS for decoupled frontend deployment (e.g. Vercel)
    if cors:
        cors_origins = app.config.get('CORS_ORIGINS', '*')
        cors.init_app(
            app,
            supports_credentials=True,
            origins=cors_origins,
            allow_headers=['Content-Type', 'X-CSRFToken', 'X-Requested-With', 'Authorization', 'Accept'],
            methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
        )

    # User context loader before each request
    @app.before_request
    def load_logged_in_user():
        user_id = session.get('user_id')
        if user_id is None:
            g.user = None
        else:
            g.user = db.session.get(User, user_id)

    # Inject Security Headers (Phase 32)
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    # Clean session teardown on error (Phase 30)
    @app.teardown_request
    def teardown_db_session(exception=None):
        if exception:
            db.session.rollback()

    # Context processors for template rendering
    @app.context_processor
    def inject_globals():
        return {
            'current_user': getattr(g, 'user', None),
            'app_name': 'SkyGuard AI',
            'openai_enabled': bool(app.config.get('OPENAI_API_KEY')),
            'is_demo': session.get('is_demo', False)
        }

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.resume import resume_bp
    from app.routes.analysis import analysis_bp
    from app.routes.api import api_bp

    # Exempt REST API blueprint from CSRF form tokens for cross-origin API compatibility
    csrf.exempt(api_bp)

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(resume_bp, url_prefix='/resume')
    app.register_blueprint(analysis_bp, url_prefix='/analysis')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Register Error Handlers
    register_error_handlers(app)

    # Create tables automatically if running in dev/standalone
    with app.app_context():
        db.create_all()
        # Safe automatic column migration for existing SQLite databases
        try:
            with db.engine.connect() as conn:
                # 1. Resumes table migration
                result_resumes = conn.execute(db.text("PRAGMA table_info(resumes)"))
                resume_cols = [row[1] for row in result_resumes.fetchall()]
                if 'target_role' not in resume_cols:
                    conn.execute(db.text("ALTER TABLE resumes ADD COLUMN target_role VARCHAR(100) DEFAULT ''"))

                # 2. Users table migration for password reset tokens
                result_users = conn.execute(db.text("PRAGMA table_info(users)"))
                user_cols = [row[1] for row in result_users.fetchall()]
                if 'reset_token_hash' not in user_cols:
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN reset_token_hash VARCHAR(255)"))
                if 'reset_token_expires_at' not in user_cols:
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN reset_token_expires_at DATETIME"))

                conn.commit()
        except Exception:
            pass

    return app


def register_error_handlers(app: Flask):
    """Registers standard HTTP error response handlers."""

    def is_api_request():
        return request.is_json or request.path.startswith('/api/') or request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    @app.errorhandler(400)
    def bad_request(e):
        if is_api_request():
            return jsonify({'success': False, 'error': 'Bad Request. Please check your submission.'}), 400
        return render_template('errors/400.html', error=e), 400

    @app.errorhandler(401)
    def unauthorized(e):
        if is_api_request():
            return jsonify({'success': False, 'error': 'Unauthorized. Please log in.'}), 401
        return render_template('errors/401.html', error=e), 401

    @app.errorhandler(403)
    def forbidden(e):
        if is_api_request():
            return jsonify({'success': False, 'error': 'Forbidden. You do not have permission to access this resource.'}), 403
        return render_template('errors/403.html', error=e), 403

    @app.errorhandler(404)
    def not_found(e):
        if is_api_request():
            return jsonify({'success': False, 'error': 'Resource not found.'}), 404
        return render_template('errors/404.html', error=e), 404

    @app.errorhandler(413)
    def request_entity_too_large(e):
        if is_api_request():
            return jsonify({'success': False, 'error': 'Uploaded file is too large (maximum size is 5MB).'}), 413
        return render_template('errors/413.html', error=e), 413

    @app.errorhandler(429)
    def ratelimit_handler(e):
        if is_api_request():
            return jsonify({'success': False, 'error': 'Rate limit exceeded. Please slow down and try again later.'}), 429
        return render_template('errors/429.html', error=e), 429

    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f"Internal server error: {e}", exc_info=True)
        if is_api_request():
            return jsonify({'success': False, 'error': 'AI analysis service or server error. Please try again later.'}), 500
        return render_template('errors/500.html', error=e), 500
