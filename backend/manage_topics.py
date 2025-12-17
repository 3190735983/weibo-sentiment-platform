"""
删除指定话题的脚本
"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import Topic, WeiboPost, Keyword

def delete_topic_by_name(topic_name):
    """根据话题名删除话题及相关数据"""
    app = create_app()
    
    with app.app_context():
        # 查找话题
        topic = Topic.query.filter(
            (Topic.topic_name.contains(topic_name)) |
            (Topic.topic_tag.contains(topic_name))
        ).first()
        
        if not topic:
            print(f"❌ 未找到包含 '{topic_name}' 的话题")
            return False
        
        print(f"\n找到话题: {topic.topic_name}")
        print(f"话题标签: {topic.topic_tag}")
        print(f"话题ID: {topic.id}")
        
        # 统计关联数据
        posts_count = WeiboPost.query.filter_by(topic_id=topic.id).count()
        keywords_count = Keyword.query.filter_by(topic_id=topic.id).count()
        
        print(f"\n关联数据:")
        print(f"  微博数: {posts_count}")
        print(f"  关键词数: {keywords_count}")
        
        # 确认删除
        confirm = input(f"\n确定要删除话题 '{topic.topic_name}' 及其所有关联数据吗? (yes/no): ")
        
        if confirm.lower() == 'yes':
            # 删除话题（cascade会自动删除关联的posts和keywords）
            db.session.delete(topic)
            db.session.commit()
            
            print(f"\n✅ 已删除话题: {topic.topic_name}")
            print(f"   同时删除了 {posts_count} 条微博和 {keywords_count} 个关键词")
            return True
        else:
            print("\n❌ 取消删除操作")
            return False

def list_all_topics():
    """列出所有话题"""
    app = create_app()
    
    with app.app_context():
        topics = Topic.query.all()
        
        print("\n" + "="*70)
        print("所有话题列表")
        print("="*70)
        
        if not topics:
            print("数据库中没有话题")
            return
        
        for i, topic in enumerate(topics, 1):
            posts_count = WeiboPost.query.filter_by(topic_id=topic.id).count()
            status = "✓" if topic.is_active else "✗"
            print(f"{i}. {status} {topic.topic_name}")
            print(f"   标签: {topic.topic_tag}")
            print(f"   微博数: {posts_count}")
            print()

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='话题管理脚本')
    parser.add_argument('--list', action='store_true', help='列出所有话题')
    parser.add_argument('--delete', type=str, help='删除包含指定关键词的话题')
    
    args = parser.parse_args()
    
    if args.list:
        list_all_topics()
    elif args.delete:
        delete_topic_by_name(args.delete)
    else:
        # 交互模式
        print("="*70)
        print("话题管理")
        print("="*70)
        print("\n1. 列出所有话题")
        print("2. 删除话题")
        print("3. 退出")
        
        choice = input("\n请选择操作 (1/2/3): ")
        
        if choice == '1':
            list_all_topics()
        elif choice == '2':
            keyword = input("\n请输入要删除的话题关键词: ")
            delete_topic_by_name(keyword)
        else:
            print("退出")

if __name__ == "__main__":
    main()
