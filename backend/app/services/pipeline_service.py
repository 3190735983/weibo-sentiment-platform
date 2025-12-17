"""
数据Pipeline服务 - 编排完整的数据处理流程
爬取 → 同步 → 清洗/关键词 → 情感分析
"""
from typing import List, Dict, Optional
from app.services.crawler_service import CrawlerService
from app.services.data_processing_service import DataProcessingService
from app.services.sentiment_service import SentimentAnalysisService
from app.services.mediacrawler_wrapper import MediaCrawlerWrapper
from app.models import Topic
from app import db


class DataPipelineService:
    """数据Pipeline服务 - 端到端流程编排"""
    
    def __init__(self):
        self.crawler_service = CrawlerService()
        self.data_processing_service = DataProcessingService()
        self.sentiment_service = SentimentAnalysisService()
        self.mediacrawler = MediaCrawlerWrapper()
        self.is_running = False
    
    def run_full_pipeline(self, 
                         mode: str = 'hot_topics',
                         keyword: Optional[str] = None,
                         limit: int = 10,
                         steps: Optional[Dict] = None) -> Dict:
        """
        运行完整pipeline
        
        Args:
            mode: 'hot_topics' (爬取热点) 或 'search' (搜索指定话题)
            keyword: mode='search'时的搜索关键词
            limit: mode='hot_topics'时爬取的话题数量
            steps: 要执行的步骤 {'crawl': True, 'sync': True, 'keywords': True, 'sentiment': True}
            
        Returns:
            {
                'status': 'success' | 'error',
                'results': {...},
                'message': str
            }
        """
        if self.is_running:
            return {
                'status': 'error',
                'message': 'Pipeline已在运行中'
            }
        
        self.is_running = True
        
        # 默认步骤
        if steps is None:
            steps = {
                'crawl': True,
                'sync': True,
                'keywords': True,
                'sentiment': True
            }
        
        results = {
            'topics_added': 0,
            'posts_synced': 0,
            'keywords_extracted': 0,
            'sentiments_analyzed': 0,
            'errors': []
        }
        
        try:
            # Step 1: 爬取话题
            if steps.get('crawl', True):
                if mode == 'hot_topics':
                    crawl_result = self.crawler_service.crawl_hot_topics(
                        limit=limit,
                        filter_sensitive=True
                    )
                    if crawl_result['status'] == 'success':
                        results['topics_added'] = crawl_result['topics_added']
                    else:
                        results['errors'].append(f"爬取失败: {crawl_result['message']}")
                        self.is_running = False
                        return {
                            'status': 'error',
                            'results': results,
                            'message': crawl_result['message']
                        }
                elif mode == 'search':
                    if not keyword:
                        self.is_running = False
                        return {
                            'status': 'error',
                            'message': 'search模式需要提供keyword参数'
                        }
                    
                    search_result = self.crawler_service.search_topic(keyword)
                    if search_result['status'] == 'success':
                        results['topics_added'] = 1 if search_result['is_new'] else 0
                    else:
                        results['errors'].append(f"搜索失败: {search_result['message']}")
            
            # 提示: MediaCrawler需要单独运行
            # 自动运行会导致超时,所以这里只配置,不运行
            print("[Pipeline] ⚠️ 提示: 话题已创建并配置到MediaCrawler")
            print("[Pipeline] 💡 要获取微博数据,请:")
            print("[Pipeline]    1. 手动运行 MediaCrawler: cd MediaCrawler && python main.py --platform wb --lt qrcode --type search")
            print("[Pipeline]    2. 或使用后台运行的 run_full_crawler.py")
            print("[Pipeline]    3. 完成后再次运行 Pipeline 同步数据")
            
            # Step 2: 同步MediaCrawler数据
            if steps.get('sync', True):
                sync_result = self.crawler_service.sync_mediacrawler_data()
                if sync_result['status'] == 'success':
                    results['posts_synced'] = sync_result['posts_added']
                else:
                    results['errors'].append(f"同步失败: {sync_result['message']}")
            
            # Step 3: 提取关键词
            if steps.get('keywords', True):
                # 处理所有活跃话题
                keywords_results = self.data_processing_service.process_all_topics(
                    method='tfidf',
                    top_n=50
                )
                
                for result in keywords_results:
                    if result.get('status') == 'success':
                        results['keywords_extracted'] += result.get('keywords_count', 0)
                    else:
                        results['errors'].append(f"关键词提取失败: {result.get('message', '')}")
            
            # Step 4: 情感分析
            if steps.get('sentiment', True):
                # 分析所有活跃话题
                topics = Topic.query.filter_by(is_active=True).all()
                
                for topic in topics:
                    sentiment_result = self.sentiment_service.analyze(topic.id)
                    if sentiment_result.get('success'):
                        results['sentiments_analyzed'] += sentiment_result.get('analyzed_count', 0)
                    else:
                        results['errors'].append(
                            f"话题{topic.id}情感分析失败: {sentiment_result.get('error', '')}"
                        )
            
            self.is_running = False
            
            return {
                'status': 'success',
                'results': results,
                'message': f'Pipeline完成: 新增{results["topics_added"]}话题, 同步{results["posts_synced"]}微博, 提取{results["keywords_extracted"]}关键词, 分析{results["sentiments_analyzed"]}情感'
            }
        
        except Exception as e:
            self.is_running = False
            results['errors'].append(str(e))
            return {
                'status': 'error',
                'results': results,
                'message': f'Pipeline执行失败: {str(e)}'
            }
    
    def process_topic(self, topic_id: int, skip_crawl: bool = True) -> Dict:
        """
        处理单个话题（不包括爬取）
        
        Args:
            topic_id: 话题ID
            skip_crawl: 是否跳过爬取（默认跳过，仅处理现有数据）
            
        Returns:
            处理结果
        """
        results = {
            'keywords_count': 0,
            'sentiments_count': 0,
            'errors': []
        }
        
        try:
            # 提取关键词
            keyword_result = self.data_processing_service.process_topic(
                topic_id=topic_id,
                method='tfidf',
                top_n=50
            )
            
            if keyword_result.get('status') == 'success':
                results['keywords_count'] = keyword_result.get('keywords_count', 0)
            else:
                results['errors'].append(f"关键词提取失败: {keyword_result.get('message', '')}")
            
            # 情感分析
            sentiment_result = self.sentiment_service.analyze(topic_id)
            
            if sentiment_result.get('success'):
                results['sentiments_count'] = sentiment_result.get('analyzed_count', 0)
            else:
                results['errors'].append(f"情感分析失败: {sentiment_result.get('error', '')}")
            
            return {
                'status': 'success',
                'results': results,
                'message': f'处理完成: 提取{results["keywords_count"]}关键词, 分析{results["sentiments_count"]}情感'
            }
        
        except Exception as e:
            results['errors'].append(str(e))
            return {
                'status': 'error',
                'results': results,
                'message': f'处理失败: {str(e)}'
            }
    
    def get_status(self) -> Dict:
        """获取Pipeline状态"""
        return {
            'is_running': self.is_running,
            'crawler_status': self.crawler_service.get_status()
        }
