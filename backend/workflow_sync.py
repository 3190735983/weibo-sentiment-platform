"""
完整的爬虫数据检查和同步流程
"""
import subprocess
import sys
import os

def main():
    print("="*70)
    print("MediaCrawler数据检查与同步")
    print("="*70)
    
    # 1. 先检查数据库状态
    print("\n[步骤1] 检查MediaCrawler数据库...")
    result = subprocess.run([
        sys.executable, 
        'inspect_db.py'
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.returncode != 0:
        print(f"错误: {result.stderr}")
    
    # 2. 询问是否运行同步
    print("\n[步骤2] 准备同步数据...")
    response = input("是否运行数据同步? (yes/no): ")
    
    if response.lower() == 'yes':
        print("\n开始同步...")
        result = subprocess.run([
            sys.executable,
            'sync_crawler_data.py'
        ])
        
        if result.returncode == 0:
            print("\n✅ 同步完成！")
            
            #3. 显示统计
            print("\n[步骤3] 查看主数据库统计...")
            result = subprocess.run([
                sys.executable,
                'test_full_processing.py',
                '--mode', 'stats'
            ])
    else:
        print("\n跳过同步")
    
    print("\n"+ "="*70)
    print("完成")
    print("="*70)

if __name__ == "__main__":
    main()
