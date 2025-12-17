from flask import Blueprint, request, jsonify, send_file
from app.models import Topic, WeiboPost
from app import db
from datetime import datetime
import csv
import io

manage_bp = Blueprint('manage', __name__)


@manage_bp.route('/topics', methods=['GET'])
def get_topics():
    """获取话题列表"""
    try:
        topics = Topic.query.all()
        return jsonify({
            'success': True,
            'data': [topic.to_dict() for topic in topics]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        }), 500


@manage_bp.route('/topics', methods=['POST'])
def create_topic():
    """添加话题"""
    try:
        data = request.get_json()
        topic = Topic(
            topic_name=data['topic_name'],
            topic_tag=data['topic_tag'],
            is_active=data.get('is_active', True)
        )
        db.session.add(topic)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': topic.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'添加失败: {str(e)}'
        }), 500


@manage_bp.route('/topics/<int:topic_id>', methods=['PUT'])
def update_topic(topic_id):
    """更新话题"""
    try:
        topic = Topic.query.get_or_404(topic_id)
        data = request.get_json()
        
        topic.topic_name = data.get('topic_name', topic.topic_name)
        topic.topic_tag = data.get('topic_tag', topic.topic_tag)
        topic.is_active = data.get('is_active', topic.is_active)
        topic.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': topic.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'更新失败: {str(e)}'
        }), 500


@manage_bp.route('/topics/<int:topic_id>', methods=['DELETE'])
def delete_topic(topic_id):
    """删除话题"""
    try:
        topic = Topic.query.get_or_404(topic_id)
        db.session.delete(topic)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '删除成功'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'删除失败: {str(e)}'
        }), 500


@manage_bp.route('/data/export', methods=['GET'])
def export_data():
    """导出数据"""
    try:
        topic_id = request.args.get('topic_id', type=int)
        format_type = request.args.get('format', 'csv')
        
        # TODO: 实现数据导出逻辑
        
        return jsonify({
            'success': True,
            'message': '导出功能待实现'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'导出失败: {str(e)}'
        }), 500


@manage_bp.route('/data/query', methods=['GET'])
def query_data():
    """查询历史数据"""
    try:
        topic_id = request.args.get('topic_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        keyword = request.args.get('keyword')
        
        # TODO: 实现数据查询逻辑
        
        return jsonify({
            'success': True,
            'data': []
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        }), 500
