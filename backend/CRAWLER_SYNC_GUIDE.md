# 爬虫数据同步 - 完整流程说明

## 📋 当前状态总结

### ✅ 已完成
1. **数据处理服务** - 完全实现（清洗、分词、TF-IDF、保存）
2. **同步脚本** - 根据MediaCrawler实际表结构编写
3. **数据库连接** - 路径已修正为 `../MediaCrawler/database/sqlite_tables.db`

### ⚠️ 当前问题
**爬虫遇到反爬限制**：
- 错误：`'msg': '这里还没有内容'`
- 原因：微博对敏感关键词（如政治相关）进行了限制
- 解决：已更新关键词为娱乐话题（"有翡"等）

---

## 🚀 完整数据处理流程

### 步骤1: 运行爬虫

```bash
cd MediaCrawler
python main.py --platform wb --lt qrcode --type search
```

**说明**：
- MediaCrawler会自动保存数据到 `database/sqlite_tables.db`
- 数据同时保存为JSON到 `data/weibo/json/` (备份)
- 配置文件：`config/base_config.py` 中的 `KEYWORDS`

**当前配置**：
```python
KEYWORDS = "习近平听取岑浩辉述职报告,芸汐传 16亿,深圳16岁少年卖烤鸡日入过万,海南自贸港全岛封关后有啥变化,有翡"
SAVE_DATA_OPTION = "sqlite"  # 保存到SQLite
ENABLE_GET_COMMENTS = True    # 爬取评论
CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES = 10  # 每条微博10条评论
```

---

### 步骤2: 检查爬虫数据

```bash
cd backend
.\venv\Scripts\python.exe inspect_db.py
```

**预期输出**：
```
表名: weibo_note
  字段: user_id, nickname, content, create_time, liked_count...
  记录数: X

表名: weibo_note_comment
  字段: comment_id, note_id, content, nickname, create_time...
  记录数: Y
```

---

### 步骤3: 同步数据到主数据库

```bash
.\venv\Scripts\python.exe sync_crawler_data.py
```

**同步逻辑**：
- 从 `MediaCrawler/database/sqlite_tables.db` 读取
- 表映射：
  - `weibo_note` → `WeiboPost`
  - `weibo_note_comment` → `WeiboPost`
- 自动关联话题（从内容提取或使用默认话题）
- 去重：通过 `weibo_id` 避免重复

**预期输出**：
```
找到 50 条微博内容记录
找到 200 条评论记录

同步完成！
  ✅ 新增: 250 条
  ℹ️  跳过: 0 条（已存在）

主数据库统计:
  总微博数: 250
  总话题数: 5
```

---

### 步骤4: 处理数据（提取关键词）

```bash
# 处理单个话题（测试）
.\venv\Scripts\python.exe test_full_processing.py --mode single

# 批量处理所有话题
.\venv\Scripts\python.exe test_full_processing.py --mode all
```

**处理流程**：
1. 从数据库读取微博内容
2. 文本清洗（去URL、emoji、特殊字符）
3. jieba分词 + 停用词过滤
4. TF-IDF提取Top 50关键词
5. 保存到 `keywords` 表

---

## 🔧 故障排查

### 问题1: 爬虫提示"这里还没有内容"

**原因**: 微博反爬或敏感词限制

**解决方案**:
1. 更换关键词（避免政治、敏感话题）
2. 使用娱乐、生活类关键词（"有翡"、"美食"、"旅游"等）
3. 降低爬取频率：修改 `CRAWLER_MAX_SLEEP_SEC = 5`

### 问题2: 数据库是空的

**检查清单**:
```bash
# 1. 确认数据库文件存在
dir ..\MediaCrawler\database\sqlite_tables.db

# 2. 检查表结构和记录数
.\venv\Scripts\python.exe inspect_db.py

# 3. 检查JSON文件（备份数据）
dir ..\MediaCrawler\data\weibo\json\
```

**可能原因**:
- 爬虫还在运行，数据未提交
- 爬虫遇到错误提前退出
- 配置错误（检查 `SAVE_DATA_OPTION`）

### 问题3: 同步后主数据库仍然没数据

**检查**:
```bash
# 查看主数据库统计
.\venv\Scripts\python.exe test_full_processing.py --mode stats
```

**可能原因**:
- 话题表为空（先运行 `add_topics_simple.py` 添加话题）
- 同步脚本映射错误
- 事务未提交

---

## 📊 数据库表结构对应

### MediaCrawler表 → 主数据库表

| MediaCrawler | 字段 | 主数据库 | 字段 |
|---|---|---|---|
| weibo_note | note_id | WeiboPost | weibo_id |
| | content | | content |
| | nickname | | user_nickname |
| | create_time | | publish_time |
| | liked_count | | likes_count |
| weibo_note_comment | comment_id | WeiboPost | weibo_id |
| | content | | comment_text |
| | nickname | | user_nickname |

---

## 🎯 快速测试流程（推荐）

### 方案A: 使用娱乐话题快速测试

1. **修改关键词**（已完成）:
   ```python
   # config/base_config.py
   KEYWORDS = "有翡,长月烬明,微博热搜,美食推荐"
   ```

2. **运行爬虫** (5-10分钟):
   ```bash
   cd MediaCrawler
   python main.py
   ```

3. **同步 + 处理**:
   ```bash
   cd backend
   .\venv\Scripts\python.exe sync_crawler_data.py
   .\venv\Scripts\python.exe test_full_processing.py --mode single
   ```

### 方案B: 使用测试数据（快速验证）

如果爬虫仍有问题，可以先用测试数据验证流程：

```bash
cd backend
.\venv\Scripts\python.exe test_data_processing.py --mode create_sample
.\venv\Scripts\python.exe test_full_processing.py --mode single
```

---

## 💡 建议的关键词

### ✅ 推荐（不易被限制）
- 娱乐：有翡、长月烬明、芸汐传
- 生活：美食推荐、旅游攻略、健身
- 科技：人工智能、编程、数码
- 其他：微博热搜、新闻、摄影

### ❌ 避免（容易被限制）
- 政治相关
- 敏感人物
- 负面新闻
- 争议话题

---

## 📝 后续开发

数据处理完成后：
1. ✅ 关键词已保存到数据库 → 可以展示词云
2. ✅ 数据已清洗 → 可以进行情感分析
3. ✅ TF-IDF提取 → 可以做主题分析
4. 🔄 前端展示 → 连接API显示数据

---

## 🆘 需要帮助？

运行诊断脚本查看完整状态：
```bash
.\venv\Scripts\python.exe workflow_sync.py
```

或直接查看：
1. MediaCrawler数据库：`inspect_db.py`
2. 主数据库统计：`test_full_processing.py --mode stats`
3. 完整处理测试：`test_full_processing.py --mode single`

---

**当前建议**：现在关键词已更新为娱乐话题，再次运行爬虫应该可以成功爬取数据！

```bash
cd MediaCrawler
python main.py --platform wb --lt qrcode --type search
```
