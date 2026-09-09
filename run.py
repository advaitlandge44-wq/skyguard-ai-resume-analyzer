import os
from app import create_app

# Resolve environment configuration name
config_name = os.environ.get('FLASK_CONFIG') or os.environ.get('FLASK_ENV') or 'development'

# Create Flask application instance
app = create_app(config_name)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() in ['true', '1', 't'] if config_name == 'development' else False
    # Run development server
    app.run(host='0.0.0.0', port=port, debug=debug)
