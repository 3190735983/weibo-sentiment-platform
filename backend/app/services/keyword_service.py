import jieba
import jieba.analyse
from collections import Counter


class KeywordAnalysisService:
    """关键词分析服务"""
    
    def __init__(self):
        # 加载停用词
        self.stopwords = self.load_stopwords()
    
    def load_stopwords(self):
        """加载停用词表"""
        # TODO: 加载停用词文件
        # 可以使用常用的中文停用词表
        stopwords = set(['的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'])
        return stopwords
    
    def extract(self, topic_id, top_n=50):
        """提取关键词
        
        Args:
            topic_id: 话题ID
            top_n: 提取前N个关键词
        
        Returns:
            list: 关键词列表
        """
        # TODO: 实现关键词提取逻辑
        # 1. 获取话题下的所有评论
        # 2. 分词
        # 3. 去除停用词
        # 4. 统计词频
        # 5. 保存到数据库
        pass
    
    def extract_tfidf(self, texts, top_n=20):
        """使用TF-IDF提取关键词
        
        Args:
            texts: 文本列表
            top_n: 提取前N个关键词
        
        Returns:
            list: 关键词列表
        """
        # TODO: 实现TF-IDF提取
        pass
    
    def word_frequency(self, texts):
        """统计词频
        
        Args:
            texts: 文本列表
        
        Returns:
            Counter: 词频统计结果
        """
        words = []
        for text in texts:
            # 分词
            seg_list = jieba.cut(text)
            # 过滤停用词和短词
            filtered_words = [w for w in seg_list if w not in self.stopwords and len(w) > 1]
            words.extend(filtered_words)
        
        return Counter(words)
