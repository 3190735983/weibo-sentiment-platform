# Phase 1 实施指南 - 核心数据采集与分析

## 当前进度
- [/] MediaCrawler环境配置
  - [/] 安装依赖包
  - [ ] 安装Playwright浏览器
  - [ ] 首次登录配置
- [ ] 情感模型测试
- [ ] 爬虫-分析流程测试

## Step 1: MediaCrawler环境配置

### 1.1 安装依赖（进行中）
```bash
cd MediaCrawler
pip install -r requirements.txt  # 正在执行
```

### 1.2 安装Playwright浏览器
```bash
# 等待依赖安装完成后执行
playwright install chromium
```

### 1.3 配置MediaCrawler
```bash
# 编辑配置文件
# 文件位置: MediaCrawler/config/base_config.py

修改以下配置:
- KEYWORDS = "测试关键词"  # 先用简单关键词测试
- CRAWLER_MAX_NOTES_COUNT = 10  # 测试时少爬一些
- SAVE_DATA_OPTION = "json"  # 使用JSON格式
- ENABLE_GET_COMMENTS = True  # 爬取评论
```

### 1.4 首次登录
```bash
# 在MediaCrawler目录下执行
python main.py --platform wb --lt qrcode --type search

# 会弹出浏览器，扫描二维码登录
# 登录成功后会保存在 browser_data 目录
# 以后不需要重复登录
```

## Step 2: 测试情感分析模型

### 2.1 创建测试脚本
```python
# 在backend目录创建 test_sentiment.py

import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.services.sentiment_service import SentimentAnalysisService

app = create_app()

with app.app_context():
    service = SentimentAnalysisService()
    
    # 测试单条预测
    test_texts = [
        "这个产品真的太棒了！非常满意",
        "质量太差了，完全不能用",
        "还可以吧，一般般"
    ]
    
    print("=== 情感分析测试 ===")
    for text in test_texts:
        result = service.predict(text)
        print(f"文本: {text}")
        print(f"结果: {result}")
        print("-" * 50)
```

### 2.2 运行测试
```bash
cd backend
.\venv\Scripts\python.exe test_sentiment.py
```

**预期输出**:
```
=== 情感分析测试 ===
文本: 这个产品真的太棒了！非常满意
结果: {'label': '正面', 'score': 0.95, 'intensity': 0.95}
--------------------------------------------------
文本: 质量太差了，完全不能用
结果: {'label': '负面', 'score': 0.92, 'intensity': 0.92}
--------------------------------------------------
文本: 还可以吧，一般般
结果: {'label': '中性', 'score': 0.78, 'intensity': 0.78}
```

## Step 3: 端到端流程测试

### 3.1 准备测试数据

**方式1: 使用API测试**
```bash
# 1. 添加测试话题
curl -X POST http://localhost:5000/api/manage/topics \
  -H "Content-Type: application/json" \
  -d '{
    "topic_name": "2024春节",
    "topic_tag": "#2024春节#"
  }'

# 2. 爬取该话题（会调用MediaCrawler）
curl -X POST http://localhost:5000/api/crawler/crawl-topic/1 \
  -H "Content-Type: application/json" \
  -d '{
    "max_notes": 10,
    "max_comments": 20
  }'

# 3. 执行情感分析
curl -X POST http://localhost:5000/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "topic_id": 1
  }'

# 4. 查看结果
curl http://localhost:5000/api/sentiment/results?topic_id=1
```

**方式2: 使用Postman**
- 导入以下Collection进行测试
- 按顺序执行各个请求

### 3.2 创建测试Collection

创建文件 `backend/tests/phase1_test.postman_collection.json`:
```json
{
  "info": {
    "name": "Phase 1 Tests",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "1. 添加话题",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "url": "http://localhost:5000/api/manage/topics",
        "body": {
          "mode": "raw",
          "raw": "{\"topic_name\":\"春节\",\"topic_tag\":\"#春节#\"}"
        }
      }
    },
    {
      "name": "2. 爬取话题",
      "request": {
        "method": "POST",
        "url": "http://localhost:5000/api/crawler/crawl-topic/1",
        "body": {
          "mode": "raw",
          "raw": "{\"max_notes\":10,\"max_comments\":20}"
        }
      }
    },
    {
      "name": "3. 情感分析",
      "request": {
        "method": "POST",
        "url": "http://localhost:5000/api/sentiment/analyze",
        "body": {
          "mode": "raw",
          "raw": "{\"topic_id\":1}"
        }
      }
    },
    {
      "name": "4. 查看结果",
      "request": {
        "method": "GET",
        "url": "http://localhost:5000/api/sentiment/results?topic_id=1"
      }
    }
  ]
}
```

## Step 4: 调试常见问题

### 问题1: MediaCrawler爬取失败
**症状**: subprocess timeout或返回错误

**解决**:
```bash
# 手动测试MediaCrawler是否能独立运行
cd MediaCrawler
python main.py --platform wb --lt cookie --type search

# 检查配置文件是否正确
# 检查登录状态是否有效
```

### 问题2: 情感模型加载失败
**症状**: Model file not found

**解决**:
```python
# 检查模型文件路径
import os
model_path = 'deployed_ml_models/lightgbm_classifier.joblib'
print(f"模型存在: {os.path.exists(model_path)}")

# 如果路径不对，在.env中配置正确路径
SENTIMENT_MODEL_PATH=/absolute/path/to/model.joblib
```

### 问题3: 数据同步失败
**症状**: synced_count = 0

**解决**:
```python
# 检查JSON数据文件
import json
json_file = 'MediaCrawler/data/weibo/xxx.json'
with open(json_file) as f:
    data = json.load(f)
    print(f"数据条数: {len(data.get('notes', []))}")

# 检查数据清洗逻辑
from app.utils.data_cleaner import is_valid_comment
text = "测试评论"
print(f"是否有效: {is_valid_comment(text)}")
```

## Step 5: 验收标准

✅ **MediaCrawler配置完成**:
- [ ] 能成功登录微博
- [ ] 能执行搜索并爬取数据
- [ ] JSON文件正确生成

✅ **情感模型正常**:
- [ ] 模型加载成功
- [ ] 预测结果准确
- [ ] 三种情感都能识别

✅ **端到端流程通畅**:
- [ ] 添加话题成功
- [ ] 爬取数据成功
- [ ] 数据同步到数据库
- [ ] 情感分析执行成功
- [ ] 能查看分析结果

## 下一步

完成Phase 1后，进入Phase 2:
- 开发话题管理界面
- 实现情感可视化图表

## 快速命令参考

```bash
# 启动后端服务
cd backend
.\venv\Scripts\python.exe run.py

# 测试MediaCrawler
cd MediaCrawler
python main.py --platform wb --lt cookie --type search

# 测试情感模型
cd backend
.\venv\Scripts\python.exe test_sentiment.py

# 查看数据库
sqlite3 backend/weibo_sentiment.db
SELECT COUNT(*) FROM weibo_posts;
SELECT COUNT(*) FROM sentiment_results;
```

## 进度追踪

- [/] Step 1: MediaCrawler环境配置
- [ ] Step 2: 情感模型测试
- [ ] Step 3: 端到端流程测试
- [ ] Step 4: 调试问题
- [ ] Step 5: 验收确认
