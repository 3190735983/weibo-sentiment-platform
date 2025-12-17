# 数据处理模块 - 完整实现说明

## ✅ 已完成的功能

### 1. 核心服务实现 ✅
文件: `app/services/data_processing_service.py`

已实现的功能:
- ✅ **停用词加载**: 从 `app/utils/stopwords.txt` 加载停用词（2313个）
- ✅ **文本清洗**: 去除URL、@用户名、emoji、特殊字符
- ✅ **中文分词**: 使用jieba分词 + 停用词过滤
- ✅ **TF词频统计**: 基于词频的关键词提取
- ✅ **TF-IDF提取**: 基于TF-IDF算法的关键词提取
- ✅ **数据库查询**: 从数据库读取话题和微博
- ✅ **数据库保存**: 批量保存关键词到数据库
- ✅ **批量处理**: 处理所有活跃话题

---

## 📦 已安装的依赖

```bash
✅ jieba           # 中文分词
✅ scikit-learn    # TF-IDF算法
```

---

## 🚀 使用方法

### 方法1: 使用测试脚本

#### 查看统计信息
```bash
cd backend
.\venv\Scripts\python.exe test_full_processing.py --mode stats
```

#### 处理单个话题
```bash
.\venv\Scripts\python.exe test_full_processing.py --mode single
```
- 自动选择第一个话题
- 分别测试TF和TF-IDF方法
- 显示Top 20关键词
- 验证数据库保存

#### 批量处理所有话题
```bash
.\venv\Scripts\python.exe test_full_processing.py --mode all
```
- 处理所有活跃话题（is_active=True）
- 使用TF-IDF方法
- 每个话题提取30个关键词
- 显示处理进度和结果

#### 清空关键词（重新处理）
```bash
.\venv\Scripts\python.exe test_full_processing.py --mode clear
```

---

### 方法2: Python代码调用

```python
from app import create_app
from app.services.data_processing_service import DataProcessingService

app = create_app()

with app.app_context():
    # 创建服务实例
    service = DataProcessingService()
    
    # 处理单个话题
    result = service.process_topic(
        topic_id=1,
        method='tfidf',  # 'tf' 或 'tfidf'
        top_n=50         # 提取前50个关键词
    )
    
    print(result)
    
    # 批量处理所有话题
    results = service.process_all_topics(method='tfidf', top_n=50)
```

---

### 方法3: 独立使用各个功能

```python
from app.services.data_processing_service import DataProcessingService

service = DataProcessingService()

# 1. 文本清洗
text = "今天天气真好！http://example.com @张三 #话题# 😊"
cleaned = service.clean_text(text)
print(cleaned)  # 输出: "今天天气真好 话题"

# 2. 分词
words = service.segment_text(cleaned)
print(words)  # 输出: ['今天', '天气', '真好', '话题']

# 3. 提取关键词（需要在app_context中）
with app.app_context():
    from app.models import WeiboPost
    
    posts = WeiboPost.query.filter_by(topic_id=1).all()
    
    # TF方法
    keywords_tf = service.extract_keywords_tf(posts, top_n=20)
    
    # TF-IDF方法
    keywords_tfidf = service.extract_keywords_tfidf(posts, top_n=20)
    
    # 保存到数据库
    service.save_keywords(topic_id=1, keywords=keywords_tfidf)
```

---

## 📊 数据流程

```
1. 爬虫采集数据
   ↓
   WeiboPost (content字段)
   
2. 数据处理服务
   ↓
   clean_text() → "今天天气真好 话题"
   ↓
   segment_text() → ['今天', '天气', '真好', '话题']
   ↓
   extract_keywords_tfidf() → [
       {'keyword': '天气', 'frequency': 10, 'weight': 0.85},
       {'keyword': '话题', 'frequency': 8, 'weight': 0.72},
       ...
   ]
   ↓
   save_keywords()
   ↓
3. 数据库保存
   ↓
   Keyword表 (keyword, frequency, time_period)
```

---

## 🗄️ 数据库表结构

### Keyword表
```sql
CREATE TABLE keywords (
    id INTEGER PRIMARY KEY,
    topic_id INTEGER NOT NULL,
    keyword VARCHAR(100) NOT NULL,
    frequency INTEGER DEFAULT 0,
    time_period VARCHAR(50),         -- 例如: "2024-12-17"
    analyzed_at DATETIME,
    FOREIGN KEY (topic_id) REFERENCES topics(id)
);
```

### 查询示例
```python
# 查询某话题的所有关键词
keywords = Keyword.query.filter_by(topic_id=1).order_by(
    Keyword.frequency.desc()
).all()

# 查询某时间段的关键词
keywords = Keyword.query.filter_by(
    topic_id=1,
    time_period='2024-12-17'
).all()
```

---

## ⚙️ 配置和优化

### 停用词自定义
编辑 `app/utils/stopwords.txt` 添加或删除停用词

### 调整参数
在调用时可以自定义参数：

```python
result = service.process_topic(
    topic_id=1,
    method='tfidf',      # 算法选择
    top_n=100            # 提取更多关键词
)
```

### 性能优化建议
1. **大量数据时**: 使用批量处理 `process_all_topics()`
2. **定期更新**: 通过 `time_period` 参数区分不同时间段
3. **清理旧数据**: `save_keywords()` 会自动删除同时间段的旧记录

---

## 🧪 测试状态

### 基础功能测试 ✅
```bash
.\venv\Scripts\python.exe test_data_processing.py --mode basic
```
- ✅ 文本清洗正常
- ✅ 分词功能正常
- ✅ 停用词过滤正常

### 完整流程测试 (需要数据)
```bash
# 1. 确保有爬虫数据
.\venv\Scripts\python.exe test_full_processing.py --mode stats

# 2. 处理单个话题测试
.\venv\Scripts\python.exe test_full_processing.py --mode single

# 3. 批量处理测试
.\venv\Scripts\python.exe test_full_processing.py --mode all
```

---

## 📋 待测试检查清单

当你的爬虫采集到数据后：

1. [ ] 运行 `--mode stats` 确认有数据
2. [ ] 运行 `--mode single` 测试单个话题处理
3. [ ] 检查数据库 Keyword 表是否有数据
4. [ ] 验证关键词是否合理
5. [ ] 运行 `--mode all` 批量处理所有话题
6. [ ] 在前端查看关键词展示

---

## 🔧 故障排查

### 问题1: ModuleNotFoundError: sklearn
**解决**: 
```bash
.\venv\Scripts\pip.exe install scikit-learn
```

### 问题2: 停用词未加载
**检查**: 
- 文件路径: `backend/app/utils/stopwords.txt`
- 文件编码: UTF-8
- 查看日志: 是否显示 "[INFO] 成功加载 2313 个停用词"

### 问题3: 没有提取到关键词
**原因**: 
- 数据库中没有微博数据
- 微博内容为空或太短
- 所有词都被停用词过滤

**解决**: 
- 运行爬虫采集数据
- 调整停用词列表
- 降低词长度限制（修改 `segment_text()` 中的 `len(word) > 1`）

---

## 📈 预期输出示例

### TF方法输出
```
============================================================
开始处理话题 ID: 1
============================================================

[1/4] 读取数据...
      读取到 150 条微博
[2/4] 数据清洗和分词...
[3/4] 提取关键词...
      提取到 20 个关键词
[4/4] 保存关键词...
[INFO] 删除了 0 个旧关键词记录
[INFO] 成功保存 20 个关键词到数据库

============================================================
处理完成！
耗时: 2.35s
Top 10 关键词:
  1. 春节: 45 次
  2. 回家: 38 次
  3. 团圆: 32 次
  4. 家人: 28 次
  5. 过年: 25 次
  ...
============================================================
```

---

## 🎯 下一步

数据处理模块已完全实现！你可以：

1. **等爬虫采集数据后**: 立即运行 `test_full_processing.py --mode single`
2. **集成到API**: 将处理功能暴露为API接口
3. **定时任务**: 设置定时任务自动处理新数据
4. **前端展示**: 从Keyword表读取数据展示词云

---

**状态**: ✅ 开发完成，等待数据测试
