"""诊断MediaCrawler数据同步问题"""
import sqlite3
import os

# 检查MediaCrawler数据库
mc_db_path = '../MediaCrawler/database/sqlite_tables.db'

if not os.path.exists(mc_db_path):
    print(f"❌ MediaCrawler数据库不存在: {mc_db_path}")
    exit(1)

print(f"✅ MediaCrawler数据库存在: {mc_db_path}")
print(f"文件大小: {os.path.getsize(mc_db_path) / 1024:.2f} KB\n")

conn = sqlite3.connect(mc_db_path)
cursor = conn.cursor()

# 检查表结构
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("=== 数据库表 ===")
for table in tables:
    print(f"  - {table[0]}")

print("\n=== weibo_note 表统计 ===")
cursor.execute("SELECT COUNT(*) FROM weibo_note")
note_count = cursor.fetchone()[0]
print(f"总记录数: {note_count}")

if note_count > 0:
    cursor.execute("SELECT note_id, content, source_keyword, create_time FROM weibo_note LIMIT 5")
    notes = cursor.fetchall()
    print("\n前5条记录:")
    for i, note in enumerate(notes, 1):
        print(f"\n{i}. Note ID: {note[0]}")
        print(f"   内容: {note[1][:100]}...")
        print(f"   关键词: {note[2]}")
        print(f"   时间: {note[3]}")

print("\n=== weibo_note_comment 表统计 ===")
cursor.execute("SELECT COUNT(*) FROM weibo_note_comment")
comment_count = cursor.fetchone()[0]
print(f"总记录数: {comment_count}")

if comment_count > 0:
    cursor.execute("SELECT comment_id, content, create_time FROM weibo_note_comment LIMIT 5")
    comments = cursor.fetchall()
    print("\n前5条评论:")
    for i, comment in enumerate(comments, 1):
        print(f"\n{i}. Comment ID: {comment[0]}")
        print(f"   内容: {comment[1][:100]}...")
        print(f"   时间: {comment[2]}")

conn.close()

# 检查主数据库
print("\n" + "="*50)
print("=== 主数据库检查 ===")

from app import create_app, db
from app.models import Topic, WeiboPost

app = create_app()

with app.app_context():
    topic_count = Topic.query.count()
    post_count = WeiboPost.query.count()
    
    print(f"话题数量: {topic_count}")
    print(f"微博数量: {post_count}")
    
    if topic_count > 0:
        print("\n现有话题:")
        topics = Topic.query.all()
        for topic in topics:
            posts_count = WeiboPost.query.filter_by(topic_id=topic.id).count()
            print(f"  - {topic.topic_name} (ID: {topic.id}, 微博数: {posts_count})")
