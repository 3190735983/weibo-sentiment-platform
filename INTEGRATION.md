# 集成说明文档

## 集成完成内容

### 1. 情感分析模型集成 ✅

**位置**: `backend/app/services/sentiment_service.py`

**功能**:
- 加载LightGBM情感分析模型
- 提供单条文本预测接口
- 批量预测优化
- 情感分布统计

**API接口**:
- `POST /api/sentiment/analyze` - 分析话题情感
- `GET /api/sentiment/results?topic_id=X` - 获取情感分布
- `POST /api/sentiment/predict` - 预测单条文本

**使用示例**:
```python
# 预测单条文本
POST /api/sentiment/predict
{
    "text": "这个产品真的很好用！"
}

# 分析话题
POST /api/sentiment/analyze
{
    "topic_id": 1
}
```

### 2. MediaCrawler爬虫集成 ✅

**位置**: `backend/app/services/mediacrawler_wrapper.py`

**功能**:
- 调用MediaCrawler执行爬取任务
- 支持关键词搜索模式
- 自动同步JSON数据到主数据库
- 数据清洗和去重

**工作流程**:
1. 修改MediaCrawler配置文件
2. 使用subprocess调用MediaCrawler
3. 等待爬取完成
4. 读取JSON数据文件
5. 同步到主数据库（WeiboPost表）

**注意事项**:
- 需要先在MediaCrawler目录运行 `uv sync` 安装依赖
- 首次使用需要扫码登录
- 登录状态会保存在 `browser_data` 目录

### 3. 热点话题发现 ✅

**位置**: `backend/app/services/hot_topic_service.py`

**功能**:
- 使用Selenium访问微博热搜榜
- 提取热门话题列表
- 自动添加到系统

**API接口**:
- `POST /api/crawler/discover-hot-topics` - 发现热点话题

**使用示例**:
```python
POST /api/crawler/discover-hot-topics
{
    "limit": 10
}
```

### 4. 爬虫协调器 ✅

**位置**: `backend/app/services/crawler_service.py`

**功能**:
- 完整的数据流水线
- 热点发现 → 爬取数据 → 情感分析
- 支持单个话题或批量处理

**API接口**:
- `POST /api/crawler/start` - 启动完整流程
- `POST /api/crawler/crawl-topic/<topic_id>` - 爬取单个话题
- `POST /api/crawler/stop` - 停止爬虫
- `GET /api/crawler/status` - 获取状态

**完整流程示例**:
```python
# 1. 发现热点话题
POST /api/crawler/discover-hot-topics
{
    "limit": 5
}

# 2. 爬取特定话题
POST /api/crawler/crawl-topic/1
{
    "max_notes": 100,
    "max_comments": 50
}

# 3. 分析情感
POST /api/sentiment/analyze
{
    "topic_id": 1
}

# 4. 查看结果
GET /api/sentiment/results?topic_id=1
```

## 数据流转

```
热点话题榜
    ↓
[HotTopicService.get_hot_topics()]
    ↓
Topic表（新增话题）
    ↓
[MediaCrawlerWrapper.crawl_by_keywords()]
    ↓
MediaCrawler爬取 → JSON文件
    ↓
[sync_data_from_json()]
    ↓
WeiboPost表（微博和评论数据）
    ↓
[SentimentService.analyze()]
    ↓
SentimentResult表（情感分析结果）
```

## 文件说明

### 新增服务文件
- `sentiment_service.py` - 情感分析服务
- `mediacrawler_wrapper.py` - MediaCrawler封装
- `hot_topic_service.py` - 热点话题服务
- `crawler_service.py` - 爬虫协调器（更新）

### 更新的API文件
- `api/crawler.py` - 新增热点发现和单话题爬取接口
- `api/sentiment.py` - 集成实际模型预测

### 依赖更新
- 新增：`joblib`, `lightgbm`, `selenium`

## 使用指南

### 首次使用

1. **安装依赖**:
```bash
cd backend
.\venv\Scripts\pip install -r requirements.txt
```

2. **配置MediaCrawler**:
```bash
cd MediaCrawler
uv sync
uv run playwright install
```

3. **首次登录**:
- 运行爬虫时会弹出浏览器
- 扫描二维码登录微博
- 登录状态会保存，后续无需重复登录

### 日常使用

**场景1：发现并分析热点话题**
```bash
# 通过API调用
POST /api/crawler/start
{
    "discover_hot_topics": true
}
```

**场景2：爬取特定话题**
```bash
# 先添加话题
POST /api/manage/topics
{
    "topic_name": "人工智能",
    "topic_tag": "#人工智能#"
}

# 然后爬取
POST /api/crawler/crawl-topic/1
```

**场景3：单独测试情感预测**
```bash
POST /api/sentiment/predict
{
    "text": "今天天气真好！"
}
```

## 故障排查

### MediaCrawler无法启动
- 检查MediaCrawler目录是否存在
- 检查是否已运行 `uv sync`
- 检查uv命令是否可用

### 情感模型加载失败
- 检查 `deployed_ml_models/lightgbm_classifier.joblib` 是否存在
- 检查joblib和lightgbm是否已安装

### Selenium浏览器问题
- 确保已安装Chrome浏览器
- 检查ChromeDriver版本匹配
- 可以在代码中启用headless模式

## 性能优化建议

1. **批量处理**: 使用 `batch_predict()` 而不是循环调用 `predict()`
2. **异步爬取**: 可以将爬虫放到后台任务队列（如Celery）
3. **缓存**: 对已爬取的数据做好去重标记
4. **限流**: MediaCrawler配置中设置合理的爬取间隔

## 下一步开发

- [ ] 前端界面对接新增API
- [ ] 可视化图表展示情感分布
- [ ] 定时任务自动化
- [ ] 数据导出功能
