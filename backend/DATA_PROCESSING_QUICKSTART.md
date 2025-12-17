# 数据处理模块 - 快速开始

## 📝 已创建的文件

我已经为你准备好了数据处理模块的完整框架：

### 1. 设计文档
- **`DATA_PROCESSING_PLAN.md`** - 详细的数据处理流程设计方案
  - 包含完整的5阶段处理流程
  - 代码结构规划
  - 技术选型建议
  - 实现优先级

### 2. 核心代码
- **`app/services/data_processing_service.py`** - 数据处理服务类
  - ✅ `clean_text()` - 文本清洗（去URL、@用户名、emoji等）
  - ✅ `segment_text()` - 中文分词（jieba + 停用词过滤）
  - ✅ `extract_keywords_tf()` - 词频统计提取关键词
  - 🔧 `extract_keywords_tfidf()` - TF-IDF提取（待实现）
  - 🔧 `fetch_topic_posts()` - 数据库查询（待实现）
  - 🔧 `save_keywords()` - 保存到数据库（待实现）
  - ✅ `process_topic()` - 完整处理流程

### 3. 配置文件
- **`app/utils/stopwords.txt`** - 中文停用词表

### 4. 测试脚本
- **`test_data_processing.py`** - 测试脚本（3种模式）

---

## 🚀 快速测试

### 模式1: 测试基础功能（文本清洗和分词）

```bash
cd backend
.\venv\Scripts\python.exe test_data_processing.py --mode basic
```

**预期输出：**
- 展示文本清洗效果（去除URL、@、emoji）
- 展示分词结果（过滤停用词）

### 模式2: 创建测试数据

```bash
.\venv\Scripts\python.exe test_data_processing.py --mode create_sample
```

**功能：**
- 在数据库中创建测试话题 "#数据处理测试#"
- 插入10条示例微博数据

### 模式3: 测试数据库处理

```bash
.\venv\Scripts\python.exe test_data_processing.py --mode database
```

**功能：**
- 查看数据库中的话题和微博统计
- 显示第一个话题的前5条微博

---

## 📋 待完成的TODO

### 优先级1: 核心功能

在 `app/services/data_processing_service.py` 中完成以下函数：

1. **`fetch_topic_posts()`** - 数据库查询
   ```python
   def fetch_topic_posts(self, topic_id: int):
       topic = Topic.query.get(topic_id)
       if not topic:
           return None
       posts = WeiboPost.query.filter_by(topic_id=topic_id).all()
       return {
           'topic_id': topic.id,
           'topic_name': topic.topic_name,
           'posts': posts
       }
   ```

2. **`save_keywords()`** - 保存关键词
   ```python
   def save_keywords(self, topic_id: int, keywords: List[Dict], time_period: str = None):
       try:
           if not time_period:
               time_period = datetime.now().strftime('%Y-%m-%d')
           
           # 删除旧数据（可选）
           Keyword.query.filter_by(topic_id=topic_id, time_period=time_period).delete()
           
           # 批量插入
           keyword_objs = []
           for kw in keywords:
               keyword_objs.append({
                   'topic_id': topic_id,
                   'keyword': kw['keyword'],
                   'frequency': kw['frequency'],
                   'time_period': time_period,
                   'analyzed_at': datetime.utcnow()
               })
           
           db.session.bulk_insert_mappings(Keyword, keyword_objs)
           db.session.commit()
           return True
       except Exception as e:
           db.session.rollback()
           print(f"Error: {e}")
           return False
   ```

### 优先级2: 增强功能

3. **`extract_keywords_tfidf()`** - TF-IDF
   ```python
   from sklearn.feature_extraction.text import TfidfVectorizer
   
   def extract_keywords_tfidf(self, posts, top_n=50):
       # 准备文档
       documents = []
       for post in posts:
           cleaned = self.clean_text(post.content)
           words = self.segment_text(cleaned)
           documents.append(' '.join(words))
       
       # TF-IDF
       vectorizer = TfidfVectorizer(max_features=top_n)
       tfidf_matrix = vectorizer.fit_transform(documents)
       feature_names = vectorizer.get_feature_names_out()
       
       # 计算总分数
       scores = tfidf_matrix.sum(axis=0).A1
       keyword_scores = list(zip(feature_names, scores))
       keyword_scores.sort(key=lambda x: x[1], reverse=True)
       
       # 格式化结果
       results = []
       for keyword, score in keyword_scores[:top_n]:
           results.append({
               'keyword': keyword,
               'frequency': 0,  # 可以单独统计
               'weight': float(score)
           })
       return results
   ```

---

## 🧪 完整测试流程

### 步骤1: 测试基础功能
```bash
.\venv\Scripts\python.exe test_data_processing.py --mode basic
```

### 步骤2: 创建测试数据
```bash
.\venv\Scripts\python.exe test_data_processing.py --mode create_sample
```

### 步骤3: 完善代码
- 在 `data_processing_service.py` 中实现上述TODO
- 需要取消注释相关数据库操作代码

### 步骤4: 运行完整处理
```python
# 在Python环境中测试
from app import create_app
from app.services.data_processing_service import DataProcessingService

app = create_app()
with app.app_context():
    service = DataProcessingService()
    result = service.process_topic(topic_id=1, method='tf', top_n=50)
    print(result)
```

### 步骤5: 查看结果
```python
from app.models import Keyword

with app.app_context():
    # 查询某话题的关键词
    keywords = Keyword.query.filter_by(topic_id=1).order_by(Keyword.frequency.desc()).limit(20).all()
    for kw in keywords:
        print(f"{kw.keyword}: {kw.frequency}")
```

---

## 📦 依赖检查

确保以下Python包已安装：

```bash
pip install jieba
pip install scikit-learn  # 用于TF-IDF
```

---

## 🎯 下一步建议

### 立即可做：
1. ✅ 运行基础功能测试（不需要数据库）
2. ✅ 查看文本清洗和分词效果

### 需要数据后：
3. 🔧 实现 `fetch_topic_posts()` 和 `save_keywords()`
4. 🔧 运行完整流程测试
5. 🔧 验证关键词保存到数据库

### 高级优化：
6. ⭐ 实现TF-IDF算法
7. ⭐ 添加时间维度分析
8. ⭐ 创建API接口（可选）

---

## 📖 参考文档

- **设计方案**: `DATA_PROCESSING_PLAN.md` - 完整思路和架构
- **代码框架**: `app/services/data_processing_service.py` - 可直接使用的类
- **测试脚本**: `test_data_processing.py` - 3种测试模式

---

## 💡 提示

1. **渐进式开发**: 先跑通基础功能 → 再连接数据库 → 最后优化算法
2. **小步测试**: 每完成一个函数就立即测试
3. **查看日志**: 代码中有丰富的print输出，方便调试
4. **扩展停用词**: `stopwords.txt` 可以继续添加更多词汇

---

**开始测试吧！** 🚀

```bash
cd backend
.\venv\Scripts\python.exe test_data_processing.py --mode basic
```
