"""
数据处理服务 - 负责清洗、分词、关键词提取
"""

import re
import os
import jieba
from typing import List, Dict, Tuple
from datetime import datetime
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from app import db
from app.models import Topic, WeiboPost, Keyword


class DataProcessingService:
    """数据处理服务类"""
    
    def __init__(self):
        # 加载停用词
        self.stopwords = self._load_stopwords()
        
    def _load_stopwords(self) -> set:
        """加载停用词表"""
        try:
            # 获取stopwords.txt的绝对路径
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            stopwords_path = os.path.join(current_dir, 'utils', 'stopwords.txt')
            
            if os.path.exists(stopwords_path):
                with open(stopwords_path, 'r', encoding='utf-8') as f:
                    stopwords = set(line.strip() for line in f if line.strip())
                print(f"[INFO] 成功加载 {len(stopwords)} 个停用词")
                return stopwords
            else:
                print(f"[WARNING] 停用词文件不存在: {stopwords_path}，使用默认停用词")
                return {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都'}
        except Exception as e:
            print(f"[ERROR] 加载停用词失败: {e}，使用默认停用词")
            return {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都'}
    
    # ====== 阶段一：数据读取 ======
    
    def fetch_topic_posts(self, topic_id: int) -> Dict:
        """
        读取指定话题的所有微博数据
        
        Args:
            topic_id: 话题ID
            
        Returns:
            {
                'topic_id': int,
                'topic_name': str,
                'posts': [WeiboPost列表]
            }
        """
        topic = Topic.query.get(topic_id)
        if not topic:
            return None
        
        posts = WeiboPost.query.filter_by(topic_id=topic_id).all()
        return {
            'topic_id': topic.id,
            'topic_name': topic.topic_name,
            'posts': posts
        }
    
    # ====== 阶段二：文本清洗 ======
    
    def clean_text(self, raw_text: str) -> str:
        """
        清洗单条文本
        
        处理步骤:
        1. 去除URL
        2. 去除@用户名
        3. 去除emoji表情
        4. 去除特殊字符
        5. 去除多余空格
        
        Args:
            raw_text: 原始文本
            
        Returns:
            清洗后的文本
        """
        if not raw_text:
            return ""
        
        text = raw_text
        
        # 1. 去除URL链接
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # 2. 去除@用户名
        text = re.sub(r'@[\w\u4e00-\u9fa5]+', '', text)
        
        # 3. 去除话题标签#(可选，根据需求)
        # text = re.sub(r'#[^#]+#', '', text)
        
        # 4. 去除emoji和特殊符号
        # TODO: 更完善的emoji过滤
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', '', text)
        
        # 5. 去除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    # ====== 阶段三：分词处理 ======
    
    def segment_text(self, text: str) -> List[str]:
        """
        对文本进行分词并过滤
        
        Args:
            text: 清洗后的文本
            
        Returns:
            分词列表
        """
        if not text:
            return []
        
        # 1. jieba分词
        words = jieba.cut(text)
        
        # 2. 过滤处理
        filtered_words = []
        for word in words:
            word = word.strip()
            # 过滤条件：
            # - 不在停用词表中
            # - 长度大于1
            # - 不是纯数字
            if (word and 
                word not in self.stopwords and 
                len(word) > 1 and 
                not word.isdigit()):
                filtered_words.append(word)
        
        return filtered_words
    
    # ====== 阶段四：关键词提取 ======
    
    def extract_keywords_tf(self, posts: List[WeiboPost], top_n: int = 50) -> List[Dict]:
        """
        使用词频(TF)方法提取关键词
        
        Args:
            posts: 微博列表
            top_n: 返回前N个关键词
            
        Returns:
            [
                {'keyword': str, 'frequency': int, 'weight': float},
                ...
            ]
        """
        # 1. 收集所有分词
        all_words = []
        for post in posts:
            # 清洗文本
            cleaned = self.clean_text(post.content)
            # 分词
            words = self.segment_text(cleaned)
            all_words.extend(words)
        
        # 2. 统计词频
        word_counter = Counter(all_words)
        
        # 3. 获取Top N
        top_keywords = word_counter.most_common(top_n)
        
        # 4. 格式化结果
        total_words = len(all_words)
        results = []
        for keyword, freq in top_keywords:
            results.append({
                'keyword': keyword,
                'frequency': freq,
                'weight': freq / total_words if total_words > 0 else 0
            })
        
        return results
    
    def extract_keywords_tfidf(self, posts: List[WeiboPost], top_n: int = 50) -> List[Dict]:
        """
        使用TF-IDF方法提取关键词
        
        Args:
            posts: 微博列表
            top_n: 返回前N个关键词
            
        Returns:
            关键词列表
        """
        if not posts:
            return []
        
        # 1. 准备文档列表和统计词频（每条微博是一个文档）
        documents = []
        word_freq_counter = Counter()
        
        for post in posts:
            # 清洗文本
            cleaned = self.clean_text(post.content)
            # 分词
            words = self.segment_text(cleaned)
            # 用空格连接分词结果作为文档
            documents.append(' '.join(words))
            # 同时统计全局词频
            word_freq_counter.update(words)
        
        # 如果文档为空，返回空结果
        if not documents or all(not doc for doc in documents):
            return []
        
        # 2. 使用TfidfVectorizer计算TF-IDF
        try:
            vectorizer = TfidfVectorizer(max_features=top_n * 2)  # 提取更多特征避免丢失
            tfidf_matrix = vectorizer.fit_transform(documents)
            
            # 3. 提取特征词和权重
            feature_names = vectorizer.get_feature_names_out()
            
            # 计算每个词的平均TF-IDF分数（跨所有文档）
            tfidf_scores = tfidf_matrix.sum(axis=0).A1
            
            # 4. 为每个词创建(词, TF-IDF分数, 词频)的元组
            keyword_data = []
            for idx, word in enumerate(feature_names):
                keyword_data.append({
                    'keyword': word,
                    'tfidf_score': float(tfidf_scores[idx]),
                    'frequency': word_freq_counter.get(word, 0)
                })
            
            # 5. 按TF-IDF分数排序并取Top N
            keyword_data.sort(key=lambda x: x['tfidf_score'], reverse=True)
            top_keywords = keyword_data[:top_n]
            
            # 6. 格式化结果（保留频率和权重）
            results = []
            for kw in top_keywords:
                results.append({
                    'keyword': kw['keyword'],
                    'frequency': kw['frequency'],
                    'weight': kw['tfidf_score']
                })
            
            return results
            
        except Exception as e:
            print(f"[ERROR] TF-IDF提取失败: {e}")
            # 降级到TF方法
            print("[INFO] 降级使用TF方法")
            return self.extract_keywords_tf(posts, top_n)
    
    # ====== 阶段五：数据保存 ======
    
    def save_keywords(self, topic_id: int, keywords: List[Dict], time_period: str = None) -> bool:
        """
        保存关键词到数据库
        
        Args:
            topic_id: 话题ID
            keywords: 关键词列表 [{'keyword': str, 'frequency': int}, ...]
            time_period: 时间段标识，如 '2024-12-16'
            
        Returns:
            是否成功
        """
        try:
            # 1. 准备时间段
            if not time_period:
                time_period = datetime.now().strftime('%Y-%m-%d')
            
            # 2. 删除该话题该时间段的旧关键词（避免重复）
            deleted_count = Keyword.query.filter_by(
                topic_id=topic_id, 
                time_period=time_period
            ).delete()
            if deleted_count > 0:
                print(f"[INFO] 删除了 {deleted_count} 个旧关键词记录")
            
            # 3. 准备批量插入数据
            keyword_objs = []
            for kw in keywords:
                keyword_objs.append({
                    'topic_id': topic_id,
                    'keyword': kw['keyword'],
                    'frequency': kw.get('frequency', 0),
                    'time_period': time_period,
                    'analyzed_at': datetime.utcnow()
                })
            
            # 4. 批量插入
            if keyword_objs:
                db.session.bulk_insert_mappings(Keyword, keyword_objs)
                db.session.commit()
                print(f"[INFO] 成功保存 {len(keyword_objs)} 个关键词到数据库")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] 保存关键词失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    # ====== 主处理函数 ======
    
    def process_topic(self, topic_id: int, method: str = 'tf', top_n: int = 50) -> Dict:
        """
        处理单个话题的完整流程
        
        Args:
            topic_id: 话题ID
            method: 关键词提取方法 'tf' 或 'tfidf'
            top_n: 提取前N个关键词
            
        Returns:
            处理结果统计
        """
        start_time = datetime.now()
        
        print(f"\n{'='*60}")
        print(f"开始处理话题 ID: {topic_id}")
        print(f"{'='*60}\n")
        
        # 1. 读取数据
        print("[1/4] 读取数据...")
        topic_data = self.fetch_topic_posts(topic_id)
        if not topic_data:
            return {'status': 'error', 'message': '话题不存在'}
        
        posts = topic_data['posts']
        print(f"      读取到 {len(posts)} 条微博")
        
        # 2. 数据清洗（在分词时处理）
        print("[2/4] 数据清洗和分词...")
        
        # 3. 提取关键词
        print("[3/4] 提取关键词...")
        if method == 'tf':
            keywords = self.extract_keywords_tf(posts, top_n)
        elif method == 'tfidf':
            keywords = self.extract_keywords_tfidf(posts, top_n)
        else:
            return {'status': 'error', 'message': '不支持的提取方法'}
        
        print(f"      提取到 {len(keywords)} 个关键词")
        
        # 4. 保存结果
        print("[4/4] 保存关键词...")
        success = self.save_keywords(topic_id, keywords)
        
        # 5. 统计信息
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        result = {
            'status': 'success' if success else 'error',
            'topic_id': topic_id,
            'topic_name': topic_data['topic_name'],
            'processed_posts': len(posts),
            'keywords_count': len(keywords),
            'top_10_keywords': keywords[:10],
            'processing_time': f"{processing_time:.2f}s"
        }
        
        print(f"\n{'='*60}")
        print(f"处理完成！")
        print(f"耗时: {result['processing_time']}")
        print(f"Top 10 关键词:")
        for i, kw in enumerate(result['top_10_keywords'], 1):
            print(f"  {i}. {kw['keyword']}: {kw['frequency']} 次")
        print(f"{'='*60}\n")
        
        return result
    
    def process_all_topics(self, method: str = 'tf', top_n: int = 50) -> List[Dict]:
        """
        批量处理所有活跃话题
        
        Args:
            method: 关键词提取方法
            top_n: 每个话题提取的关键词数量
            
        Returns:
            所有话题的处理结果列表
        """
        # 1. 查询所有活跃话题
        active_topics = Topic.query.filter_by(is_active=True).all()
        print(f"\n[INFO] 找到 {len(active_topics)} 个活跃话题\n")
        
        # 2. 遍历处理
        results = []
        for i, topic in enumerate(active_topics, 1):
            print(f"\n处理进度: {i}/{len(active_topics)}")
            try:
                result = self.process_topic(topic.id, method, top_n)
                results.append(result)
            except Exception as e:
                print(f"[ERROR] 处理话题 {topic.id} 失败: {e}")
                results.append({
                    'status': 'error',
                    'topic_id': topic.id,
                    'message': str(e)
                })
        
        return results


# 使用示例
if __name__ == '__main__':
    # 创建服务实例
    service = DataProcessingService()
    
    # 测试文本清洗
    test_text = "今天天气真不错！http://example.com @张三 #微博话题# 😊"
    cleaned = service.clean_text(test_text)
    print(f"原文: {test_text}")
    print(f"清洗后: {cleaned}")
    
    # 测试分词
    words = service.segment_text(cleaned)
    print(f"分词结果: {words}")
    
    # TODO: 测试完整流程（需要数据库数据）
    # result = service.process_topic(topic_id=1, method='tf', top_n=50)
    # print(result)
