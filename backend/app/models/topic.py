from datetime import datetime
from app import db


class Topic(db.Model):
    """话题表"""
    __tablename__ = 'topics'
    
    id = db.Column(db.Integer, primary_key=True)
    topic_name = db.Column(db.String(200), nullable=False)
    topic_tag = db.Column(db.String(200), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    weibo_posts = db.relationship('WeiboPost', backref='topic', lazy='dynamic', cascade='all, delete-orphan')
    keywords = db.relationship('Keyword', backref='topic', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'topic_name': self.topic_name,
            'topic_tag': self.topic_tag,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Topic {self.topic_name}>'
