import re


def clean_text(text):
    """清洗文本数据
    
    Args:
        text: 原始文本
    
    Returns:
        str: 清洗后的文本
    """
    if not text:
        return ""
    
    # 去除URL
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # 去除@用户名
    text = re.sub(r'@[\w\-]+', '', text)
    
    # 去除多余空格
    text = re.sub(r'\s+', ' ', text)
    
    # 去除首尾空格
    text = text.strip()
    
    return text


def extract_topic_and_comment(text):
    """从文本中分离话题和评论内容
    
    Args:
        text: 包含话题标签的文本
    
    Returns:
        tuple: (话题文本, 评论文本)
    """
    # 匹配话题标签 #话题#
    topic_pattern = r'#([^#]+)#'
    topics = re.findall(topic_pattern, text)
    
    # 提取话题文本
    topic_text = ' '.join(['#{}#'.format(t) for t in topics]) if topics else ''
    
    # 去除话题标签，得到纯评论
    comment_text = re.sub(topic_pattern, '', text).strip()
    
    return topic_text, comment_text


def is_valid_comment(text, min_length=5):
    """判断评论是否有效
    
    Args:
        text: 评论文本
        min_length: 最小长度
    
    Returns:
        bool: 是否有效
    """
    if not text or len(text) < min_length:
        return False
    
    # 检查是否只包含表情符号
    # 可以根据需要添加更多过滤规则
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags
        "]+", flags=re.UNICODE)
    
    text_without_emoji = emoji_pattern.sub('', text)
    
    if len(text_without_emoji.strip()) < min_length:
        return False
    
    return True
