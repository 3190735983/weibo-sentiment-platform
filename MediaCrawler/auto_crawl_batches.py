"""
多批次自动采集脚本 - 避免反爬
每批采集后自动休息，然后继续下一批
"""
import subprocess
import time
from datetime import datetime

# 配置不同批次的关键词
keyword_batches = [
    "纸片人老公,虚拟恋人,乙游男友,本命角色",
    "光与夜之恋,恋与深空",
    "未定事件簿,恋与制作人",
    "时空中的绘旅人,代号鸢",
    "乙游恋爱,游戏男友",
    "二次元老公,虚拟男友",
]

# 每批次采集设置
notes_per_batch = 60  # 每批60个帖子
sleep_between_batches = 180  # 批次间隔3分钟（180秒）

def update_config(keywords):
    """更新配置文件中的关键词"""
    config_file = "config/base_config.py"
    
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换关键词行
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('KEYWORDS = '):
            lines[i] = f'KEYWORDS = "{keywords}"'
            break
    
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ 已更新关键词: {keywords}")

def run_crawler():
    """运行爬虫"""
    print(f"🚀 开始爬取... ({datetime.now().strftime('%H:%M:%S')})")
    
    cmd = [
        r".\venv\Scripts\python.exe",
        "main.py",
        "--platform", "xhs",
        "--lt", "qrcode",
        "--type", "search"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        print(f"✅ 爬取完成 (返回码: {result.returncode})")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def main():
    print("=" * 60)
    print("📊 多批次自动采集脚本")
    print("=" * 60)
    print(f"总批次: {len(keyword_batches)}")
    print(f"每批帖子数: {notes_per_batch}")
    print(f"批次间隔: {sleep_between_batches}秒")
    print(f"预计总时间: {len(keyword_batches) * (sleep_between_batches / 60):.1f}分钟")
    print("=" * 60)
    
    total_success = 0
    
    for batch_num, keywords in enumerate(keyword_batches, 1):
        print(f"\n{'='*60}")
        print(f"📦 第 {batch_num}/{len(keyword_batches)} 批")
        print(f"{'='*60}")
        
        # 更新配置
        update_config(keywords)
        
        # 运行爬虫
        success = run_crawler()
        
        if success:
            total_success += 1
            print(f"✅ 第{batch_num}批完成")
        else:
            print(f"⚠️ 第{batch_num}批可能遇到问题")
        
        # 等待下一批（如果不是最后一批）
        if batch_num < len(keyword_batches):
            print(f"\n⏳ 等待 {sleep_between_batches} 秒后继续...")
            time.sleep(sleep_between_batches)
    
    print(f"\n{'='*60}")
    print(f"🎉 全部完成！")
    print(f"✅ 成功: {total_success}/{len(keyword_batches)} 批")
    print(f"📊 预计总数据: 约 {total_success * notes_per_batch} 个帖子")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
