import os
from app import create_app

app = create_app(os.getenv('FLASK_ENV') or 'default')

if __name__ == '__main__':
    host = app.config.get('HOST', '0.0.0.0')
    port = app.config.get('PORT', 5000)
    debug = app.config.get('DEBUG', True)
    
    print(f"Starting Flask server on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
