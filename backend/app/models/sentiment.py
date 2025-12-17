from datetime import datetime
from app import db


class SentimentResult(db.Model):
    """情感分析结果表"""
    __tablename__ = 'sentiment_results'
    
    id = db.Column(db.Integer, primary_key=True)
    weibo_id = db.Column(db.Integer, db.ForeignKey('weibo_posts.id'), nullable=False)
    sentiment_label = db.Column(db.String(20), nullable=False)  # 正面/负面/中性
    sentiment_score = db.Column(db.Float)
    sentiment_intensity = db.Column(db.Float)
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'weibo_id': self.weibo_id,
            'sentiment_label': self.sentiment_label,
            'sentiment_score': self.sentiment_score,
            'sentiment_intensity': self.sentiment_intensity,
            'analyzed_at': self.analyzed_at.isoformat() if self.analyzed_at else None
        }
    
    def __repr__(self):
        return f'<SentimentResult {self.id} - {self.sentiment_label}>'
