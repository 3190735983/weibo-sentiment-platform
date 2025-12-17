"""
微博评论爬虫 - 基于auto_spider改进
爬取指定话题的微博和评论
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
import time
import json
import re
from datetime import datetime

class WeiboCommentCrawler:
    """微博评论爬虫"""
    
    def __init__(self):
        # 浏览器配置
        self.browser_options = Options()
        # self.browser_options.add_argument("--headless")  # 可开启无头模式
        self.browser_options.add_argument('--no-sandbox')
        self.browser_options.add_argument('--disable-dev-shm-usage')
        self.browser = None
        self.base_url = 'https://s.weibo.com/weibo'
        
    def start_browser(self):
        """启动浏览器"""
        print("正在启动浏览器...")
        self.browser = webdriver.Chrome(options=self.browser_options)
        print("✅ 浏览器已启动")
        
        # 加载cookie（如果有）
        try:
            with open('cookies.txt', 'r', encoding='utf-8') as f:
                cookies_list = json.load(f)
                self.browser.get('https://weibo.com')
                time.sleep(2)
                for cookie in cookies_list:
                    if isinstance(cookie.get('expiry'), float):
                        cookie['expiry'] = int(cookie['expiry'])
                    try:
                        self.browser.add_cookie(cookie)
                    except:
                        pass
                print("✅ Cookie已加载")
        except FileNotFoundError:
            print("ℹ️  未找到cookies.txt，将使用未登录状态爬取")
        except Exception as e:
            print(f"⚠️  Cookie加载失败: {e}")
    
    def search_keyword(self, keyword, max_posts=10):
        """搜索关键词并爬取微博"""
        try:
            # 构建搜索URL
            search_url = f'{self.base_url}?q={keyword}&Refer=index'
            print(f"\n正在搜索: {keyword}")
            print(f"URL: {search_url}")
            
            self.browser.get(search_url)
            time.sleep(3)
            
            # 切换到综合标签页（如果需要）
            try:
                click_list = self.browser.find_element(By.XPATH, '//div[@class="m-main-nav"]/ul/li[2]/a')
                click_list.click()
                time.sleep(2)
                print("✅ 切换到列表视图")
            except:
                print("ℹ️  已在列表视图")
            
            # 提取微博列表
            posts = []
            
            print(f"开始爬取前 {max_posts} 条微博...")
            
            # 获取微博URL列表
            data = etree.HTML(self.browser.page_source)
            post_urls = data.xpath('//p[@class="from"]/a[1]/@href')
            
            if len(post_urls) == 0:
                # 尝试另一种选择器
                post_urls = data.xpath('//div[@class="from"]/a[1]/@href')
            
            print(f"找到 {len(post_urls)} 条微博链接")
            
            # 爬取每条微博
            for index, url_single in enumerate(post_urls[:max_posts], 1):
                try:
                    post_data = self.crawl_single_post(url_single, index)
                    if post_data:
                        posts.append(post_data)
                        print(f"✅ [{index}/{max_posts}] 爬取成功")
                    time.sleep(1)  # 避免请求过快
                except Exception as e:
                    print(f"❌ [{index}/{max_posts}] 爬取失败: {str(e)}")
                    continue
            
            return posts
        
        except Exception as e:
            print(f"❌ 搜索失败: {str(e)}")
            return []
    
    def crawl_single_post(self, url_single, index):
        """爬取单条微博详情"""
        url = 'https:' + url_single if not url_single.startswith('http') else url_single
        
        print(f"  [{index}] 访问: {url}")
        self.browser.get(url)
        time.sleep(2)
        
        # 解析页面
        post = etree.HTML(self.browser.page_source)
        
        try:
            # 提取用户名
            names = post.xpath('//a[@usercard]/span[@title]/text()')
            if not names:
                names = post.xpath('//div[@class="head-info_nick"]/a/text()')
            username = names[0] if names else '未知用户'
            
            # 提取发文时间
            time_elem = post.xpath('//a[@title][@href][@class][1]/text()')
            publish_time = f'20{"".join(time_elem).strip()}' if time_elem else ''
            
            # 提取发送平台
            from1 = post.xpath('//div[@class="woo-box-flex"]/div[@title]/text()')
            from2 = post.xpath('//div[@class="woo-box-flex"]/div[contains(@class, "head-info_cut")]/text()')
            platform = ''.join(from1) + ''.join(from2)
            
            # 提取微博内容
            blogs = post.xpath('//div[contains(@class, "detail_text")]/div/text()')
            content = ''.join(blogs).strip()
            
            # 提取转发数
            forward = post.xpath('//span[@class="woo-pop-ctrl"]/div/span/text()')
            forward_count = self._parse_count(forward)
            
            # 提取评论数
            comments = post.xpath('//div[contains(@class, "woo-box-item-flex toolbar_item")]/div[contains(@class, "woo-box-flex")]/span/text()')
            comment_count = self._parse_count(comments)
            
            # 提取点赞数
            likes = post.xpath('//div[contains(@class, "toolbar_likebox")]/button/span[@class="woo-like-count"]/text()')
            like_count = self._parse_count(likes)
            
            post_data = {
                'username': username,
                'publish_time': publish_time,
                'platform': platform,
                'content': content,
                'forward_count': forward_count,
                'comment_count': comment_count,
                'like_count': like_count,
                'url': url
            }
            
            # 返回列表
            self.browser.back()
            
            return post_data
        
        except Exception as e:
            print(f"    解析失败: {str(e)}")
            self.browser.back()
            return None
    
    def _parse_count(self, count_list):
        """解析数量（处理'万'等单位）"""
        if not count_list:
            return 0
        
        count_str = ''.join(count_list).strip()
        
        # 处理空值
        if not count_str or count_str in [' 转发 ', ' 评论 ', '赞']:
            return 0
        
        # 处理'万'
        if '万' in count_str:
            try:
                num = float(count_str.replace('万', ''))
                return int(num * 10000)
            except:
                return 0
        
        # 处理普通数字
        try:
            return int(count_str)
        except:
            return 0
    
    def save_to_json(self, posts, keyword):
        """保存到JSON文件"""
        filename = f'weibo_posts_{keyword}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 数据已保存到: {filename}")
    
    def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.quit()
            self.browser = None
            print("浏览器已关闭")


def main():
    """主函数 - 测试爬虫"""
    print("=" * 70)
    print("微博评论爬虫测试")
    print("=" * 70)
    
    crawler = WeiboCommentCrawler()
    
    try:
        crawler.start_browser()
        
        # 测试爬取
        keyword = input("\n请输入要爬取的话题关键词（如：人工智能）: ").strip()
        if not keyword:
            keyword = "人工智能"
            print(f"使用默认关键词: {keyword}")
        
        max_posts = input("请输入要爬取的微博数量（默认5条）: ").strip()
        if not max_posts or not max_posts.isdigit():
            max_posts = 5
        else:
            max_posts = int(max_posts)
        
        print(f"\n开始爬取 '{keyword}' 的前 {max_posts} 条微博...")
        
        posts = crawler.search_keyword(keyword, max_posts)
        
        if posts:
            print(f"\n✅ 成功爬取 {len(posts)} 条微博:")
            for i, post in enumerate(posts, 1):
                print(f"\n{i}. {post['username']}")
                print(f"   内容: {post['content'][:50]}...")
                print(f"   点赞: {post['like_count']}, 转发: {post['forward_count']}, 评论: {post['comment_count']}")
            
            # 保存数据
            crawler.save_to_json(posts, keyword)
        else:
            print("\n❌ 未能爬取到数据")
    
    except Exception as e:
        print(f"\n❌ 运行出错: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        crawler.close_browser()
    
    print("\n" + "=" * 70)
    print("完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
