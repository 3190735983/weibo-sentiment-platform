from datetime import datetime
from app import db


class WeiboPost(db.Model):
    """微博数据表"""
    __tablename__ = 'weibo_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    weibo_id = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    topic_text = db.Column(db.String(500))
    comment_text = db.Column(db.Text)
    user_nickname = db.Column(db.String(100))
    user_fans_count = db.Column(db.Integer, default=0)
    publish_time = db.Column(db.DateTime)
    likes_count = db.Column(db.Integer, default=0)
    reposts_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    location = db.Column(db.String(200))
    raw_data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sentiment_result = db.relationship('SentimentResult', backref='weibo_post', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'topic_id': self.topic_id,
            'weibo_id': self.weibo_id,
            'content': self.content,
            'topic_text': self.topic_text,
            'comment_text': self.comment_text,
            'user_nickname': self.user_nickname,
            'user_fans_count': self.user_fans_count,
            'publish_time': self.publish_time.isoformat() if self.publish_time else None,
            'likes_count': self.likes_count,
            'reposts_count': self.reposts_count,
            'comments_count': self.comments_count,
            'location': self.location,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<WeiboPost {self.weibo_id}>'
