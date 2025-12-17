from datetime import datetime
from app import db


class Keyword(db.Model):
    """关键词表"""
    __tablename__ = 'keywords'
    
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    keyword = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.Integer, default=0)
    time_period = db.Column(db.String(50))  # e.g., "2024-12-16", "2024-12-W50"
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'topic_id': self.topic_id,
            'keyword': self.keyword,
            'frequency': self.frequency,
            'time_period': self.time_period,
            'analyzed_at': self.analyzed_at.isoformat() if self.analyzed_at else None
        }
    
    def __repr__(self):
        return f'<Keyword {self.keyword}>'
