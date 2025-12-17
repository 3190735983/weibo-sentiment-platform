"""
爬虫服务 - 生产级封装
整合热点话题爬取、MediaCrawler数据同步的完整流程
基于已测试的run_full_crawler.py和sync_crawler_data.py
"""
import os
import sys
import re
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime

# 添加项目路径以便导入crawl_hot_topics
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import db
from app.models import Topic, WeiboPost
from crawl_hot_topics import HotTopicCrawler


class CrawlerService:
    """爬虫服务 - 封装所有爬虫操作"""
    
    # 敏感词列表
    SENSITIVE_KEYWORDS = [
        '习近平', '李克强', '国务院', '政府', '中央',
        '主席', '总理', '述职', '政治', '党',
        '失业率', '经济', '国会', '议员'
    ]
    
    def __init__(self):
        self.hot_topic_crawler = None
        self.is_running = False
        
    def _is_sensitive_topic(self, topic_name: str) -> bool:
        """检查话题是否包含敏感词"""
        for keyword in self.SENSITIVE_KEYWORDS:
            if keyword in topic_name:
                return True
        return False
    
    def crawl_hot_topics(self, limit: int = 10, filter_sensitive: bool = True) -> Dict:
        """
        爬取微博热点话题
        
        Args:
            limit: 要获取的话题数量
            filter_sensitive: 是否过滤敏感话题
            
        Returns:
            {
                'status': 'success' | 'error',
                'topics_added': int,
                'topics_filtered': int,
                'topics': [{'name': str, 'tag': str, 'id': int, 'is_new': bool}],
                'message': str
            }
        """
        try:
            # 初始化爬虫
            self.hot_topic_crawler = HotTopicCrawler()
            
            # 爬取更多话题以便过滤后还有足够数量
            fetch_limit = limit * 2 if filter_sensitive else limit
            hot_topics = self.hot_topic_crawler.get_hot_topics(limit=fetch_limit)
            
            if not hot_topics:
                return {
                    'status': 'error',
                    'message': '未能获取热点话题',
                    'topics_added': 0,
                    'topics': []
                }
            
            # 过滤敏感话题
            filtered_topics = []
            filtered_count = 0
            
            for topic_data in hot_topics:
                topic_text = topic_data['topic']
                topic_name = topic_text.replace('#', '').strip()
                
                if filter_sensitive and self._is_sensitive_topic(topic_name):
                    filtered_count += 1
                    continue
                
                filtered_topics.append(topic_data)
                
                if len(filtered_topics) >= limit:
                    break
            
            # 保存到数据库
            added_count = 0
            topics_info = []
            
            for topic_data in filtered_topics:
                topic_text = topic_data['topic']
                topic_name = topic_text.replace('#', '').strip()
                topic_tag = topic_text if topic_text.startswith('#') else f"#{topic_text}#"
                
                # 检查是否已存在
                existing = Topic.query.filter_by(topic_tag=topic_tag).first()
                
                if not existing:
                    new_topic = Topic(
                        topic_name=topic_name,
                        topic_tag=topic_tag,
                        is_active=True,
                        created_at=datetime.utcnow()
                    )
                    db.session.add(new_topic)
                    db.session.flush()  # 获取ID
                    added_count += 1
                    
                    topics_info.append({
                        'name': topic_name,
                        'tag': topic_tag,
                        'id': new_topic.id,
                        'is_new': True
                    })
                else:
                    topics_info.append({
                        'name': topic_name,
                        'tag': topic_tag,
                        'id': existing.id,
                        'is_new': False
                    })
            
            db.session.commit()
            
            # 更新MediaCrawler配置
            if topics_info:
                keywords = [t['name'] for t in topics_info[:5]]
                self._update_mediacrawler_config(keywords)
            
            return {
                'status': 'success',
                'topics_added': added_count,
                'topics_filtered': filtered_count,
                'topics': topics_info,
                'message': f'成功添加 {added_count} 个新话题, 过滤 {filtered_count} 个敏感话题'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'status': 'error',
                'message': f'爬取失败: {str(e)}',
                'topics_added': 0,
                'topics': []
            }
        finally:
            if self.hot_topic_crawler:
                self.hot_topic_crawler.close_browser()
    
    def search_topic(self, keyword: str) -> Dict:
        """
        搜索指定话题（用于前端输入）
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            {
                'status': 'success' | 'error',
                'topic_id': int,
                'topic_name': str,
                'is_new': bool,
                'message': str
            }
        """
        try:
            # 检查话题是否已存在
            topic_tag = f"#{keyword}#"
            existing = Topic.query.filter(
                (Topic.topic_name == keyword) |
                (Topic.topic_tag == topic_tag)
            ).first()
            
            if existing:
                topic_id = existing.id
                is_new = False
                message = f'话题已存在: {existing.topic_name}'
            else:
                # 创建新话题
                new_topic = Topic(
                    topic_name=keyword,
                    topic_tag=topic_tag,
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.session.add(new_topic)
                db.session.commit()
                
                topic_id = new_topic.id
                is_new = True
                message = f'创建新话题: {keyword}'
            
            # 更新MediaCrawler配置为单个关键词
            self._update_mediacrawler_config([keyword])
            
            return {
                'status': 'success',
                'topic_id': topic_id,
                'topic_name': keyword,
                'is_new': is_new,
                'message': message
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'status': 'error',
                'message': f'搜索话题失败: {str(e)}'
            }
    
    def _update_mediacrawler_config(self, keywords: List[str]) -> bool:
        """
        更新MediaCrawler配置文件的关键词
        
        Args:
            keywords: 关键词列表
            
        Returns:
            是否成功更新
        """
        try:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'MediaCrawler', 'config', 'base_config.py'
            )
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config_content = f.read()
            
            keywords_str = ",".join(keywords[:5])  # 最多5个关键词
            new_content = re.sub(
                r'KEYWORDS = "[^"]*"',
                f'KEYWORDS = "{keywords_str}"',
                config_content
            )
            
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
            
        except Exception as e:
            print(f"[CrawlerService] 更新配置失败: {e}")
            return False
    
    def sync_mediacrawler_data(self) -> Dict:
        """
        从MediaCrawler同步数据到主数据库
        基于sync_crawler_data.py的逻辑
        
        Returns:
            {
                'status': 'success' | 'error',
                'posts_added': int,
                'posts_skipped': int,
                'message': str
            }
        """
        try:
            # 修复: 从 app/services/crawler_service.py 到项目根目录
            # __file__: backend/app/services/crawler_service.py
            # dirname 1: backend/app/services
            # dirname 2: backend/app
            # dirname 3: backend
            # dirname 4: project_root
            current_file = os.path.abspath(__file__)
            services_dir = os.path.dirname(current_file)  # backend/app/services
            app_dir = os.path.dirname(services_dir)  # backend/app
            backend_dir = os.path.dirname(app_dir)  # backend
            project_root = os.path.dirname(backend_dir)  # 项目根目录
            mc_db_path = os.path.join(project_root, 'MediaCrawler', 'database', 'sqlite_tables.db')
            
            print(f"[CrawlerService] Current file: {current_file}")
            print(f"[CrawlerService] Backend dir: {backend_dir}")
            print(f"[CrawlerService] Project root: {project_root}")
            print(f"[CrawlerService] MC DB path: {mc_db_path}")
            print(f"[CrawlerService] DB exists: {os.path.exists(mc_db_path)}")
            
            if not os.path.exists(mc_db_path):
                return {
                    'status': 'error',
                    'message': f'MediaCrawler数据库不存在: {mc_db_path}',
                    'posts_added': 0,
                    'posts_skipped': 0
                }
            
            mc_conn = sqlite3.connect(mc_db_path)
            mc_conn.row_factory = sqlite3.Row
            mc_cursor = mc_conn.cursor()
            
            # 查询数据
            mc_cursor.execute("SELECT * FROM weibo_note ORDER BY add_ts DESC")
            notes = mc_cursor.fetchall()
            
            mc_cursor.execute("SELECT * FROM weibo_note_comment ORDER BY add_ts DESC")
            comments = mc_cursor.fetchall()
            
            added_posts = 0
            skipped_posts = 0
            
            # 同步微博
            for note in notes:
                added, skipped = self._sync_single_note(note)
                added_posts += added
                skipped_posts += skipped
                
                if added_posts % 10 == 0 and added_posts > 0:
                    db.session.commit()
            
            # 同步评论
            for comment in comments:
                added, skipped = self._sync_single_comment(comment)
                added_posts += added
                skipped_posts += skipped
                
                if added_posts % 10 == 0:
                    db.session.commit()
            
            db.session.commit()
            mc_conn.close()
            
            return {
                'status': 'success',
                'posts_added': added_posts,
                'posts_skipped': skipped_posts,
                'message': f'同步完成: 新增{added_posts}条, 跳过{skipped_posts}条'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'status': 'error',
                'message': f'同步失败: {str(e)}',
                'posts_added': 0,
                'posts_skipped': 0
            }
    
    def _safe_get(self, row, key, default=''):
        """安全获取sqlite3.Row的值"""
        try:
            return row[key] if row[key] is not None else default
        except (KeyError, IndexError):
            return default
    
    def _sync_single_note(self, note) -> tuple:
        """同步单条微博"""
        try:
            note_id = str(note['note_id'])
            if WeiboPost.query.filter_by(weibo_id=note_id).first():
                return 0, 1
            
            content = self._safe_get(note, 'content', '')
            topic = self._find_topic_for_content(content, self._safe_get(note, 'source_keyword', ''))
            
            if not topic:
                return 0, 1
            
            post = WeiboPost(
                topic_id=topic.id,
                weibo_id=note_id,
                content=content,
                topic_text=topic.topic_tag,
                comment_text=content,
                user_nickname=self._safe_get(note, 'nickname', '未知用户'),
                user_fans_count=0,
                publish_time=self._parse_timestamp(self._safe_get(note, 'create_time')),
                likes_count=self._safe_int(self._safe_get(note, 'liked_count')),
                reposts_count=self._safe_int(self._safe_get(note, 'shared_count')),
                comments_count=self._safe_int(self._safe_get(note, 'comments_count')),
                location=self._safe_get(note, 'ip_location', ''),
                created_at=datetime.utcnow()
            )
            
            db.session.add(post)
            return 1, 0
            
        except Exception as e:
            print(f"[CrawlerService] Error syncing note: {e}")
            return 0, 0
    
    def _sync_single_comment(self, comment) -> tuple:
        """同步单条评论"""
        try:
            comment_id = str(comment['comment_id'])
            if WeiboPost.query.filter_by(weibo_id=comment_id).first():
                return 0, 1
            
            content = self._safe_get(comment, 'content', '')
            topic = self._find_topic_for_content(content, None)
            
            if not topic:
                return 0, 1
            
            post = WeiboPost(
                topic_id=topic.id,
                weibo_id=comment_id,
                content=content,
                topic_text=topic.topic_tag,
                comment_text=content,
                user_nickname=self._safe_get(comment, 'nickname', '未知用户'),
                user_fans_count=0,
                publish_time=self._parse_timestamp(self._safe_get(comment, 'create_time')),
                likes_count=self._safe_int(self._safe_get(comment, 'comment_like_count')),
                reposts_count=0,
                comments_count=self._safe_int(self._safe_get(comment, 'sub_comment_count')),
                location=self._safe_get(comment, 'ip_location', ''),
                created_at=datetime.utcnow()
            )
            
            db.session.add(post)
            return 1, 0
            
        except Exception as e:
            print(f"[CrawlerService] Error syncing comment: {e}")
            return 0, 0
    
    def _find_topic_for_content(self, content: str, source_keyword: Optional[str]) -> Optional[Topic]:
        """为内容查找话题 - 使用多层匹配策略"""
        
        # 策略1: 从内容提取话题标签 (#话题名#)
        if content:
            match = re.search(r'#([^#]+)#', content)
            if match:
                topic_name = match.group(1).strip()
                topic = Topic.query.filter(
                    (Topic.topic_name == topic_name) |
                    (Topic.topic_tag.contains(topic_name))
                ).first()
                if topic:
                    print(f"[Sync] 精确匹配话题标签: {topic.topic_name}")
                    return topic
        
        # 策略2: 使用source_keyword精确匹配
        if source_keyword:
            topic = Topic.query.filter(
                (Topic.topic_name == source_keyword) |
                (Topic.topic_tag.contains(source_keyword))
            ).first()
            if topic:
                print(f"[Sync] 精确匹配source_keyword: {topic.topic_name}")
                return topic
        
        # 策略3: source_keyword模糊匹配 - 检查是否包含任何话题关键词
        if source_keyword:
            all_topics = Topic.query.filter_by(is_active=True).all()
            for topic in all_topics:
                # 检查source_keyword是否包含话题名
                if topic.topic_name in source_keyword or source_keyword in topic.topic_name:
                    print(f"[Sync] 模糊匹配source_keyword '{source_keyword}' -> {topic.topic_name}")
                    return topic
        
        # 策略4: 从内容模糊匹配 - 检查内容是否包含任何话题关键词
        if content:
            all_topics = Topic.query.filter_by(is_active=True).all()
            for topic in all_topics:
                if topic.topic_name in content:
                    print(f"[Sync] 内容包含话题名: {topic.topic_name}")
                    return topic
        
        # 策略5: 使用默认话题(第一个活跃话题)
        default_topic = Topic.query.filter_by(is_active=True).first()
        if default_topic:
            print(f"[Sync] 使用默认话题: {default_topic.topic_name}")
            return default_topic
        
        # 如果都没有话题,返回None
        print(f"[Sync] ⚠️  无可用话题,跳过此条数据")
        return None
    
    def _parse_timestamp(self, ts) -> datetime:
        """解析时间戳"""
        try:
            if not ts:
                return datetime.now()
            if isinstance(ts, (int, float)):
                if ts > 10000000000:
                    return datetime.fromtimestamp(ts / 1000)
                else:
                    return datetime.fromtimestamp(ts)
            return datetime.now()
        except:
            return datetime.now()
    
    def _safe_int(self, value) -> int:
        """安全转换为整数"""
        try:
            if value is None or value == '':
                return 0
            return int(value)
        except:
            return 0
    
    def get_status(self) -> Dict:
        """获取爬虫状态"""
        current_file = os.path.abspath(__file__)
        services_dir = os.path.dirname(current_file)
        app_dir = os.path.dirname(services_dir)
        backend_dir = os.path.dirname(app_dir)
        project_root = os.path.dirname(backend_dir)
        mc_db_path = os.path.join(project_root, 'MediaCrawler', 'database', 'sqlite_tables.db')
        
        return {
            'status': 'ready',
            'mediacrawler_db_exists': os.path.exists(mc_db_path),
            'topics_count': Topic.query.count(),
            'posts_count': WeiboPost.query.count(),
            'is_running': self.is_running
        }
