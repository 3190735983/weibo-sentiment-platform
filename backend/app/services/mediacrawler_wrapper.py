"""
MediaCrawler封装服务
负责调用MediaCrawler爬虫并同步数据到主数据库
"""
import os
import subprocess
import json
import time
from datetime import datetime
from app.models import Topic, WeiboPost
from app.utils.data_cleaner import extract_topic_and_comment, is_valid_comment
from app import db


class MediaCrawlerWrapper:
    """MediaCrawler爬虫封装"""
    
    def __init__(self):
        # MediaCrawler项目路径
        # __file__: backend/app/services/mediacrawler_wrapper.py
        # dirname 1: backend/app/services  
        # dirname 2: backend/app
        # dirname 3: backend
        # dirname 4: project_root
        current_file = os.path.abspath(__file__)
        services_dir = os.path.dirname(current_file)
        app_dir = os.path.dirname(services_dir)
        backend_dir = os.path.dirname(app_dir)
        project_root = os.path.dirname(backend_dir)
        self.mediacrawler_dir = os.path.join(project_root, 'MediaCrawler')
        
        print(f"[MediaCrawler] Path: {self.mediacrawler_dir}")
        print(f"[MediaCrawler] Exists: {os.path.exists(self.mediacrawler_dir)}")
        
        self.is_running = False
        self.current_process = None
        
    def check_mediacrawler_exists(self):
        """检查MediaCrawler是否存在"""
        if not os.path.exists(self.mediacrawler_dir):
            print(f"[MediaCrawler] Directory not found: {self.mediacrawler_dir}")
            return False
        
        main_py = os.path.join(self.mediacrawler_dir, 'main.py')
        if not os.path.exists(main_py):
            print(f"[MediaCrawler] main.py not found")
            return False
            
        return True
    
    def crawl_by_keywords(self, keywords, max_notes=50, max_comments=100):
        """根据关键词爬取微博数据
        
        Args:
            keywords: 关键词字符串（多个关键词用逗号分隔）
            max_notes: 最大爬取微博数量
            max_comments: 每条微博最大爬取评论数
        
        Returns:
            dict: {'success': bool, 'message': str, 'data_file': str}
        """
        if not self.check_mediacrawler_exists():
            return {
                'success': False,
                'message': 'MediaCrawler not found',
                'data_file': None
            }
        
        try:
            # 修改MediaCrawler配置
            config_file = os.path.join(self.mediacrawler_dir, 'config', 'base_config.py')
            self._update_config(config_file, {
                'KEYWORDS': keywords,
                'CRAWLER_MAX_NOTES_COUNT': max_notes,
                'CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES': max_comments,
                'SAVE_DATA_OPTION': 'json',  # 使用JSON格式便于读取
                'ENABLE_GET_COMMENTS': True
            })
            
            # 调用MediaCrawler
            print(f"[MediaCrawler] Starting crawl for keywords: {keywords}")
            
            cmd = [
                'python', 'main.py',
                '--platform', 'wb',
                '--lt', 'qrcode',  # 使用二维码登录
                '--type', 'search'
            ]
            
            # 在MediaCrawler目录下执行
            self.current_process = subprocess.Popen(
                cmd,
                cwd=self.mediacrawler_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.is_running = True
            
            # 等待完成（或设置超时）
            stdout, stderr = self.current_process.communicate(timeout=600)  # 10分钟超时
            
            self.is_running = False
            
            if self.current_process.returncode == 0:
                # 查找生成的数据文件
                data_dir = os.path.join(self.mediacrawler_dir, 'data', 'weibo')
                data_file = self._find_latest_json_file(data_dir)
                
                return {
                    'success': True,
                    'message': 'Crawl completed successfully',
                    'data_file': data_file
                }
            else:
                print(f"[MediaCrawler] Error: {stderr}")
                return {
                    'success': False,
                    'message': f'Crawl failed: {stderr}',
                    'data_file': None
                }
                
        except subprocess.TimeoutExpired:
            self.current_process.kill()
            self.is_running = False
            return {
                'success': False,
                'message': 'Crawl timeout',
                'data_file': None
            }
        except Exception as e:
            self.is_running = False
            print(f"[MediaCrawler] Exception: {e}")
            return {
                'success': False,
                'message': str(e),
                'data_file': None
            }
    
    def sync_data_from_json(self, json_file, topic_id):
        """从MediaCrawler的JSON文件同步数据到主数据库
        
        Args:
            json_file: JSON数据文件路径
            topic_id: 关联的话题ID
        
        Returns:
            dict: {'synced_count': int, 'success': bool}
        """
        if not os.path.exists(json_file):
            return {'synced_count': 0, 'success': False, 'error': 'File not found'}
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            synced_count = 0
            
            # 处理微博帖子数据
            for note_data in data.get('notes', []):
                # 检查是否已存在
                weibo_id = str(note_data.get('note_id', ''))
                existing = WeiboPost.query.filter_by(weibo_id=weibo_id).first()
                
                if existing:
                    continue
                
                # 提取并清洗数据
                content = note_data.get('content', '')
                topic_text, comment_text = extract_topic_and_comment(content)
                
                # 验证评论有效性
                if not is_valid_comment(comment_text):
                    continue
                
                # 创建新记录
                post = WeiboPost(
                    topic_id=topic_id,
                    weibo_id=weibo_id,
                    content=content,
                    topic_text=topic_text,
                    comment_text=comment_text,
                    user_nickname=note_data.get('nickname', ''),
                    user_fans_count=self._parse_count(note_data.get('fans', '0')),
                    publish_time=self._parse_datetime(note_data.get('create_date_time')),
                    likes_count=self._parse_count(note_data.get('liked_count', '0')),
                    reposts_count=self._parse_count(note_data.get('shared_count', '0')),
                    comments_count=self._parse_count(note_data.get('comments_count', '0')),
                    location=note_data.get('ip_location', ''),
                    raw_data=json.dumps(note_data, ensure_ascii=False),
                    created_at=datetime.utcnow()
                )
                
                db.session.add(post)
                synced_count += 1
            
            db.session.commit()
            
            return {
                'synced_count': synced_count,
                'success': True
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"[MediaCrawler] Sync error: {e}")
            return {
                'synced_count': 0,
                'success': False,
                'error': str(e)
            }
    
    def _update_config(self, config_file, updates):
        """更新MediaCrawler配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for key, value in updates.items():
                if isinstance(value, str):
                    pattern = f'{key} = ".*?"'
                    replacement = f'{key} = "{value}"'
                elif isinstance(value, bool):
                    pattern = f'{key} = (True|False)'
                    replacement = f'{key} = {value}'
                else:
                    pattern = f'{key} = \\d+'
                    replacement = f'{key} = {value}'
                
                import re
                content = re.sub(pattern, replacement, content)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            print(f"[MediaCrawler] Config update error: {e}")
    
    def _find_latest_json_file(self, directory):
        """查找最新的JSON数据文件"""
        try:
            json_files = [
                os.path.join(directory, f)
                for f in os.listdir(directory)
                if f.endswith('.json')
            ]
            
            if not json_files:
                return None
            
            # 按修改时间排序，返回最新的
            latest_file = max(json_files, key=os.path.getmtime)
            return latest_file
            
        except Exception as e:
            print(f"[MediaCrawler] Find file error: {e}")
            return None
    
    def _parse_count(self, count_str):
        """解析数量字符串（处理'万'等单位）"""
        try:
            count_str = str(count_str).strip()
            if '万' in count_str:
                return int(float(count_str.replace('万', '')) * 10000)
            return int(count_str) if count_str.isdigit() else 0
        except:
            return 0
    
    def _parse_datetime(self, datetime_str):
        """解析日期时间字符串"""
        try:
            if not datetime_str:
                return None
            # MediaCrawler格式：'2024-12-16 20:30'
            return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
        except:
            return None
    
    def stop_crawl(self):
        """停止正在运行的爬虫"""
        if self.is_running and self.current_process:
            self.current_process.terminate()
            self.is_running = False
            return True
        return False
