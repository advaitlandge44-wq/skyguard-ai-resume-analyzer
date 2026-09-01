import os
from app import create_app

# Create Flask application instance
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Run development server
    app.run(host='127.0.0.1', port=port, debug=True)
