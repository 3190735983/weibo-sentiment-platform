"""
热点话题获取服务
从微博热搜榜获取热门话题
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re


class HotTopicService:
    """热点话题获取服务"""
    
    def __init__(self):
        self.browser = None
        self.browser_options = Options()
        # 可以设置为无头模式
        # self.browser_options.add_argument("--headless")
        self.browser_options.add_argument('--no-sandbox')
        self.browser_options.add_argument('--disable-dev-shm-usage')
    
    def init_browser(self):
        """初始化浏览器"""
        if self.browser is None:
            self.browser = webdriver.Chrome(options=self.browser_options)
            print("[HotTopic] Browser initialized")
    
    def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.quit()
            self.browser = None
            print("[HotTopic] Browser closed")
    
    def get_hot_topics(self, limit=10):
        """获取微博热搜话题
        
        Args:
            limit: 获取数量限制
        
        Returns:
            list: 话题列表，每项包含 {'rank': int, 'topic': str, 'heat': str}
        """
        try:
            self.init_browser()
            
            # 访问微博热搜页面
            hot_search_url = 'https://s.weibo.com/top/summary'
            self.browser.get(hot_search_url)
            time.sleep(3)  # 等待页面加载
            
            # 获取热搜列表
            topics = []
            
            # 不同的选择器尝试
            try:
                # 尝试方法1：通过tbody获取
                wait = WebDriverWait(self.browser, 10)
                table = wait.until(
                    EC.presence_of_element_located((By.ID, 'pl_top_realtimehot'))
                )
                
                rows = table.find_elements(By.TAG_NAME, 'tr')
                
                for idx, row in enumerate(rows[1:limit+1]):  # 跳过表头
                    try:
                        # 获取排名
                        rank_elem = row.find_element(By.CLASS_NAME, 'td-01')
                        rank = rank_elem.text.strip()
                        
                        # 获取话题
                        topic_elem = row.find_element(By.CLASS_NAME, 'td-02')
                        topic_link = topic_elem.find_element(By.TAG_NAME, 'a')
                        topic = topic_link.text.strip()
                        
                        # 获取热度
                        heat_elem = row.find_element(By.CLASS_NAME, 'td-03')
                        heat = heat_elem.text.strip()
                        
                        # 清理话题文本（移除图标等）
                        topic = self._clean_topic_text(topic)
                        
                        if topic:
                            topics.append({
                                'rank': int(rank) if rank.isdigit() else idx + 1,
                                'topic': topic,
                                'heat': heat
                            })
                            
                    except Exception as e:
                        print(f"[HotTopic] Error parsing row {idx}: {e}")
                        continue
                
            except Exception as e:
                print(f"[HotTopic] Error getting hot topics: {e}")
                # 尝试备用方法
                topics = self._get_hot_topics_fallback(limit)
            
            print(f"[HotTopic] Retrieved {len(topics)} hot topics")
            return topics
            
        except Exception as e:
            print(f"[HotTopic] Error: {e}")
            return []
        finally:
            self.close_browser()
    
    def _get_hot_topics_fallback(self, limit):
        """备用方法获取热点话题"""
        topics = []
        try:
            # 简化版：直接查找所有话题链接
            elements = self.browser.find_elements(By.CSS_SELECTOR, 'td.td-02 a')
            
            for idx, elem in enumerate(elements[:limit]):
                topic = elem.text.strip()
                topic = self._clean_topic_text(topic)
                
                if topic:
                    topics.append({
                        'rank': idx + 1,
                        'topic': topic,
                        'heat': ''
                    })
                    
        except Exception as e:
            print(f"[HotTopic] Fallback error: {e}")
        
        return topics
    
    def _clean_topic_text(self, text):
        """清理话题文本"""
        # 移除特殊字符和图标
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9#\s]', '', text)
        text = text.strip()
        
        # 确保话题格式
        if text and not text.startswith('#'):
            text = f'#{text}#'
        
        return text
    
    def get_topic_details(self, topic_name):
        """获取单个话题的详细信息
        
        Args:
            topic_name: 话题名称
        
        Returns:
            dict: 话题详细信息
        """
        try:
            self.init_browser()
            
            # 搜索话题
            search_url = f'https://s.weibo.com/weibo?q={topic_name}'
            self.browser.get(search_url)
            time.sleep(2)
            
            # 提取话题信息（根据实际页面结构调整）
            info = {
                'topic_name': topic_name,
                'topic_tag': topic_name if topic_name.startswith('#') else f'#{topic_name}#',
                'description': '',
                'post_count': 0
            }
            
            return info
            
        except Exception as e:
            print(f"[HotTopic] Error getting topic details: {e}")
            return None
        finally:
            self.close_browser()
