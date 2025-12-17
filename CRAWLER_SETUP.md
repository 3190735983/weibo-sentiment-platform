# MediaCrawler依赖安装指南和测试

## 问题诊断

MediaCrawler安装失败的原因是需要C++编译工具来编译某些Python包（如numpy、pandas等）。

## 解决方案

### 方案1：安装Visual C++ Build Tools（推荐）

1. 下载安装器：
   https://visualstudio.microsoft.com/visual-cpp-build-tools/

2. 安装时选择：
   - "使用C++的桌面开发"
   - 确保勾选 "MSVC" 和 "Windows SDK"

3. 安装完成后重启电脑

4. 重新安装MediaCrawler依赖：
```bash
cd MediaCrawler
pip install -r requirements.txt
playwright install chromium
```

### 方案2：使用预编译的wheel包

```bash
cd MediaCrawler

# 使用清华镜像源安装
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

### 方案3：跳过MediaCrawler，使用简化爬虫

如果暂时无法解决依赖问题，可以：
1. 先使用热点话题爬取功能
2. 手动添加话题到系统
3. 使用测试数据继续开发其他功能

## 测试热点话题爬取

运行测试脚本：
```bash
cd backend
.\venv\Scripts\python.exe test_hot_topics.py
```

这会：
1. 打开浏览器访问微博热搜榜
2. 提取前10个热点话题
3. 选择性添加到数据库

## 备用方案：手动爬虫

如果Selenium也有问题，可以使用requests简化版：

```python
import requests
from bs4 import BeautifulSoup

def get_hot_topics_simple():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get('https://s.weibo.com/top/summary', headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        topics = []
        # 根据实际HTML结构提取
        for item in soup.select('tbody tr')[:10]:
            topic_elem = item.select_one('.td-02 a')
            if topic_elem:
                topics.append(topic_elem.text.strip())
        
        return topics
    except Exception as e:
        print(f"Error: {e}")
        return []
```

## 当前可用功能

即使没有MediaCrawler，系统仍可以：
1. ✅ 使用测试数据
2. ✅ 运行情感分析
3. ✅ 展示前端界面
4. ✅ 测试API功能
5. ✅ 热点话题爬取（Selenium）

## 下一步

优先级顺序：
1. 测试热点话题爬取 → `test_hot_topics.py`
2. 如果成功，添加话题到数据库
3. 然后决定是否需要解决MediaCrawler依赖

建议：先测试热点话题功能，看看是否能正常工作！
