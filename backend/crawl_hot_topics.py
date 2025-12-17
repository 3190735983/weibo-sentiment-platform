"""
热点话题爬虫 - 基于auto_spider改进
使用Selenium爬取微博热搜榜 (无头模式)
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import re

class HotTopicCrawler:
    """微博热搜榜爬虫"""
    
    def __init__(self):
        # 浏览器配置 - 无头模式
        self.browser_options = Options()
        self.browser_options.add_argument("--headless")  # 无头模式，不显示浏览器窗口
        self.browser_options.add_argument('--no-sandbox')
        self.browser_options.add_argument('--disable-dev-shm-usage')
        self.browser = None
        
    def start_browser(self):
        """启动浏览器"""
        print("正在启动浏览器(无头模式)...")
        self.browser = webdriver.Chrome(options=self.browser_options)
        print("✅ 浏览器已启动")
        
    def get_hot_topics(self, limit=10):
        """获取热搜话题"""
        try:
            self.start_browser()
            
            # 访问热搜榜
            url = 'https://s.weibo.com/top/summary'
            print(f"正在访问: {url}")
            self.browser.get(url)
            time.sleep(3)  # 等待页面加载
            
            print(f"✅ 页面已打开: {self.browser.current_url}")
            
            # 提取热搜列表
            topics = []
            
            # 方法1：通过table tbody tr提取
            try:
                # 等待表格加载
                wait = WebDriverWait(self.browser, 10)
                table = wait.until(EC.presence_of_element_located((By.ID, 'pl_top_realtimehot')))
                
                print("找到热搜表格，开始提取...")
                
                # 获取所有行
                rows = table.find_elements(By.TAG_NAME, 'tr')
                print(f"找到 {len(rows)} 行数据")
                
                # 跳过表头，提取前limit条
                for idx, row in enumerate(rows[1:limit+1], 1):
                    try:
                        # 提取排名
                        rank_elem = row.find_element(By.CLASS_NAME, 'td-01')
                        rank = rank_elem.text.strip()
                        
                        # 提取话题
                        topic_elem = row.find_element(By.CLASS_NAME, 'td-02')
                        topic_link = topic_elem.find_element(By.TAG_NAME, 'a')
                        topic_text = topic_link.text.strip()
                        
                        # 提取热度
                        try:
                            heat_elem = row.find_element(By.CLASS_NAME, 'td-03')
                            heat = heat_elem.text.strip()
                        except:
                            heat = ''
                        
                        # 清理话题文本
                        topic_text = self._clean_topic(topic_text)
                        
                        if topic_text:
                            topics.append({
                                'rank': int(rank) if rank.isdigit() else idx,
                                'topic': topic_text,
                                'heat': heat
                            })
                            print(f"{idx}. {topic_text} (热度: {heat})")
                    
                    except Exception as e:
                        print(f"提取第{idx}行失败: {str(e)}")
                        continue
                
            except Exception as e:
                print(f"方法1失败: {str(e)}")
                print("尝试备用方法...")
                topics = self._fallback_method(limit)
            
            return topics
            
        except Exception as e:
            print(f"❌ 爬取失败: {str(e)}")
            return []
        
        finally:
            self.close_browser()
    
    def _fallback_method(self, limit):
        """备用提取方法"""
        topics = []
        try:
            # 直接查找所有话题链接
            topic_elements = self.browser.find_elements(By.CSS_SELECTOR, 'td.td-02 a')
            
            print(f"备用方法找到 {len(topic_elements)} 个话题")
            
            for idx, elem in enumerate(topic_elements[:limit], 1):
                try:
                    topic_text = elem.text.strip()
                    topic_text = self._clean_topic(topic_text)
                    
                    if topic_text:
                        topics.append({
                            'rank': idx,
                            'topic': topic_text,
                            'heat': ''
                        })
                        print(f"{idx}. {topic_text}")
                
                except Exception as e:
                    continue
        
        except Exception as e:
            print(f"备用方法也失败: {str(e)}")
        
        return topics
    
    def _clean_topic(self, text):
        """清理话题文本"""
        # 移除特殊字符，保留中英文数字
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', '', text)
        text = text.strip()
        
        # 添加话题标签
        if text and not text.startswith('#'):
            text = f'#{text}#'
        
        return text
    
    def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.quit()
            self.browser = None
            print("浏览器已关闭")


def main():
    """主函数"""
    print("=" * 70)
    print("微博热搜榜爬虫")
    print("=" * 70)
    
    crawler = HotTopicCrawler()
    
    try:
        # 获取前10个热搜
        hot_topics = crawler.get_hot_topics(limit=10)
        
        if hot_topics:
            print("\n" + "=" * 70)
            print(f"✅ 成功获取 {len(hot_topics)} 个热搜话题:")
            print("=" * 70)
            
            for topic in hot_topics:
                print(f"{topic['rank']}. {topic['topic']} ({topic['heat']})")
            
            # 保存到JSON
            with open('hot_topics.json', 'w', encoding='utf-8') as f:
                json.dump(hot_topics, f, ensure_ascii=False, indent=2)
            
            print("\n✅ 数据已保存到 hot_topics.json")
        else:
            print("\n❌ 未能获取热搜话题")
    
    except Exception as e:
        print(f"\n❌ 运行出错: {str(e)}")
    
    print("\n" + "=" * 70)
    print("完成！")
    print("==" * 70)


if __name__ == "__main__":
    main()
