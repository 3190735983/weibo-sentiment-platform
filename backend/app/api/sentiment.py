from flask import Blueprint, request, jsonify
from app.models import SentimentResult, WeiboPost
from app.services.sentiment_service import SentimentAnalysisService
from app import db

sentiment_bp = Blueprint('sentiment', __name__)
sentiment_service = SentimentAnalysisService()


@sentiment_bp.route('/analyze', methods=['POST'])
def analyze_sentiment():
    """执行情感分析"""
    try:
        data = request.get_json()
        topic_id = data.get('topic_id')
        
        if not topic_id:
            return jsonify({
                'success': False,
                'message': '缺少topic_id参数'
            }), 400
        
        # 执行情感分析
        results = sentiment_service.analyze(topic_id)
        
        return jsonify({
            'success': results['success'],
            'message': f"情感分析完成，分析了{results.get('analyzed_count', 0)}条评论",
            'data': results
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'分析失败: {str(e)}'
        }), 500


@sentiment_bp.route('/results', methods=['GET'])
def get_sentiment_results():
    """获取情感分析结果"""
    try:
        topic_id = request.args.get('topic_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 获取情感分布
        if topic_id:
            distribution = sentiment_service.get_sentiment_distribution(topic_id)
            return jsonify({
                'success': True,
                'data': distribution
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '缺少topic_id参数'
            }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        }), 500


@sentiment_bp.route('/predict', methods=['POST'])
def predict_text():
    """预测单条文本的情感"""
    try:
        data = request.get_json()
        text = data.get('text')
        
        if not text:
            return jsonify({
                'success': False,
                'message': '缺少text参数'
            }), 400
        
        result = sentiment_service.predict(text)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'预测失败: {str(e)}'
        }), 500

