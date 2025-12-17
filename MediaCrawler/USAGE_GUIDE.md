# MediaCrawler 使用指南

## 1. 安装uv包管理器

uv是一个快速的Python包管理器，MediaCrawler使用它来管理依赖。

### 安装方法：
```bash
pip install uv
```

## 2. 安装MediaCrawler依赖

```bash
cd MediaCrawler
uv sync
```

或者使用requirements安装：
```bash
uv pip install -r requirements.txt
```

## 3. 运行MediaCrawler

### 查看帮助：
```bash
uv run main.py --help
```

### 爬取微博（关键词搜索）：
```bash
uv run main.py --platform wb --lt qrcode --type search
```

### 配置说明：
- `--platform wb`: 指定平台为微博
- `--lt qrcode`: 登录方式（二维码）
- `--type search`: 爬取类型（关键词搜索）

## 4. 配置关键词

编辑 `config/base_config.py`:
```python
KEYWORDS = "人工智能,ChatGPT,春节"  # 你要爬取的关键词，逗号分隔
```

## 5. 首次使用

第一次运行需要：
1. 扫描二维码登录微博
2. Cookie会自动保存
3. 后续运行会复用Cookie

## 6. 数据存储

爬取的数据会保存在：
- SQLite数据库: `data/weibo.db`
- JSON文件: `data/weibo/` 目录

## 7. 常见问题

### Q1: uv命令不可用
**解决**: `pip install uv`

### Q2: 依赖安装失败
**解决**: 
```bash
uv pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

### Q3: 登录失败
**解决**: 
1. 关闭无头模式 (HEADLESS = False)
2. 手动过验证码
3. 确保网络稳定

## 8. 与主系统集成

爬取的数据在 `data/weibo.db`，可以：
1. 读取SQLite数据库
2. 同步到主系统数据库
3. 进行情感分析
