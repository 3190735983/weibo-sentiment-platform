# 将爬取的热点话题添加到数据库
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import Topic
import json

def import_hot_topics():
    """从JSON导入热点话题"""
    app = create_app()
    
    with app.app_context():
        print("=" * 70)
        print("导入真实热点话题")
        print("=" * 70)
        
        # 读取JSON文件
        try:
            with open('hot_topics.json', 'r', encoding='utf-8') as f:
                topics_data = json.load(f)
            
            print(f"\n✅ 从JSON读取到 {len(topics_data)} 个话题\n")
        except FileNotFoundError:
            print("❌ 未找到 hot_topics.json 文件")
            return
        
        added_count = 0
        updated_count = 0
        
        for topic_data in topics_data:
            topic_text = topic_data['topic']
            heat = topic_data.get('heat', '')
            
            # 清理话题名称
            topic_name = topic_text.replace('#', '').strip()
            topic_tag = topic_text if topic_text.startswith('#') else f"#{topic_text}#"
            
            # 检查是否已存在
            existing = Topic.query.filter_by(topic_tag=topic_tag).first()
            
            if not existing:
                new_topic = Topic(
                    topic_name=topic_name,
                    topic_tag=topic_tag,
                    is_active=True
                )
                db.session.add(new_topic)
                added_count += 1
                print(f"✅ 添加: {topic_name} ({heat})")
            else:
                # 更新现有话题状态
                existing.is_active = True
                updated_count += 1
                print(f"ℹ️  已存在: {topic_name} ({heat})")
        
        # 提交到数据库
        if added_count > 0 or updated_count > 0:
            db.session.commit()
            print(f"\n✅ 成功添加 {added_count} 个新话题")
            print(f"✅ 更新 {updated_count} 个已有话题")
        else:
            print("\n所有话题已存在")
        
        # 显示数据库统计
        total_topics = Topic.query.count()
        active_topics = Topic.query.filter_by(is_active=True).count()
        
        print(f"\n数据库统计:")
        print(f"  总话题数: {total_topics}")
        print(f"  活跃话题: {active_topics}")
        
        print("\n" + "=" * 70)
        print("导入完成！")
        print("=" * 70)

if __name__ == "__main__":
    import_hot_topics()
