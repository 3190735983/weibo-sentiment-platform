import requests
import csv
import time
import json

def get_new_cookie():
    """获取新cookie的步骤"""
    print("=" * 60)
    print("🔑 需要更新Cookie！")
    print("=" * 60)
    print("获取新Cookie的步骤：")
    print("1. 打开浏览器，访问 https://weibo.com")
    print("2. 登录你的微博账号")
    print("3. 按F12打开开发者工具")
    print("4. 切换到 Network（网络）标签")
    print("5. 刷新微博页面")
    print("6. 在请求列表中找到任意一个请求（如 hotflow）")
    print("7. 在 Request Headers（请求头）中找到 Cookie")
    print("8. 复制整个Cookie字符串")
    print("=" * 60)
    return input("请粘贴新的Cookie值: ").strip()

def crawl_with_cookie(weibo_url, cookie=None):
    """使用cookie爬取"""
    
    # 提取参数
    weibo_id = weibo_url.split('id=')[1].split('&')[0] if 'id=' in weibo_url else ''
    user_id = weibo_url.split('uid=')[1].split('&')[0] if 'uid=' in weibo_url else ''
    
    filename = f"微博{weibo_id}_评论.csv"
    
    # 如果没有提供cookie，尝试从文件读取或要求输入
    if not cookie:
        try:
            with open('weibo_cookie.txt', 'r', encoding='utf-8') as f:
                cookie = f.read().strip()
                print(f"📁 从文件读取cookie，长度: {len(cookie)} 字符")
        except:
            cookie = get_new_cookie()
            # 保存cookie到文件
            with open('weibo_cookie.txt', 'w', encoding='utf-8') as f:
                f.write(cookie)
    
    # 请求头（包含cookie）
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': f'https://weibo.com/{user_id}',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cookie': cookie,  # 关键！添加cookie
        'x-requested-with': 'XMLHttpRequest',
    }
    
    print(f"🎯 开始爬取微博 {weibo_id}...")
    print(f"📁 输出: {filename}")
    
    # 初始化CSV
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        csv.writer(f).writerow(['id', '用户名', '评论内容', '点赞数', '时间'])
    
    base_url = "https://weibo.com/ajax/statuses/buildComments"
    params = {
        'is_reload': 1,
        'id': weibo_id,
        'is_show_bulletin': 2,
        'is_mix': 0,
        'count': 20,
        'uid': user_id,
        'fetch_level': 0,
        'locale': 'zh-CN'
    }
    
    max_id = 0
    page = 1
    total = 0
    
    while page <= 100:  # 最多100页
        print(f"📄 第 {page} 页...")
        
        if max_id:
            params['max_id'] = max_id
        elif 'max_id' in params:
            del params['max_id']
        
        try:
            response = requests.get(base_url, headers=headers, params=params, timeout=15)
            
            print(f"📥 状态码: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ 请求失败")
                if response.status_code == 403:
                    print("🔒 访问被拒绝，cookie可能已过期")
                    # 尝试更新cookie
                    new_cookie = get_new_cookie()
                    headers['Cookie'] = new_cookie
                    # 保存新cookie
                    with open('weibo_cookie.txt', 'w', encoding='utf-8') as f:
                        f.write(new_cookie)
                    print("🔄 使用新cookie重试...")
                    continue
                break
            
            data = response.json()
            
            # 检查响应内容
            if 'ok' in data and 'url' in data:
                print(f"⚠️ 需要登录或重定向: {data.get('url', '')}")
                print("请更新cookie！")
                break
            
            if 'data' not in data:
                print(f"❌ 无数据字段")
                print(f"响应: {data}")
                break
            
            comments = data.get('data', [])
            
            if not comments:
                print("✅ 没有更多评论")
                break
            
            # 保存数据
            with open(filename, 'a', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                for comment in comments:
                    try:
                        writer.writerow([
                            comment.get('id', ''),
                            comment.get('user', {}).get('screen_name', ''),
                            comment.get('text_raw', '').replace('\n', ' ')[:500],  # 限制长度
                            comment.get('like_counts', 0),
                            comment.get('created_at', '')
                        ])
                    except:
                        continue
            
            total += len(comments)
            print(f"✅ 获取 {len(comments)} 条，累计 {total} 条")
            
            # 下一页
            next_max_id = data.get('max_id', 0)
            if not next_max_id:
                print("✅ 已获取所有评论")
                break
            
            max_id = next_max_id
            page += 1
            time.sleep(1.5)
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            break
    
    print(f"🎉 完成！共获取 {total} 条评论")
    return total > 0  # 返回是否成功

# 方案2：使用简化版（不依赖cookie）
def simple_crawl(weibo_url):
    """简化版爬虫，适合公开内容"""
    print("🚀 使用简化版爬虫...")
    
    weibo_id = weibo_url.split('id=')[1].split('&')[0]
    filename = f"微博{weibo_id}_评论.csv"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://weibo.com/',
    }
    
    print(f"正在爬取微博 {weibo_id}...")
    
    # 直接使用完整URL
    url = weibo_url
    page = 1
    
    while page <= 10:
        print(f"第 {page} 页...")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"状态码: {response.status_code}")
                break
            
            data = response.json()
            
            # 检查是否需要登录
            if 'ok' in data and 'url' in data:
                print("😔 需要登录才能查看此微博")
                print("请使用带cookie的版本")
                break
            
            if 'data' not in data:
                print("无数据")
                break
            
            comments = data.get('data', [])
            
            if not comments:
                print("没有更多评论")
                break
            
            # 保存数据
            mode = 'a' if page > 1 else 'w'
            with open(filename, mode, encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                if page == 1:
                    writer.writerow(['用户名', '内容', '点赞', '时间'])
                
                for comment in comments:
                    writer.writerow([
                        comment.get('user', {}).get('screen_name', ''),
                        comment.get('text_raw', '')[:200],
                        comment.get('like_counts', 0),
                        comment.get('created_at', '')
                    ])
            
            print(f"获取 {len(comments)} 条评论")
            
            # 下一页
            max_id = data.get('max_id', 0)
            if not max_id:
                break
            
            # 构建下一页URL
            if 'max_id=' in url:
                url = url.split('max_id=')[0] + 'max_id=' + str(max_id)
            else:
                url = url + '&max_id=' + str(max_id)
            
            page += 1
            time.sleep(2)
            
        except Exception as e:
            print(f"错误: {e}")
            break
    
    print(f"完成！数据保存到 {filename}")

if __name__ == "__main__":
    print("微博评论爬虫 v3.0")
    print("=" * 60)
    
    # 你的微博URL
    weibo_url = "https://weibo.com/ajax/statuses/buildComments?is_reload=1&id=5243449034408233&is_show_bulletin=2&is_mix=0&count=10&uid=6856915235&fetch_level=0&locale=zh-CN"
    
    print("请选择爬取方式:")
    print("1. 使用Cookie爬取（需要登录，能获取更多数据）")
    print("2. 简化版爬取（无需登录，但可能受限）")
    
    choice = input("请输入选择 (1/2): ").strip()
    
    if choice == "1":
        # 尝试从文件读取cookie
        try:
            with open('weibo_cookie.txt', 'r') as f:
                cookie = f.read()
                print(f"使用已有cookie（{len(cookie)}字符）")
                success = crawl_with_cookie(weibo_url, cookie)
                if not success:
                    print("😔 爬取失败，可能需要更新cookie")
                    input("按Enter键手动输入新cookie...")
                    crawl_with_cookie(weibo_url)  # 不带cookie，会提示输入
        except:
            print("未找到cookie文件，需要手动输入")
            crawl_with_cookie(weibo_url)
    
    elif choice == "2":
        simple_crawl(weibo_url)
    
    else:
        print("无效选择，使用简化版...")
        simple_crawl(weibo_url)