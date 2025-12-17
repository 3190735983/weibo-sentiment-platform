from flask import Blueprint, request, jsonify
from app.models import WeiboPost, SentimentResult, Keyword, Topic
from app import db
from sqlalchemy import func
from datetime import datetime, timedelta

visualization_bp = Blueprint('visualization', __name__)


@visualization_bp.route('/topics', methods=['GET'])
def get_topics():
    """获取所有话题列表及微博数量"""
    try:
        # 查询所有话题,并统计每个话题的微博数量
        topics_with_count = db.session.query(
            Topic.id,
            Topic.topic_name,
            Topic.topic_tag,
            func.count(WeiboPost.id).label('post_count')
        ).outerjoin(
            WeiboPost, Topic.id == WeiboPost.topic_id
        ).filter(
            Topic.is_active == True
        ).group_by(
            Topic.id, Topic.topic_name, Topic.topic_tag
        ).order_by(
            func.count(WeiboPost.id).desc()
        ).all()
        
        # 格式化返回数据
        topics = [{
            'id': t.id,
            'name': t.topic_name,
            'tag': t.topic_tag,
            'post_count': t.post_count
        } for t in topics_with_count]
        
        return jsonify({
            'success': True,
            'topics': topics
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询话题列表失败: {str(e)}'
        }), 500


@visualization_bp.route('/topics/<int:topic_id>/keywords', methods=['GET'])
def get_topic_keywords(topic_id):
    """获取指定话题的关键词数据"""
    try:
        # 验证话题是否存在
        topic = Topic.query.get(topic_id)
        if not topic:
            return jsonify({
                'success': False,
                'message': f'话题ID {topic_id} 不存在'
            }), 404
        
        # 获取关键词数据,按频次降序排序,取前50个
        keywords = Keyword.query.filter_by(
            topic_id=topic_id
        ).order_by(
            Keyword.frequency.desc()
        ).limit(50).all()
        
        # 格式化为echarts-wordcloud需要的格式
        keyword_data = [{
            'name': kw.keyword,
            'value': kw.frequency
        } for kw in keywords]
        
        return jsonify({
            'success': True,
            'keywords': keyword_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询关键词数据失败: {str(e)}'
        }), 500


@visualization_bp.route('/topics/<int:topic_id>/sentiments', methods=['GET'])
def get_topic_sentiments(topic_id):
    """获取指定话题的情感分布统计"""
    try:
        # 验证话题是否存在
        topic = Topic.query.get(topic_id)
        if not topic:
            return jsonify({
                'success': False,
                'message': f'话题ID {topic_id} 不存在'
            }), 404
        
        # 查询该话题下所有微博的情感分析结果
        sentiment_stats = db.session.query(
            SentimentResult.sentiment_label,
            func.count(SentimentResult.id).label('count')
        ).join(
            WeiboPost, SentimentResult.weibo_id == WeiboPost.id
        ).filter(
            WeiboPost.topic_id == topic_id
        ).group_by(
            SentimentResult.sentiment_label
        ).all()
        
        # 初始化情感统计
        sentiments = {
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }
        
        # 填充统计数据
        for label, count in sentiment_stats:
            label_lower = label.lower()
            if '正' in label or 'positive' in label_lower:
                sentiments['positive'] = count
            elif '负' in label or 'negative' in label_lower:
                sentiments['negative'] = count
            elif '中' in label or 'neutral' in label_lower:
                sentiments['neutral'] = count
        
        return jsonify({
            'success': True,
            'sentiments': sentiments
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询情感分布失败: {str(e)}'
        }), 500


@visualization_bp.route('/trend', methods=['GET'])
def get_trend_data():
    """获取热度趋势数据"""
    try:
        topic_id = request.args.get('topic_id', type=int)
        period = request.args.get('period', 'day')  # hour, day, week
        
        # TODO: 实现趋势数据统计逻辑
        data = {
            'timestamps': [],
            'comment_counts': [],
            'like_counts': [],
            'repost_counts': []
        }
        
        return jsonify({
            'success': True,
            'data': data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        }), 500


@visualization_bp.route('/geographic', methods=['GET'])
def get_geographic_data():
    """获取地域分析数据"""
    try:
        topic_id = request.args.get('topic_id', type=int)
        
        # TODO: 实现地域数据统计逻辑
        data = {
            'regions': []
        }
        
        return jsonify({
            'success': True,
            'data': data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        }), 500
