# 清理脚本列表

以下是可以删除的测试和调试脚本：

## Backend 测试脚本（可删除）
- `test_sentiment.py` - 情感模型测试
- `test_api.py` - API测试
- `test_hot_topics.py` - 热点话题测试（已有正式版本）
- `test_selenium.py` - Selenium测试
- `add_hot_topics.py` - 临时热点添加
- `add_topics_simple.py` - 简单话题添加
- `create_test_data.py` - 测试数据生成
- `generate_comments.py` - 评论生成测试
- `diagnose_selenium.py` - Selenium诊断

## Backend 保留脚本（重要）
- `crawl_hot_topics.py` - ✅ 热点话题爬取（保留）
- `run_full_crawler.py` - ✅ 完整爬取流程（保留）
- `sync_crawler_data.py` - ✅ 数据同步（保留）
- `import_hot_topics.py` - ✅ 导入热点（保留）
- `run.py` - ✅ Flask启动（保留）

## MediaCrawler
- `run_crawler.py` - 可删除（临时包装脚本）

## 核心工作流程

### 1. 获取热点话题并爬取
```bash
cd backend
.\venv\Scripts\python.exe run_full_crawler.py
```

这个脚本会：
1. 爬取微博热搜榜
2. 保存话题到数据库
3. 更新MediaCrawler配置
4. 启动MediaCrawler爬取评论
5. 数据保存到 MediaCrawler/data/weibo.db

### 2. 同步数据到主数据库
```bash
cd backend
.\venv\Scripts\python.exe sync_crawler_data.py
```

### 3. 运行情感分析
```bash
# 在API中调用或通过前端触发
```

### 4. 查看结果
访问前端：http://localhost:5173
