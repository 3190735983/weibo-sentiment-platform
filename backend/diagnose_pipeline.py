"""诊断Pipeline执行结果"""
from app import create_app, db
from app.models import Topic, WeiboPost, Keyword, SentimentResult

app = create_app()

with app.app_context():
    print("=== 数据库当前状态 ===\n")
    
    # 话题统计
    topic_count = Topic.query.count()
    print(f"总话题数: {topic_count}")
    
    # 获取最新的话题
    latest_topic = Topic.query.order_by(Topic.created_at.desc()).first()
    if latest_topic:
        print(f"最新话题: {latest_topic.topic_name} (ID: {latest_topic.id})")
        print(f"创建时间: {latest_topic.created_at}")
    
    # 微博统计
    post_count = WeiboPost.query.count()
    print(f"\n总微博数: {post_count}")
    
    if post_count > 0:
        # 按话题分组统计
        print("\n各话题微博数:")
        topics = Topic.query.all()
        for topic in topics[:10]:
            posts = WeiboPost.query.filter_by(topic_id=topic.id).count()
            if posts > 0:
                print(f"  - {topic.topic_name}: {posts}条")
    
    # 关键词统计
    keyword_count = Keyword.query.count()
    print(f"\n总关键词数: {keyword_count}")
    
    if keyword_count > 0:
        # 按话题分组
        print("\n各话题关键词数:")
        topics = Topic.query.all()
        for topic in topics[:10]:
            keywords = Keyword.query.filter_by(topic_id=topic.id).count()
            if keywords > 0:
                print(f"  - {topic.topic_name}: {keywords}个关键词")
        
        # 显示一些示例关键词
        print("\n最新关键词示例:")
        recent_keywords = Keyword.query.order_by(Keyword.analyzed_at.desc()).limit(10).all()
        for kw in recent_keywords:
            topic = Topic.query.get(kw.topic_id)
            print(f"  - {kw.keyword} (频次:{kw.frequency}, 话题:{topic.topic_name if topic else 'N/A'})")
    
    # 情感分析统计
    sentiment_count = SentimentResult.query.count()
    print(f"\n总情感分析数: {sentiment_count}")
    
    if sentiment_count > 0:
        # 统计各类情感
        from sqlalchemy import func
        sentiment_stats = db.session.query(
            SentimentResult.sentiment_label,
            func.count(SentimentResult.id)
        ).group_by(SentimentResult.sentiment_label).all()
        
        print("\n情感分布:")
        for label, count in sentiment_stats:
            print(f"  - {label}: {count}条")
    
    print("\n=== MediaCrawler数据库检查 ===\n")
    import sqlite3
    import os
    
    mc_db_path = '../MediaCrawler/database/sqlite_tables.db'
    if os.path.exists(mc_db_path):
        mc_conn = sqlite3.connect(mc_db_path)
        mc_cursor = mc_conn.cursor()
        
        mc_cursor.execute("SELECT COUNT(*) FROM weibo_note")
        note_count = mc_cursor.fetchone()[0]
        print(f"MediaCrawler微博数: {note_count}")
        
        mc_cursor.execute("SELECT COUNT(*) FROM weibo_note_comment")
        comment_count = mc_cursor.fetchone()[0]
        print(f"MediaCrawler评论数: {comment_count}")
        
        mc_conn.close()
    else:
        print("⚠️  MediaCrawler数据库不存在")
