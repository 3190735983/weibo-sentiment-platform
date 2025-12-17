"""
完整数据爬取流程脚本
1. 爬取热点话题
2. 保存到主数据库
3. 用MediaCrawler爬取每个话题的评论
4. 同步到主数据库
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from crawl_hot_topics import HotTopicCrawler
from app import create_app, db
from app.models import Topic
import subprocess
import re

def main():
    """主流程"""
    print("=" * 70)
    print("微博情感分析平台 - 数据爬取流程")
    print("=" * 70)
    
    # 敏感词过滤列表（避免爬取会被限制的话题）
    SENSITIVE_KEYWORDS = [
        '习近平', '李克强', '国务院', '政府', '中央',
        '主席', '总理', '述职', '政治', '党',
        '失业率', '经济', '国会', '议员'
    ]
    
    def is_sensitive_topic(topic_name):
        """检查话题是否包含敏感词"""
        for keyword in SENSITIVE_KEYWORDS:
            if keyword in topic_name:
                return True
        return False
    
    # 步骤1: 爬取热点话题
    print("\n[步骤1] 爬取微博热搜榜...")
    crawler = HotTopicCrawler()
    
    try:
        hot_topics = crawler.get_hot_topics(limit=20)  # 多爬一些以便过滤后还有足够数量
        
        if not hot_topics:
            print("❌ 未能获取热点话题，退出")
            return
        
        print(f"✅ 获取到 {len(hot_topics)} 个热点话题")
        
        # 过滤敏感话题
        print("\n[过滤] 检查并过滤敏感话题...")
        filtered_topics = []
        for topic_data in hot_topics:
            topic_text = topic_data['topic']
            topic_name = topic_text.replace('#', '').strip()
            
            if is_sensitive_topic(topic_name):
                print(f"  ⊘ 过滤: {topic_name} (包含敏感词)")
            else:
                filtered_topics.append(topic_data)
        
        hot_topics = filtered_topics[:10]  # 取过滤后的前10个
        print(f"✅ 过滤后剩余 {len(hot_topics)} 个话题")
        
        # 步骤2: 保存到数据库
        print("\n[步骤2] 保存话题到数据库...")
        app = create_app()
        
        with app.app_context():
            added_count = 0
            keywords = []
            
            for topic_data in hot_topics:
                topic_text = topic_data['topic']
                topic_name = topic_text.replace('#', '').strip()
                topic_tag = topic_text if topic_text.startswith('#') else f"#{topic_text}#"
                
                existing = Topic.query.filter_by(topic_tag=topic_tag).first()
                
                if not existing:
                    new_topic = Topic(
                        topic_name=topic_name,
                        topic_tag=topic_tag,
                        is_active=True
                    )
                    db.session.add(new_topic)
                    added_count += 1
                    keywords.append(topic_name)
                    print(f"  ✅ 添加: {topic_name}")
                else:
                    keywords.append(topic_name)
                    print(f"  ℹ️  已存在: {topic_name}")
            
            if added_count > 0:
                db.session.commit()
                print(f"\n成功添加 {added_count} 个新话题")
        
        # 步骤3: 更新MediaCrawler配置
        print("\n[步骤3] 更新MediaCrawler配置...")
        config_path = "../MediaCrawler/config/base_config.py"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        keywords_str = ",".join(keywords[:5])  # 最多5个关键词
        new_content = re.sub(
            r'KEYWORDS = "[^"]*"',
            f'KEYWORDS = "{keywords_str}"',
            config_content
        )
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ 配置关键词: {keywords_str}")
        
        # 步骤4: 运行MediaCrawler
        print("\n[步骤4] 启动MediaCrawler爬取评论...")
        print("=" * 70)
        print("正在启动MediaCrawler...")
        print("=" * 70)
        
        # 切换到MediaCrawler目录运行
        os.chdir('../MediaCrawler')
        subprocess.run([
            'python', 'main.py',
            '--platform', 'wb',
            '--lt', 'cookie',
            '--type', 'search'
        ])
        
        print("\n" + "=" * 70)
        print("数据爬取完成！")
        print("=" * 70)
        print("\n数据已保存到:")
        print("- MediaCrawler数据库: MediaCrawler/data/weibo.db")
        print("\n下一步: 运行数据同步脚本同步到主数据库")
        
    finally:
        crawler.close_browser()

if __name__ == "__main__":
    main()
