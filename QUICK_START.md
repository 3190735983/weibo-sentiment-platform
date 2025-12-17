# Phase 1 快速开始指南（简化版）

## 🎯 目标
测试情感分析模型 + 验证基本功能

## ⚡ 快速步骤

### 1. 测试情感分析模型 ✅ 可以直接开始

```bash
# 在backend目录执行
cd backend
.\venv\Scripts\python.exe test_sentiment.py
```

**预期结果**: 看到情感分析测试结果

### 2. MediaCrawler问题解决方案

MediaCrawler依赖安装失败是因为需要编译工具。有两个选择：

**选项A: 简化测试（推荐）**
- 暂时跳过MediaCrawler
- 手动创建测试数据
- 专注测试情感分析功能

**选项B: 完整安装**
```bash
# 需要先安装Visual C++ Build Tools
# 下载: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# 然后重新安装依赖
```

### 3. 手动创建测试数据

```python
# 创建 backend/create_test_data.py

from app import create_app, db
from app.models import Topic, WeiboPost
from datetime import datetime

app = create_app()

with app.app_context():
    # 创建测试话题
    topic = Topic(
        topic_name="测试话题",
        topic_tag="#测试话题#",
        is_active=True
    )
    db.session.add(topic)
    db.session.commit()
    
    # 创建测试微博数据
    test_posts = [
        "这个产品真的太棒了！#测试话题# 强烈推荐给大家",
        "质量太差了#测试话题#，完全不能用，浪费钱",
        "#测试话题# 一般般，还可以吧",
    ]
    
    for i, content in enumerate(test_posts):
        post = WeiboPost(
            topic_id=topic.id,
            weibo_id=f"test_{i}",
            content=content,
            topic_text="#测试话题#",
            comment_text=content.replace("#测试话题#", "").strip(),
            user_nickname=f"测试用户{i}",
            publish_time=datetime.now(),
            created_at=datetime.utcnow()
        )
        db.session.add(post)
    
    db.session.commit()
    print(f"✅ 创建了1个话题和{len(test_posts)}条测试数据")
```

运行:
```bash
.\venv\Scripts\python.exe create_test_data.py
```

### 4. 测试情感分析API

```bash
# 测试分析接口
curl -X POST http://localhost:5000/api/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d "{\"topic_id\": 1}"

# 查看结果
curl http://localhost:5000/api/sentiment/results?topic_id=1
```

### 5. 测试单条预测

```bash
curl -X POST http://localhost:5000/api/sentiment/predict \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"这个产品真的很好用！\"}"
```

## ✅ 验收标准

- [x] 情感模型加载成功
- [x] 能进行单条预测
- [ ] 能批量分析数据
- [ ] API返回正确结果

## 🔧 如果遇到问题

**模型加载失败**:
```bash
# 检查模型文件是否存在
cd deployed_ml_models
dir lightgbm_classifier.joblib
```

**数据库错误**:
```bash
# 删除旧数据库重新创建
cd backend
del weibo_sentiment.db
.\venv\Scripts\python.exe run.py  # 重启服务会自动创建
```

## 📝 下一步

完成情感分析测试后:
1. 如果MediaCrawler安装成功 → 测试完整流程
2. 如果MediaCrawler失败 → 使用手动数据继续开发前端
