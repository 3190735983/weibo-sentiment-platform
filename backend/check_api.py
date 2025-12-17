"""
检查API导入和注册
"""
import sys
sys.path.insert(0, '.')

try:
    print("测试导入...")
    
    # 测试导入api模块
    from app.api import crawler_bp, pipeline_bp
    print("[OK] 成功导入 crawler_bp 和 pipeline_bp")
    
    # 检查blueprint配置
    print(f"\ncrawler_bp URL前缀: {crawler_bp.url_prefix}")
    print(f"pipeline_bp URL前缀: {pipeline_bp.url_prefix}")
    
    # 列出所有规则
    print(f"\ncrawler_bp 路由:")
    for rule in crawler_bp.url_prefix or []:
        print(f"  {rule}")
    
    print(f"\npipeline_bp 路由:")
    for rule in pipeline_bp.url_prefix or []:
        print(f"  {rule}")
    
    # 测试create_app
    from app import create_app
    app = create_app()
    
    print("\n所有注册的路由:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} [{', '.join(rule.methods - {'OPTIONS', 'HEAD'})}]")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
