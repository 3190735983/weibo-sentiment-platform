"""
爬虫API接口
提供热点爬取、话题搜索、数据同步等功能
"""
from flask import Blueprint, request, jsonify
from app.services.crawler_service import CrawlerService
from app import db

crawler_bp = Blueprint('crawler', __name__, url_prefix='/api/crawler')


@crawler_bp.route('/hot-topics', methods=['POST'])
def crawl_hot_topics():
    """
    爬取热点话题
    
    Request Body:
    {
        "limit": 10,
        "filter_sensitive": true
    }
    """
    try:
        data = request.get_json() or {}
        limit = data.get('limit', 10)
        filter_sensitive = data.get('filter_sensitive', True)
        
        crawler_service = CrawlerService()
        result = crawler_service.crawl_hot_topics(
            limit=limit,
            filter_sensitive=filter_sensitive
        )
        
        return jsonify(result), 200 if result['status'] == 'success' else 400
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'服务器错误: {str(e)}'
        }), 500


@crawler_bp.route('/search', methods=['POST'])
def search_topic():
    """
    搜索指定话题
    
    Request Body:
    {
        "keyword": "春节"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'keyword' not in data:
            return jsonify({
                'status': 'error',
                'message': '缺少keyword参数'
            }), 400
        
        keyword = data['keyword']
        
        crawler_service = CrawlerService()
        result = crawler_service.search_topic(keyword)
        
        return jsonify(result), 200 if result['status'] == 'success' else 400
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'服务器错误: {str(e)}'
        }), 500


@crawler_bp.route('/sync', methods=['POST'])
def sync_data():
    """从MediaCrawler同步数据"""
    try:
        crawler_service = CrawlerService()
        result = crawler_service.sync_mediacrawler_data()
        
        return jsonify(result), 200 if result['status'] == 'success' else 400
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'服务器错误: {str(e)}'
        }), 500


@crawler_bp.route('/status', methods=['GET'])
def get_status():
    """获取爬虫状态"""
    try:
        crawler_service = CrawlerService()
        result = crawler_service.get_status()
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'服务器错误: {str(e)}'
        }), 500
