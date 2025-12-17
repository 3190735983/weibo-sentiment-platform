# 微博情感分析平台

基于 Vue3 + Flask 的微博话题情感分析系统，支持数据采集、情感分析、关键词提取、可视化展示和 AI 智能洞察。

## 项目结构

```
weibo-sentiment-platform/
├── backend/                 # Flask 后端
│   ├── app/
│   │   ├── models/         # 数据库模型
│   │   ├── api/            # API 路由
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── venv/               # Python 虚拟环境
│   ├── run.py              # 启动文件
│   └── requirements.txt    # Python 依赖
│
└── frontend/               # Vue3 前端
    ├── src/
    │   ├── api/           # API 封装
    │   ├── components/    # 组件
    │   ├── router/        # 路由配置
    │   ├── stores/        # 状态管理
    │   └── views/         # 页面
    └── package.json       # Node 依赖
```

## 技术栈

### 后端
- Flask 3.0
- SQLAlchemy (ORM)
- Flask-CORS (跨域)
- APScheduler (定时任务)
- jieba (中文分词)

### 前端
- Vue 3
- Vite
- Element Plus (UI 组件)
- ECharts (数据可视化)
- Vue Router (路由)
- Pinia (状态管理)
- Axios (HTTP 请求)

## 快速开始

### 后端启动

```bash
# 进入后端目录
cd backend

# 激活虚拟环境
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖（如果还未安装）
pip install -r requirements.txt

# 启动 Flask 服务
python run.py
```

后端服务将运行在 `http://localhost:5000`

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖（如果还未安装）
npm install

# 启动开发服务器
npm run dev
```

前端服务将运行在 `http://localhost:5173`

## 功能模块

### 1. 数据采集模块
- 实时爬取微博指定话题评论
- 支持多话题同时监控
- 自动数据清洗和去重
- 定时任务调度

### 2. 情感分析模块
- 基于训练好的情感分析模型
- 支持正面/负面/中性分类
- 情感强度评分

### 3. 关键词分析模块
- 高频词提取
- 停用词过滤
- 关键词演化追踪
- 词云生成

### 4. 数据可视化模块
- 热度趋势图
- 情感分布饼图
- 关键词词云
- 地域分析地图

### 5. AI 智能洞察模块
- 自动生成分析报告
- 异常检测与预警
- 智能问答

### 6. 数据管理模块
- 话题增删改查
- 历史数据查询
- 数据导出 (CSV/Excel/PDF)

## API 接口

所有 API 接口都在 `http://localhost:5000/api` 下：

- `/api/manage/topics` - 话题管理
- `/api/crawler/*` - 爬虫控制
- `/api/sentiment/*` - 情感分析
- `/api/keyword/*` - 关键词分析
- `/api/visualization/*` - 可视化数据
- `/api/ai/*` - AI 洞察

## 数据库

默认使用 SQLite 数据库，数据库文件: `backend/weibo_sentiment.db`

生产环境可配置 MySQL 或 PostgreSQL，修改 `backend/.env` 文件中的 `DATABASE_URI`

## 环境变量

### 后端 (backend/.env)
```
FLASK_ENV=development
DATABASE_URI=sqlite:///weibo_sentiment.db
SENTIMENT_MODEL_PATH=models/sentiment_model.pkl
OPENAI_API_KEY=your_api_key_here
```

### 前端 (frontend/.env)
```
VITE_API_BASE_URL=http://localhost:5000
```

## 注意事项

1. **情感分析模型**: 需要将训练好的模型文件放到指定路径，并在配置文件中指定路径
2. **爬虫实现**: 爬虫功能需要根据实际需求实现，建议使用 Selenium 或 Playwright
3. **可选依赖**: pandas、scikit-learn 等需要 C++ 编译器的包已从 requirements.txt 移除，如需使用请单独安装
4. **AI API**: 如需使用 AI 功能，需要配置 OpenAI 或其他大模型 API Key

## 下一步开发

框架已搭建完成，后续需要实现：

1. 爬虫具体逻辑 (`app/services/crawler_service.py`)
2. 情感分析模型集成 (`app/services/sentiment_service.py`)
3. 关键词提取算法完善 (`app/services/keyword_service.py`)
4. 可视化图表组件开发 (frontend)
5. AI 模型 API 集成 (`app/services/ai_service.py`)

## 开发团队分工

- **爬虫组**: 实现数据采集模块
- **数据处理组**: 实现关键词提取和数据预处理
- **前端开发组**: 完成页面和可视化功能

## License

MIT
