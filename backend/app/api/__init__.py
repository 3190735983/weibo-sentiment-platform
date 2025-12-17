from app.api.crawler import crawler_bp
from app.api.sentiment import sentiment_bp
from app.api.keyword import keyword_bp
from app.api.visualization import visualization_bp
from app.api.ai_insight import ai_insight_bp
from app.api.manage import manage_bp
from app.api.pipeline import pipeline_bp

__all__ = [
    'crawler_bp',
    'sentiment_bp',
    'keyword_bp',
    'visualization_bp',
    'ai_insight_bp',
    'manage_bp',
    'pipeline_bp'
]
