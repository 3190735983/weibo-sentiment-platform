import os
import joblib
import numpy as np
from app.models import SentimentResult, WeiboPost
from app import db
from datetime import datetime


class SentimentAnalysisService:
    """情感分析服务"""
    
    def __init__(self):
        self.model = None
        self.label_map = {
            0: '中性',
            1: '正面',
            2: '负面'
        }
        # 反向映射
        self.label_to_index = {v: k for k, v in self.label_map.items()}
        self.model_loaded = False
        
    def load_model(self, model_path=None):
        """加载情感分析模型
        
        Args:
            model_path: 模型文件路径，如果为None则使用配置文件中的路径
        """
        if self.model_loaded:
            print("[SentimentService] Model already loaded")
            return True
            
        try:
            if model_path is None:
                # 从backend/app目录向上到项目根目录
                # __file__ -> app/services/sentiment_service.py
                # dirname(__file__) -> app/services
                # dirname(dirname(__file__)) -> app
                # dirname(dirname(dirname(__file__))) -> backend
                # dirname(dirname(dirname(dirname(__file__)))) -> project root
                current_file = os.path.abspath(__file__)
                app_services_dir = os.path.dirname(current_file)  # app/services
                app_dir = os.path.dirname(app_services_dir)  # app
                backend_dir = os.path.dirname(app_dir)  # backend
                project_root = os.path.dirname(backend_dir)  # project root
                model_path = os.path.join(project_root, 'deployed_ml_models', 'lightgbm_classifier.joblib')
            
            if not os.path.exists(model_path):
                print(f"[SentimentService] Model file not found: {model_path}")
                return False
                
            print(f"[SentimentService] Loading model from: {model_path}")
            self.model = joblib.load(model_path)
            self.model_loaded = True
            print(f"[SentimentService] Model loaded successfully")
            return True
            
        except Exception as e:
            print(f"[SentimentService] Error loading model: {e}")
            return False
    
    def predict(self, text):
        """预测单条文本的情感
        
        Args:
            text: 文本内容
        
        Returns:
            dict: {'label': str, 'score': float, 'intensity': float}
        """
        if not self.model_loaded:
            if not self.load_model():
                return {
                    'label': '中性',
                    'score': 0.33,
                    'intensity': 0.5
                }
        
        try:
            # 使用模型进行预测
            # 注意：这里假设模型接受文本输入，如果需要特征提取请相应修改
            prediction = self.model.predict([text])[0]
            
            # 获取概率分数（如果模型支持）
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba([text])[0]
                score = float(probabilities[prediction])
                intensity = float(np.max(probabilities))
            else:
                score = 1.0
                intensity = 1.0
            
            label = self.label_map.get(prediction, '中性')
            
            return {
                'label': label,
                'score': score,
                'intensity': intensity
            }
            
        except Exception as e:
            print(f"[SentimentService] Error predicting: {e}")
            return {
                'label': '中性',
                'score': 0.33,
                'intensity': 0.5
            }
    
    def analyze(self, topic_id):
        """对指定话题的评论进行情感分析
        
        Args:
            topic_id: 话题ID
        
        Returns:
            dict: {'analyzed_count': int, 'success': bool}
        """
        if not self.model_loaded:
            if not self.load_model():
                return {'analyzed_count': 0, 'success': False, 'error': 'Model not loaded'}
        
        try:
            # 获取该话题下所有未分析的微博评论
            posts = WeiboPost.query.filter_by(topic_id=topic_id).all()
            
            analyzed_count = 0
            
            for post in posts:
                # 检查是否已经分析过
                existing_result = SentimentResult.query.filter_by(weibo_id=post.id).first()
                if existing_result:
                    continue
                
                # 如果没有评论文本，跳过
                if not post.comment_text or len(post.comment_text.strip()) < 3:
                    continue
                
                # 预测情感
                result = self.predict(post.comment_text)
                
                # 保存结果
                sentiment_result = SentimentResult(
                    weibo_id=post.id,
                    sentiment_label=result['label'],
                    sentiment_score=result['score'],
                    sentiment_intensity=result['intensity'],
                    analyzed_at=datetime.utcnow()
                )
                db.session.add(sentiment_result)
                analyzed_count += 1
            
            db.session.commit()
            
            return {
                'analyzed_count': analyzed_count,
                'success': True
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"[SentimentService] Error analyzing topic {topic_id}: {e}")
            return {
                'analyzed_count': 0,
                'success': False,
                'error': str(e)
            }
    
    def batch_predict(self, texts):
        """批量预测文本情感
        
        Args:
            texts: 文本列表
        
        Returns:
            list: 预测结果列表
        """
        if not self.model_loaded:
            if not self.load_model():
                return []
        
        try:
            results = []
            
            # 批量预测
            predictions = self.model.predict(texts)
            
            # 获取概率（如果支持）
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(texts)
            else:
                probabilities = None
            
            for i, prediction in enumerate(predictions):
                label = self.label_map.get(prediction, '中性')
                
                if probabilities is not None:
                    score = float(probabilities[i][prediction])
                    intensity = float(np.max(probabilities[i]))
                else:
                    score = 1.0
                    intensity = 1.0
                
                results.append({
                    'label': label,
                    'score': score,
                    'intensity': intensity
                })
            
            return results
            
        except Exception as e:
            print(f"[SentimentService] Error in batch prediction: {e}")
            return []
    
    def get_sentiment_distribution(self, topic_id):
        """获取话题的情感分布统计
        
        Args:
            topic_id: 话题ID
        
        Returns:
            dict: 情感分布统计
        """
        try:
            # 获取该话题下所有情感分析结果
            results = db.session.query(
                SentimentResult.sentiment_label,
                db.func.count(SentimentResult.id).label('count')
            ).join(
                WeiboPost, SentimentResult.weibo_id == WeiboPost.id
            ).filter(
                WeiboPost.topic_id == topic_id
            ).group_by(
                SentimentResult.sentiment_label
            ).all()
            
            distribution = {
                '正面': 0,
                '负面': 0,
                '中性': 0
            }
            
            total = 0
            for label, count in results:
                distribution[label] = count
                total += count
            
            # 计算百分比
            percentages = {}
            if total > 0:
                for label, count in distribution.items():
                    percentages[label] = round(count / total * 100, 2)
            else:
                percentages = {'正面': 0, '负面': 0, '中性': 0}
            
            return {
                'distribution': distribution,
                'percentages': percentages,
                'total': total
            }
            
        except Exception as e:
            print(f"[SentimentService] Error getting distribution: {e}")
            return {
                'distribution': {'正面': 0, '负面': 0, '中性': 0},
                'percentages': {'正面': 0, '负面': 0, '中性': 0},
                'total': 0
            }
