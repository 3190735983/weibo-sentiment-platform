# 微博数据处理流程设计方案

## 📋 目标
将爬取的原始微博数据进行清洗、分词、关键词提取，并将结果保存到数据库

## 🗂️ 数据库结构分析

### 现有表结构
1. **Topic (话题表)**
   - `id`, `topic_name`, `topic_tag`, `is_active`
   - 关系：一对多 WeiboPost, 一对多 Keyword

2. **WeiboPost (微博数据表)**
   - `id`, `topic_id`, `weibo_id`, `content`, `comment_text`
   - `user_nickname`, `publish_time`, `likes_count`, `location`
   - 关系：一对一 SentimentResult

3. **Keyword (关键词表)**
   - `id`, `topic_id`, `keyword`, `frequency`, `time_period`

4. **SentimentResult (情感分析结果表)**
   - 用于存储情感分析结果

---

## 🔄 数据处理流程设计

### 阶段一：数据读取与预处理

#### 1.1 从数据库读取原始数据
```python
# 伪代码框架
def fetch_raw_data(topic_id=None):
    """
    从数据库读取待处理的微博数据
    参数:
        topic_id: 指定话题ID，None则处理所有话题
    返回:
        话题列表，每个话题包含其所有微博数据
    """
    # 1. 查询活跃话题（is_active=True）
    # 2. 对每个话题，获取所有关联的WeiboPost
    # 3. 返回结构化数据
    pass
```

**数据结构示例：**
```python
{
    "topic_id": 1,
    "topic_name": "春节回家",
    "posts": [
        {
            "weibo_id": "xxx",
            "content": "完整微博内容",
            "comment_text": "评论文本",
            "publish_time": "2024-12-16 10:00:00"
        },
        ...
    ]
}
```

#### 1.2 数据清洗
```python
def clean_text(raw_text):
    """
    清洗单条文本
    处理步骤:
        1. 去除URL链接 (http/https)
        2. 去除@用户名
        3. 去除#话题标签#（可选保留）
        4. 去除表情符号（emoji）
        5. 去除特殊字符（保留中文、英文、数字）
        6. 去除多余空格和换行
        7. 统一转小写（英文）
    返回:
        清洗后的纯文本
    """
    # 使用正则表达式处理
    pass
```

#### 1.3 数据去重
```python
def deduplicate_posts(posts):
    """
    去除重复微博
    策略:
        1. 基于weibo_id去重（已有unique约束）
        2. 基于内容相似度去重（可选）
        3. 保留最早发布的版本
    """
    pass
```

---

### 阶段二：文本分词与关键词提取

#### 2.1 中文分词
```python
def segment_text(cleaned_text):
    """
    对清洗后的文本进行分词
    工具: jieba
    步骤:
        1. 使用jieba.cut()进行分词
        2. 过滤停用词（的、了、是、在等）
        3. 过滤单字（可选）
        4. 过滤纯数字
        5. 保留名词、动词、形容词（可选使用词性标注）
    返回:
        分词列表 ['关键词1', '关键词2', ...]
    """
    pass
```

**停用词表建议：**
- 使用：`backend/app/utils/stopwords.txt`
- 可以从网上下载中文停用词表（哈工大、百度停用词等）

#### 2.2 关键词提取
```python
def extract_keywords_per_topic(topic_id, posts_data):
    """
    对某个话题的所有微博提取关键词
    
    方法1: 词频统计（TF）
        - 统计所有分词的出现次数
        - 按频率排序
        - 取Top N（如Top 50）
    
    方法2: TF-IDF（推荐）
        - 计算词频-逆文档频率
        - 提取每个话题的特征词
        - 更能反映话题特点
    
    方法3: TextRank（可选）
        - 基于图的关键词抽取算法
        - 适合长文本
    
    返回:
        [
            {'keyword': '春节', 'frequency': 150, 'weight': 0.85},
            {'keyword': '回家', 'frequency': 120, 'weight': 0.72},
            ...
        ]
    """
    pass
```

#### 2.3 时间维度分析（可选）
```python
def extract_keywords_by_time(topic_id, time_granularity='day'):
    """
    按时间粒度提取关键词
    参数:
        time_granularity: 'hour', 'day', 'week'
    目的:
        - 追踪关键词演化趋势
        - 发现热点词的生命周期
    """
    pass
```

---

### 阶段三：数据保存

#### 3.1 更新WeiboPost表
```python
def save_cleaned_data(weibo_id, cleaned_content):
    """
    选项1: 新增字段
        - 在WeiboPost表添加 cleaned_content 字段
        - 保存清洗后的文本
    
    选项2: 仅用于分析，不保存
        - 清洗后的文本只用于关键词提取
        - 不额外存储
    """
    pass
```

#### 3.2 保存关键词到Keyword表
```python
def save_keywords(topic_id, keywords_list, time_period=None):
    """
    保存提取的关键词
    
    策略:
        1. 先删除该话题的旧关键词记录（可选）
        2. 批量插入新关键词
        3. 记录analyzed_at时间戳
    
    数据示例:
        topic_id: 1
        keyword: '春节'
        frequency: 150
        time_period: '2024-12-16' 或 '2024-W50'
        analyzed_at: '2024-12-16 15:30:00'
    """
    # 使用 db.session.bulk_insert_mappings() 提高性能
    pass
```

#### 3.3 生成统计报告（可选）
```python
def generate_processing_report(topic_id):
    """
    生成数据处理报告
    包含:
        - 原始数据数量
        - 清洗后数据数量
        - 去重数量
        - 关键词总数
        - Top 10 关键词
        - 处理耗时
    
    保存为JSON或写入日志
    """
    pass
```

---

## 📊 完整流程示意

```
┌─────────────────────────────────────────────────────────────┐
│                    数据处理主流程                              │
└─────────────────────────────────────────────────────────────┘

1. 【读取数据】
   ↓
   从数据库读取 Topic 和 WeiboPost
   ↓
2. 【数据清洗】
   ↓
   遍历每条微博 → 清洗文本 → 去重
   ↓
3. 【分词处理】
   ↓
   对每条微博 → jieba分词 → 过滤停用词
   ↓
4. 【关键词提取】
   ↓
   按话题聚合 → TF-IDF提取 → 排序取Top N
   ↓
5. 【保存结果】
   ↓
   批量插入Keyword表 → 记录时间戳 → 完成
   ↓
6. 【生成报告】（可选）
   ↓
   输出统计信息 → 日志记录
```

---

## 🛠️ 代码文件规划

### 建议的文件结构

```
backend/
├── app/
│   ├── services/
│   │   ├── data_processing_service.py    # 主处理服务
│   │   ├── text_cleaner.py               # 文本清洗工具
│   │   ├── keyword_extractor.py          # 关键词提取
│   │   └── stopwords_filter.py           # 停用词过滤
│   ├── utils/
│   │   └── stopwords.txt                 # 停用词表
│   └── api/
│       └── processing.py                 # 处理相关API
│
├── scripts/
│   ├── process_all_topics.py             # 批量处理脚本
│   └── process_single_topic.py           # 单话题处理脚本
│
└── tests/
    └── test_data_processing.py           # 单元测试
```

---

## 🎯 核心函数接口设计

### 主处理函数
```python
def process_topic_data(topic_id, 
                       clean=True, 
                       extract_keywords=True,
                       time_based=False,
                       top_n=50):
    """
    处理指定话题的数据
    
    参数:
        topic_id: 话题ID
        clean: 是否清洗文本
        extract_keywords: 是否提取关键词
        time_based: 是否进行时间维度分析
        top_n: 保留前N个关键词
    
    返回:
        {
            'status': 'success',
            'topic_id': 1,
            'processed_posts': 1500,
            'keywords_count': 50,
            'processing_time': '2.5s'
        }
    """
    pass
```

### 批量处理函数
```python
def process_all_active_topics(parallel=False):
    """
    处理所有活跃话题
    
    参数:
        parallel: 是否并行处理（多线程/多进程）
    """
    pass
```

---

## ⚙️ 配置参数建议

```python
# backend/app/config.py 或单独配置文件

DATA_PROCESSING_CONFIG = {
    # 文本清洗
    'remove_urls': True,
    'remove_mentions': True,
    'remove_hashtags': False,  # 话题标签可能有用
    'remove_emojis': True,
    
    # 分词
    'use_stopwords': True,
    'stopwords_file': 'app/utils/stopwords.txt',
    'min_word_length': 2,  # 最小词长
    
    # 关键词提取
    'keyword_method': 'tfidf',  # 'tf', 'tfidf', 'textrank'
    'top_n_keywords': 50,
    'min_frequency': 3,  # 最小词频
    
    # 时间分析
    'time_granularity': 'day',  # 'hour', 'day', 'week'
    
    # 性能
    'batch_size': 100,  # 批量处理大小
    'enable_cache': True,
}
```

---

## 📌 实现优先级

### Phase 1: 基础功能（必须）
1. ✅ 数据读取
2. ✅ 基础文本清洗
3. ✅ jieba分词 + 停用词过滤
4. ✅ 词频统计（TF）
5. ✅ 保存关键词到数据库

### Phase 2: 增强功能（建议）
6. ⭐ TF-IDF关键词提取
7. ⭐ 时间维度分析
8. ⭐ 处理报告生成

### Phase 3: 高级功能（可选）
9. 🔮 TextRank算法
10. 🔮 并行处理优化
11. 🔮 实时处理（配合定时任务）

---

## 🧪 测试建议

### 单元测试
```python
def test_text_cleaning():
    """测试文本清洗功能"""
    raw = "今天天气真好！http://example.com @张三 #微博话题# 😊"
    cleaned = clean_text(raw)
    assert "http" not in cleaned
    assert "@" not in cleaned
```

### 集成测试
```python
def test_full_processing():
    """测试完整处理流程"""
    # 1. 准备测试数据
    # 2. 执行处理
    # 3. 验证数据库记录
    # 4. 验证关键词正确性
```

---

## 📝 使用示例

### 命令行用法
```bash
# 处理单个话题
python scripts/process_single_topic.py --topic_id 1

# 处理所有话题
python scripts/process_all_topics.py

# 指定参数
python scripts/process_all_topics.py --top_n 100 --method tfidf
```

### API调用
```bash
# POST /api/processing/process_topic
curl -X POST http://localhost:5000/api/processing/process_topic \
  -H "Content-Type: application/json" \
  -d '{"topic_id": 1, "top_n": 50}'

# GET /api/processing/status
curl http://localhost:5000/api/processing/status?topic_id=1
```

---

## 🎓 技术依赖

### Python库
- `jieba`: 中文分词
- `sklearn.feature_extraction.text.TfidfVectorizer`: TF-IDF计算
- `re`: 正则表达式（文本清洗）
- `sqlalchemy`: 数据库操作

### 数据资源
- 中文停用词表（网上下载或自定义）
- jieba用户词典（可选，添加领域词汇）

---

## 💡 注意事项

1. **性能优化**
   - 批量处理避免逐条数据库操作
   - 使用 `bulk_insert_mappings` 批量插入
   - 大数据量时考虑分批处理

2. **数据一致性**
   - 处理前备份数据库
   - 使用事务确保原子性
   - 记录处理日志

3. **可扩展性**
   - 设计模块化，方便更换算法
   - 配置参数化，避免硬编码
   - 预留接口支持未来功能

4. **异常处理**
   - 处理空文本
   - 处理特殊字符
   - 数据库连接异常

---

## 📅 开发计划

- **Day 1**: 实现文本清洗 + 分词模块
- **Day 2**: 实现词频统计 + 数据保存
- **Day 3**: 实现TF-IDF提取
- **Day 4**: 测试 + 优化
- **Day 5**: API接口 + 文档

---

> **总结**: 这是一个完整的数据处理流程设计，核心是"读取→清洗→分词→提取→保存"五步法。建议先实现基础功能，确保流程跑通，再逐步添加高级特性。
