"""快速验证 - 同步MediaCrawler现有数据"""
from app import create_app
from app.services.crawler_service import CrawlerService

app = create_app()

with app.app_context():
    print("=== 同步MediaCrawler数据 ===\n")
    
    service = CrawlerService()
    result = service.sync_mediacrawler_data()
    
    print(f"状态: {result['status']}")
    print(f"新增: {result['posts_added']}条")
    print(f"跳过: {result['posts_skipped']}条")
    print(f"消息: {result['message']}")
    
    if result['posts_added'] > 0:
        print("\n✅ 同步成功!现在可以:")
        print("1. 刷新前端页面")
        print("2. 在可视化页面查看数据")
        print("3. 选择有微博数量的话题")
    else:
        print("\n⚠️ 没有新数据可同步")
        print("MediaCrawler数据库中的数据已经全部同步过了")
        print("\n要获取新数据,需要:")
        print("1. 运行 MediaCrawler 爬虫")
        print("2. 等待爬取完成")
        print("3. 再次运行此脚本同步")
