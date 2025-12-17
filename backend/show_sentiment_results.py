"""
查看情感分析结果
"""
import sys
sys.path.insert(0, '.')

from app import create_app
from app.models import Topic, SentimentResult, WeiboPost
from app import db

def show_sentiment_stats():
    """显示情感分析统计"""
    app = create_app()
    
    with app.app_context():
        print("="*70)
        print("情感分析结果统计")
        print("="*70)
        
        # 总统计
        total_posts = WeiboPost.query.count()
        total_analyzed = SentimentResult.query.count()
        
        print(f"\n总体统计:")
        print(f"  总微博数: {total_posts}")
        print(f"  已分析数: {total_analyzed}")
        print(f"  分析率: {total_analyzed/total_posts*100:.1f}%" if total_posts > 0 else "  分析率: 0%")
        
        # 情感分布
        positive_count = SentimentResult.query.filter_by(sentiment_label='正面').count()
        negative_count = SentimentResult.query.filter_by(sentiment_label='负面').count()
        neutral_count = SentimentResult.query.filter_by(sentiment_label='中性').count()
        
        print(f"\n整体情感分布:")
        if total_analyzed > 0:
            print(f"  正面: {positive_count} 条 ({positive_count/total_analyzed*100:.1f}%)")
            print(f"  负面: {negative_count} 条 ({negative_count/total_analyzed*100:.1f}%)")
            print(f"  中性: {neutral_count} 条 ({neutral_count/total_analyzed*100:.1f}%)")
        else:
            print(f"  无数据")
        
        # 各话题统计
        topics = Topic.query.all()
        
        print(f"\n各话题情感分布:")
        print("-"*70)
        
        for topic in topics:
            # 查询该话题的情感统计
            results = db.session.query(
                SentimentResult.sentiment_label,
                db.func.count(SentimentResult.id).label('count')
            ).join(
                WeiboPost, SentimentResult.weibo_id == WeiboPost.id
            ).filter(
                WeiboPost.topic_id == topic.id
            ).group_by(
                SentimentResult.sentiment_label
            ).all()
            
            dist = {'正面': 0, '负面': 0, '中性': 0}
            total = 0
            for label, count in results:
                dist[label] = count
                total += count
            
            if total > 0:
                print(f"\n{topic.topic_name} (ID: {topic.id})")
                print(f"  分析数: {total}")
                print(f"  正面: {dist['正面']} ({dist['正面']/total*100:.1f}%)")
                print(f"  负面: {dist['负面']} ({dist['负面']/total*100:.1f}%)")
                print(f"  中性: {dist['中性']} ({dist['中性']/total*100:.1f}%)")
        
        # 显示一些示例
        print(f"\n\n示例分析结果 (最新10条):")
        print("-"*70)
        
        samples = db.session.query(
            WeiboPost.content,
            SentimentResult.sentiment_label,
            SentimentResult.sentiment_score,
            Topic.topic_name
        ).join(
            SentimentResult, WeiboPost.id == SentimentResult.weibo_id
        ).join(
            Topic, WeiboPost.topic_id == Topic.id
        ).order_by(
            SentimentResult.analyzed_at.desc()
        ).limit(10).all()
        
        for i, (content, label, score, topic_name) in enumerate(samples, 1):
            content_preview = content[:50] + "..." if len(content) > 50 else content
            print(f"\n{i}. [{label}] {score:.2f} - {topic_name}")
            print(f"   {content_preview}")
        
        print("\n" + "="*70)

if __name__ == "__main__":
    show_sentiment_stats()
