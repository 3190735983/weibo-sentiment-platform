# MediaCrawler - 微博数据爬虫（简化版）

> **重要说明**: 此项目已精简为仅支持微博平台的爬虫工具，其他平台代码已被删除。

## 📖 项目简介

这是 MediaCrawler 的微博专用简化版本，专注于微博平台的数据采集功能。

### ✨ 功能特性

| 平台   | 关键词搜索 | 指定帖子ID爬取 | 二级评论 | 指定创作者主页 | 登录态缓存 | IP代理池 |
| ------ | ---------- | -------------- | -------- | -------------- | ---------- | -------- |
| 微博   | ✅          | ✅              | ✅        | ✅              | ✅          | ✅        |

## 🚀 快速开始

### 📋 前置依赖

1. **Python 环境**: Python 3.11+
2. **Node.js**: >= 16.0.0
3. **uv 包管理器**（推荐）: [安装指南](https://docs.astral.sh/uv/getting-started/installation)

### 📦 安装依赖

```shell
# 进入项目目录
cd MediaCrawler

# 使用 uv 安装依赖
uv sync

# 安装浏览器驱动
uv run playwright install
```

### 🚀 运行爬虫

```shell
# 关键词搜索模式（从配置文件读取关键词）
uv run main.py --platform wb --lt qrcode --type search

# 指定帖子ID模式（从配置文件读取帖子ID列表）
uv run main.py --platform wb --lt qrcode --type detail

# 创作者主页模式（从配置文件读取用户ID列表）
uv run main.py --platform wb --lt qrcode --type creator

# 查看更多选项
uv run main.py --help
```

### ⚙️ 配置说明

#### 1. 基础配置 (`config/base_config.py`)

```python
# 平台设置（已固定为微博）
PLATFORM = "wb"

# 关键词设置
KEYWORDS = "你的关键词1,关键词2"

# 登录方式
LOGIN_TYPE = "qrcode"  # qrcode | phone | cookie

# 爬取类型
CRAWLER_TYPE = "search"  # search | detail | creator

# 数据保存方式
SAVE_DATA_OPTION = "db"  # csv | db | json | sqlite | excel

# 是否开启评论爬取
ENABLE_GET_COMMENTS = True

# 爬取数量控制
CRAWLER_MAX_NOTES_COUNT = 15
CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES = 10
```

#### 2. 微博配置 (`config/weibo_config.py`)

```python
# 搜索类型
WEIBO_SEARCH_TYPE = "default"

# 指定微博ID列表
WEIBO_SPECIFIED_ID_LIST = [
    "4982041758140155",
]

# 指定微博用户ID列表
WEIBO_CREATOR_ID_LIST = [
    "5533390220",
]
```

## 💾 数据存储

### 数据库表结构

项目包含三个主要数据表：

1. **weibo_note**: 存储微博帖子信息
2. **weibo_note_comment**: 存储微博评论信息
3. **weibo_creator**: 存储微博创作者信息

### 存储配置

在 `config/db_config.py` 中配置数据库连接：

```python
# MySQL 配置示例
RELATION_DB_CONFIG = {
    "db_type": "mysql",
    "db_host": "localhost",
    "db_port": 3306,
    "db_user": "your_username",
    "db_password": "your_password",
    "db_name": "media_crawler"
}
```

## 📂 项目结构

```
MediaCrawler/
├── config/                 # 配置文件目录
│   ├── base_config.py     # 基础配置
│   ├── db_config.py       # 数据库配置
│   └── weibo_config.py    # 微博平台配置
├── database/              # 数据库相关
│   └── models.py          # 数据模型（仅Weibo）
├── media_platform/        # 平台实现
│   └── weibo/            # 微博爬虫实现
├── store/                # 数据存储
│   └── weibo/           # 微博数据存储实现
├── main.py              # 主入口文件
└── README_WEIBO_ONLY.md # 本文档
```

## ⚠️ 免责声明

> **重要提示**：本项目仅供学习和研究使用，请遵守以下原则：
> 
> 1. 不得用于任何商业用途
> 2. 使用时应遵守目标平台的使用条款和robots.txt规则
> 3. 不得进行大规模爬取或对平台造成运营干扰
> 4. 应合理控制请求频率，避免给目标平台带来不必要的负担
> 5. 不得用于任何非法或不当的用途

详细许可条款请参阅项目根目录下的 LICENSE 文件。

## 📚 参考资料

- [MediaCrawler 原项目](https://github.com/NanmiCoder/MediaCrawler)
- [Playwright 文档](https://playwright.dev/)

---

**最后更新**: 2025-12-16
