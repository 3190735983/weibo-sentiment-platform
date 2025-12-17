# 微博情感分析平台 - 最终使用指南

## 系统架构

```
热点话题爬取 → 话题数据库 → MediaCrawler评论爬取 → 数据同步 → 情感分析 → 前端展示
```

## 核心工作流程

### 方式一：完整自动流程

```bash
cd backend
.\venv\Scripts\python.exe run_full_crawler.py
```

**这个脚本会自动:**
1. 爬取微博热搜榜TOP10
2. 保存话题到主数据库
3. 更新MediaCrawler配置
4. 启动MediaCrawler爬取评论（需要扫码登录）
5. 数据保存到 MediaCrawler/data/weibo.db

### 方式二：分步执行

#### 步骤1: 爬取热点话题
```bash
cd backend
.\venv\Scripts\python.exe crawl_hot_topics.py
```

#### 步骤2: 导入话题到数据库
```bash
.\venv\Scripts\python.exe import_hot_topics.py
```

#### 步骤3: 运行MediaCrawler
```bash
cd ../MediaCrawler
python main.py --platform wb --lt qrcode --type search
```

#### 步骤4: 同步数据到主数据库
```bash
cd ../backend
.\venv\Scripts\python.exe sync_crawler_data.py
```

### 第三步：运行后端和前端

#### 启动后端API
```bash
cd backend
.\venv\Scripts\python.exe run.py
```

#### 启动前端
```bash
cd frontend
npm run dev
```

访问: http://localhost:5173

## 数据库说明

### 主数据库 (backend/instance/app.db)
- `topic` - 话题表
- `weibo_post` - 微博和评论表
- `sentiment_result` - 情感分析结果表

### MediaCrawler数据库 (MediaCrawler/data/weibo.db)
- `weibo_note` - 微博内容
- `weibo_note_comment` - 评论内容

## 关键文件

### 核心脚本
- `backend/crawl_hot_topics.py` - 热点话题爬取
- `backend/run_full_crawler.py` - 完整爬取流程
- `backend/sync_crawler_data.py` - 数据同步
- `backend/run.py` - Flask后端服务

### 配置文件
- `backend/.env` - 后端配置
- `MediaCrawler/config/base_config.py` - 爬虫配置

### 前端页面
- Dashboard - 总览和话题管理
- TopicDetail - 话题详情和分析
- DataManage - 数据管理和导出
- AIInsight - AI洞察

## 常见问题

### Q: MediaCrawler无法启动？
A: 确保Python 3.14兼容性修复已应用到 `MediaCrawler/main.py`

### Q: 爬虫登录失败？
A: 使用手机微博扫码登录，Cookie会自动保存

### Q: 数据同步失败？
A: 检查 MediaCrawler/data/weibo.db 是否存在

### Q: 情感分析不准？
A: 模型路径配置在 `backend/.env` 中的 `SENTIMENT_MODEL_PATH`

## 清理测试脚本

参考 `CLEANUP_GUIDE.md` 删除测试脚本。

## 下一步开发

1. 关键词分析服务
2. 可视化数据API
3. 数据导出功能
4. 定时任务调度
