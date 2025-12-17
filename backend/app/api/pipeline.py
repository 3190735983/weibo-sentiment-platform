"""
Pipeline API接口
提供完整的数据处理流程
"""
from flask import Blueprint, request, jsonify
from app.services.pipeline_service import DataPipelineService

pipeline_bp = Blueprint('pipeline', __name__, url_prefix='/api/pipeline')


@pipeline_bp.route('/run', methods=['POST'])
def run_pipeline():
    """
    运行完整pipeline
    
    Request Body:
    {
        "mode": "hot_topics",  // 'hot_topics' 或 'search'
        "keyword": "春节",  // mode='search'时必需
        "limit": 10,  // mode='hot_topics'时的数量，默认10
        "steps": {  // 可选，默认全部执行
            "crawl": true,
            "sync": true,
            "keywords": true,
            "sentiment": true
        }
    }
    
    Response:
    {
        "status": "success",
        "results": {
            "topics_added": 5,
            "posts_synced": 150,
            "keywords_extracted": 400,
            "sentiments_analyzed": 150,
            "errors": []
        },
        "message": "..."
    }
    """
    try:
        data = request.get_json() or {}
        
        mode = data.get('mode', 'hot_topics')
        keyword = data.get('keyword')
        limit = data.get('limit', 10)
        steps = data.get('steps')
        
        # 验证参数
        if mode not in ['hot_topics', 'search']:
            return jsonify({
                'status': 'error',
                'message': 'mode必须是hot_topics或search'
            }), 400
        
        if mode == 'search' and not keyword:
            return jsonify({
                'status': 'error',
                'message': 'search模式需要提供keyword参数'
            }), 400
        
        # 运行pipeline
        pipeline_service = DataPipelineService()
        result = pipeline_service.run_full_pipeline(
            mode=mode,
            keyword=keyword,
            limit=limit,
            steps=steps
        )
        
        return jsonify(result), 200 if result['status'] == 'success' else 400
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'服务器错误: {str(e)}'
        }), 500


@pipeline_bp.route('/process/<int:topic_id>', methods=['POST'])
def process_topic(topic_id):
    """
    处理单个话题（仅数据处理，不包括爬取）
    
    Response:
    {
        "status": "success",
        "results": {
            "keywords_count": 50,
            "sentiments_count": 100,
            "errors": []
        },
        "message": "..."
    }
    """
    try:
        pipeline_service = DataPipelineService()
        result = pipeline_service.process_topic(topic_id)
        
        return jsonify(result), 200 if result['status'] == 'success' else 400
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'服务器错误: {str(e)}'
        }), 500


@pipeline_bp.route('/status', methods=['GET'])
def get_status():
    """
    获取pipeline状态
    
    Response:
    {
        "is_running": false,
        "crawler_status": {...}
    }
    """
    try:
        pipeline_service = DataPipelineService()
        result = pipeline_service.get_status()
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'服务器错误: {str(e)}'
        }), 500
