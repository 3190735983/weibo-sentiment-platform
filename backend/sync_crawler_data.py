"""
从MediaCrawler的SQLite数据库同步数据到主数据库
根据MediaCrawler的实际表结构: WeiboNote 和 WeiboNoteComment
"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import Topic, WeiboPost
import sqlite3
from datetime import datetime

def sync_from_mediacrawler():
    """从MediaCrawler数据库同步数据"""
    app = create_app()
    
    print("=" * 70)
    print("数据同步 - MediaCrawler SQLite → 主数据库")
    print("=" * 70)
    
    # 连接MediaCrawler数据库（正确路径）
    mc_db_path = '../MediaCrawler/database/sqlite_tables.db'
    
    try:
        mc_conn = sqlite3.connect(mc_db_path)
        mc_conn.row_factory = sqlite3.Row
        mc_cursor = mc_conn.cursor()
        
        print(f"\n✅ 连接到MediaCrawler数据库: {mc_db_path}")
        
        # 1. 查询微博内容数据 (WeiboNote)
        mc_cursor.execute("SELECT * FROM weibo_note ORDER BY add_ts DESC")
        notes = mc_cursor.fetchall()
        print(f"找到 {len(notes)} 条微博内容记录")
        
        # 2. 查询评论数据 (WeiboNoteComment)
        mc_cursor.execute("SELECT * FROM weibo_note_comment ORDER BY add_ts DESC")
        comments = mc_cursor.fetchall()
        print(f"找到 {len(comments)} 条评论记录\n")
        
        with app.app_context():
            added_posts = 0
            skipped_posts = 0
            
            # 3. 同步微博内容
            print("同步微博内容...")
            for note in notes:
                added, skipped = sync_note(note)
                added_posts += added
                skipped_posts += skipped
                
                if added_posts % 10 == 0 and added_posts > 0:
                    db.session.commit()
                    print(f"  已同步 {added_posts} 条...")
            
            # 4. 同步评论
            print("\n同步评论...")
            for comment in comments:
                added, skipped = sync_comment(comment)
                added_posts += added
                skipped_posts += skipped
                
                if added_posts % 10 == 0:
                    db.session.commit()
                    print(f"  已同步 {added_posts} 条...")
            
            db.session.commit()
            
            print(f"\n{'='*70}")
            print(f"同步完成！")
            print(f"  ✅ 新增: {added_posts} 条")
            print(f"  ℹ️  跳过: {skipped_posts} 条（已存在）")
            print(f"{'='*70}")
            
            # 5. 统计
            total = WeiboPost.query.count()
            print(f"\n主数据库统计:")
            print(f"  总微博数: {total}")
            print(f"  总话题数: {Topic.query.count()}")
        
    except sqlite3.Error as e:
        print(f"❌ 数据库错误: {e}")
    except Exception as e:
        print(f"❌ 同步失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'mc_conn' in locals():
            mc_conn.close()

def safe_get(row, key, default=''):
    """安全获取sqlite3.Row的值"""
    try:
        return row[key] if row[key] is not None else default
    except (KeyError, IndexError):
        return default

def sync_note(note):
    """同步单条微博内容"""
    try:
        # 检查是否已存在
        note_id = str(note['note_id'])
        existing = WeiboPost.query.filter_by(weibo_id=note_id).first()
        if existing:
            return 0, 1
        
        # 提取话题
        content = safe_get(note, 'content', '')
        topic = find_or_create_topic(content, safe_get(note, 'source_keyword', ''))
        if not topic:
            return 0, 0
        
        # 创建微博记录
        post = WeiboPost(
            topic_id=topic.id,
            weibo_id=note_id,
            content=content,
            topic_text=topic.topic_tag,
            comment_text=content,
            user_nickname=safe_get(note, 'nickname', '未知用户'),
            user_fans_count=0,
            publish_time=parse_timestamp(safe_get(note, 'create_time')),
            likes_count=safe_int(safe_get(note, 'liked_count')),
            reposts_count=safe_int(safe_get(note, 'shared_count')),
            comments_count=safe_int(safe_get(note, 'comments_count')),
            location=safe_get(note, 'ip_location', ''),
            created_at=datetime.utcnow()
        )
        
        db.session.add(post)
        return 1, 0
        
    except Exception as e:
        print(f"  错误处理note {safe_get(note, 'note_id', 'unknown')}: {e}")
        return 0, 0

def sync_comment(comment):
    """同步单条评论"""
    try:
        # 检查是否已存在
        comment_id = str(comment['comment_id'])
        existing = WeiboPost.query.filter_by(weibo_id=comment_id).first()
        if existing:
            return 0, 1
        
        # 找出评论所属的微博话题
        content = safe_get(comment, 'content', '')
        note_id = comment['note_id']
        
        # 尝试从note_id对应的微博找话题
        existing_post = WeiboPost.query.filter_by(weibo_id=str(note_id)).first()
        if existing_post:
            topic = Topic.query.get(existing_post.topic_id)
        else:
            topic = find_or_create_topic(content, None)
        
        if not topic:
            return 0, 0
        
        # 创建微博记录（评论也存为WeiboPost）
        post = WeiboPost(
            topic_id=topic.id,
            weibo_id=comment_id,
            content=content,
            topic_text=topic.topic_tag,
            comment_text=content,
            user_nickname=safe_get(comment, 'nickname', '未知用户'),
            user_fans_count=0,
            publish_time=parse_timestamp(safe_get(comment, 'create_time')),
            likes_count=safe_int(safe_get(comment, 'comment_like_count')),
            reposts_count=0,
            comments_count=safe_int(safe_get(comment, 'sub_comment_count')),
            location=safe_get(comment, 'ip_location', ''),
            created_at=datetime.utcnow()
        )
        
        db.session.add(post)
        return 1, 0
        
    except Exception as e:
        print(f"  错误处理comment {safe_get(comment, 'comment_id', 'unknown')}: {e}")
        return 0, 0

def find_or_create_topic(content, source_keyword):
    """查找或创建话题"""
    import re
    
    # 1. 从内容中提取话题
    topic_name = None
    if content:
        match = re.search(r'#([^#]+)#', content)
        if match:
            topic_name = match.group(1).strip()
    
    # 2. 使用source_keyword
    if not topic_name and source_keyword:
        topic_name = source_keyword.strip()
    
    # 3. 查找话题
    if topic_name:
        topic = Topic.query.filter(
            (Topic.topic_name == topic_name) |
            (Topic.topic_tag.contains(topic_name))
        ).first()
        if topic:
            return topic
    
    # 4. 使用第一个话题作为默认
    topic = Topic.query.first()
    if not topic:
        print("  ⚠️  数据库中没有话题，请先添加话题")
        return None
    
    return topic

def parse_timestamp(ts):
    """解析时间戳"""
    try:
        if not ts:
            return datetime.now()
        
        # 如果是BigInt时间戳（秒或毫秒）
        if isinstance(ts, (int, float)):
            if ts > 10000000000:  # 毫秒
                return datetime.fromtimestamp(ts / 1000)
            else:  # 秒
                return datetime.fromtimestamp(ts)
        
        # 如果是字符串
        if isinstance(ts, str):
            try:
                return datetime.fromisoformat(ts)
            except:
                pass
        
        return datetime.now()
    except:
        return datetime.now()

def safe_int(value):
    """安全转换为整数"""
    try:
        if value is None or value == '':
            return 0
        return int(value)
    except:
        return 0

if __name__ == "__main__":
    sync_from_mediacrawler()
