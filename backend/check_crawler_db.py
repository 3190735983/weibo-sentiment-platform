"""
检查MediaCrawler数据库的内容（正确路径版本）
"""
import sqlite3
import os

def check_mediacrawler_db():
    """检查MediaCrawler数据库"""
    # 正确的数据库路径
    db_path = '../MediaCrawler/database/sqlite_tables.db'
    
    if not os.path.exists(db_path):
        print(f"❌ MediaCrawler数据库不存在: {db_path}")
        return
    
    print("="*70)
    print("MediaCrawler数据库检查")
    print("="*70)
    print(f"\n数据库路径: {db_path}")
    print(f"文件大小: {os.path.getsize(db_path) / 1024:.2f} KB\n")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查看所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"数据库中的表: {[t[0] for t in tables]}\n")
        
        # 检查weibo相关的表
        for table_name in [t[0] for t in tables if 'weibo' in t[0].lower()]:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"✓ {table_name}: {count} 条记录")
            
            # 显示表结构
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            col_names = [col[1] for col in columns]
            print(f"  字段: {', '.join(col_names)}")
            
            # 显示示例数据
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
                rows = cursor.fetchall()
                print(f"\n  示例数据 (前2条):")
                for i, row in enumerate(rows, 1):
                    print(f"    记录{i}:")
                    for col_name, value in zip(col_names, row):
                        if value and len(str(value)) > 50:
                            value = str(value)[:50] + "..."
                        print(f"      {col_name}: {value}")
                print()
        
        # 总结
        print("="*70)
        print("总结")
        print("="*70)
        
        # 统计所有weibo表的记录数
        total_records = 0
        weibo_tables = [t[0] for t in tables if 'weibo' in t[0].lower()]
        
        for table_name in weibo_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_records += count
        
        if total_records > 0:
            print(f"✅ 找到 {len(weibo_tables)} 个微博相关表，共 {total_records} 条记录")
            print(f"\n可以运行同步脚本将数据导入主数据库:")
            print(f"   python sync_crawler_data.py")
        else:
            print(f"⚠️  数据库存在但没有数据")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ 数据库错误: {e}")
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_mediacrawler_db()
