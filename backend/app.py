import os
from pathlib import Path
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

from backend.config import Config
from backend.database import init_db, SessionLocal
from backend.utils.responses import error_response

# Import Blueprints
from backend.routes.auth import auth_bp
from backend.routes.farmer import farmer_bp
from backend.routes.center import center_bp
from backend.routes.booking import booking_bp
from backend.routes.procurement import procurement_bp
from backend.routes.admin import admin_bp
from backend.routes.ivr import ivr_bp
from backend.routes.chatbot import chatbot_bp

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / 'frontend'

def create_app():
    app = Flask(__name__, static_folder=str(FRONTEND_DIR))
    app.config.from_object(Config)

    # Enable CORS
    CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)

    # Initialize Database Schema
    with app.app_context():
        try:
            init_db()
        except Exception as e:
            print(f"[Warning] Database auto-init error: {e}")

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(farmer_bp)
    # Also register plural alias /api/farmers to guarantee compatibility with PRD
    app.register_blueprint(farmer_bp, name='farmers', url_prefix='/api/farmers')

    app.register_blueprint(center_bp)
    app.register_blueprint(center_bp, name='centers', url_prefix='/api/centers')

    app.register_blueprint(booking_bp)
    app.register_blueprint(procurement_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(ivr_bp)
    app.register_blueprint(chatbot_bp)

    # Database session teardown
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        SessionLocal.remove()

    # Serve Frontend Single-Page App and static files
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        # Don't intercept API routes
        if path.startswith('api/'):
            return error_response(f"API endpoint '/{path}' not found.", error_code="NOT_FOUND", status_code=404)

        if path:
            target_file = FRONTEND_DIR / path
            if target_file.exists():
                if target_file.is_dir():
                    index_file = target_file / 'index.html'
                    if index_file.exists():
                        return send_from_directory(str(target_file), 'index.html')
                return send_from_directory(str(FRONTEND_DIR), path)

            # Check css/ subfolder fallback
            css_fallback = FRONTEND_DIR / 'css' / path
            if css_fallback.exists():
                return send_from_directory(str(FRONTEND_DIR / 'css'), path)

            # Check js/ subfolder fallback
            js_fallback = FRONTEND_DIR / 'js' / path
            if js_fallback.exists():
                return send_from_directory(str(FRONTEND_DIR / 'js'), path)

        # Default to home.html or index.html
        if (FRONTEND_DIR / 'home.html').exists():
            return send_from_directory(str(FRONTEND_DIR), 'home.html')
        return send_from_directory(str(FRONTEND_DIR), 'index.html')

    # Global Error Handlers
    @app.errorhandler(404)
    def handle_404(e):
        return error_response("The requested resource was not found.", error_code="NOT_FOUND", status_code=404)

    @app.errorhandler(405)
    def handle_405(e):
        return error_response("HTTP method not allowed for this endpoint.", error_code="METHOD_NOT_ALLOWED", status_code=405)

    @app.errorhandler(500)
    def handle_500(e):
        return error_response("An internal server error occurred.", error_code="INTERNAL_SERVER_ERROR", status_code=500)

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    print(f"🌾 FASAL Backend starting on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)
