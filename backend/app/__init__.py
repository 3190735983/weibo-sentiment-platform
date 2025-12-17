from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from app.config import config

# Initialize extensions
db = SQLAlchemy()

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.api import crawler_bp, sentiment_bp, keyword_bp, visualization_bp, ai_insight_bp, manage_bp, pipeline_bp
    
    app.register_blueprint(crawler_bp)  # url_prefix已在blueprint中定义
    app.register_blueprint(sentiment_bp, url_prefix='/api/sentiment')
    app.register_blueprint(keyword_bp, url_prefix='/api/keyword')
    app.register_blueprint(visualization_bp, url_prefix='/api/visualization')
    app.register_blueprint(ai_insight_bp, url_prefix='/api/ai')
    app.register_blueprint(manage_bp, url_prefix='/api/manage')
    app.register_blueprint(pipeline_bp)  # url_prefix已在blueprint中定义
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    @app.route('/')
    def index():
        return {'message': 'Weibo Sentiment Analysis Platform API', 'status': 'running'}
    
    @app.route('/health')
    def health():
        return {'status': 'healthy'}
    
    return app
