"""
情感分析完整流程
1. 读取微博评论
2. 使用数据清洗服务清洗文本
3. 输入情感分析模型
4. 保存结果到数据库
"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import Topic, WeiboPost, SentimentResult
from app.services.sentiment_service import SentimentAnalysisService
from app.services.data_processing_service import DataProcessingService
from datetime import datetime


def analyze_sentiment_for_topic(topic_id, use_cleaned_text=True):
    """
    对指定话题进行情感分析（使用清洗后的文本）
    
    Args:
        topic_id: 话题ID
        use_cleaned_text: 是否使用清洗后的文本
    
    Returns:
        分析结果统计
    """
    app = create_app()
    
    with app.app_context():
        # 获取话题信息
        topic = Topic.query.get(topic_id)
        if not topic:
            print(f"❌ 话题 {topic_id} 不存在")
            return None
        
        print("="*70)
        print(f"情感分析 - {topic.topic_name}")
        print("="*70)
        
        # 初始化服务
        sentiment_service = SentimentAnalysisService()
        if not sentiment_service.load_model():
            print("❌ 情感分析模型加载失败")
            return None
        
        # 如果使用清洗后的文本，初始化数据处理服务
        if use_cleaned_text:
            print("\n使用数据清洗服务处理文本")
            data_service = DataProcessingService()
        
        # 获取该话题下所有微博
        posts = WeiboPost.query.filter_by(topic_id=topic_id).all()
        print(f"\n找到 {len(posts)} 条微博/评论")
        
        analyzed_count = 0
        skipped_count = 0
        
        print("\n开始情感分析...")
        for i, post in enumerate(posts, 1):
            # 检查是否已经分析过
            existing_result = SentimentResult.query.filter_by(weibo_id=post.id).first()
            if existing_result:
                skipped_count += 1
                continue
            
            # 获取文本内容
            text = post.comment_text or post.content
            if not text or len(text.strip()) < 3:
                skipped_count += 1
                continue
            
            # 如果使用清洗，先清洗文本
            if use_cleaned_text:
                text = data_service.clean_text(text)
                if not text or len(text.strip()) < 3:
                    skipped_count += 1
                    continue
            
            # 预测情感
            result = sentiment_service.predict(text)
            
            # 保存结果
            sentiment_result = SentimentResult(
                weibo_id=post.id,
                sentiment_label=result['label'],
                sentiment_score=result['score'],
                sentiment_intensity=result['intensity'],
                analyzed_at=datetime.utcnow()
            )
            db.session.add(sentiment_result)
            analyzed_count += 1
            
            # 每10条提交一次
            if analyzed_count % 10 == 0:
                db.session.commit()
                print(f"  已分析: {analyzed_count}/{len(posts)}")
        
        db.session.commit()
        
        print(f"\n{'='*70}")
        print(f"分析完成！")
        print(f"  [+] 新分析: {analyzed_count} 条")
        print(f"  [i] 跳过: {skipped_count} 条（已分析或无效文本）")
        
        # 获取情感分布
        distribution = sentiment_service.get_sentiment_distribution(topic_id)
        
        print(f"\n情感分布:")
        print(f"  正面: {distribution['distribution']['正面']} 条 ({distribution['percentages']['正面']}%)")
        print(f"  负面: {distribution['distribution']['负面']} 条 ({distribution['percentages']['负面']}%)")
        print(f"  中性: {distribution['distribution']['中性']} 条 ({distribution['percentages']['中性']}%)")
        print(f"  总计: {distribution['total']} 条")
        print(f"{'='*70}\n")
        
        return {
            'status': 'success',
            'topic_name': topic.topic_name,
            'analyzed_count': analyzed_count,
            'skipped_count': skipped_count,
            'distribution': distribution
        }


def analyze_all_topics(use_cleaned_text=True):
    """批量分析所有话题"""
    app = create_app()
    
    with app.app_context():
        topics = Topic.query.filter_by(is_active=True).all()
        
        print("="*70)
        print(f"批量情感分析 - {len(topics)} 个话题")
        print("="*70)
        
        results = []
        for i, topic in enumerate(topics, 1):
            print(f"\n[{i}/{len(topics)}] 处理话题: {topic.topic_name}")
            result = analyze_sentiment_for_topic(topic.id, use_cleaned_text)
            if result:
                results.append(result)
        
        # 总结
        print("\n" + "="*70)
        print("批量分析总结")
        print("="*70)
        
        total_analyzed = sum(r['analyzed_count'] for r in results)
        total_skipped = sum(r['skipped_count'] for r in results)
        
        print(f"总计分析: {total_analyzed} 条")
        print(f"总计跳过: {total_skipped} 条")
        print(f"\n各话题分布:")
        
        for result in results:
            dist = result['distribution']
            print(f"\n  {result['topic_name']}:")
            print(f"    正面: {dist['percentages']['正面']}%")
            print(f"    负面: {dist['percentages']['负面']}%")
            print(f"    中性: {dist['percentages']['中性']}%")
        
        return results


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='情感分析脚本')
    parser.add_argument('--mode', type=str, default='single',
                       choices=['single', 'all'],
                       help='分析模式: single=单个话题, all=所有话题')
    parser.add_argument('--topic_id', type=int,
                       help='话题ID（single模式需要）')
    parser.add_argument('--no-clean', action='store_true',
                       help='不使用文本清洗（直接使用原始文本）')
    
    args = parser.parse_args()
    
    use_cleaned = not args.no_clean
    
    if args.mode == 'single':
        if not args.topic_id:
            # 如果没有指定topic_id，使用第一个话题
            app = create_app()
            with app.app_context():
                first_topic = Topic.query.first()
                if first_topic:
                    args.topic_id = first_topic.id
                    print(f"未指定topic_id，使用第一个话题: {first_topic.topic_name} (ID: {first_topic.id})")
                else:
                    print("❌ 数据库中没有话题")
                    return
        
        analyze_sentiment_for_topic(args.topic_id, use_cleaned)
    
    elif args.mode == 'all':
        analyze_all_topics(use_cleaned)


if __name__ == "__main__":
    main()
