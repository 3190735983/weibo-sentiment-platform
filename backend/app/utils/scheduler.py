from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime


class CrawlerScheduler:
    """爬虫定时调度器"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.is_running = False
    
    def start(self, crawler_func, interval_hours=2):
        """启动定时任务
        
        Args:
            crawler_func: 爬虫函数
            interval_hours: 时间间隔（小时）
        """
        if not self.is_running:
            self.scheduler.add_job(
                crawler_func,
                'interval',
                hours=interval_hours,
                id='weibo_crawler',
                replace_existing=True
            )
            self.scheduler.start()
            self.is_running = True
            print(f"定时任务已启动，每{interval_hours}小时执行一次")
    
    def stop(self):
        """停止定时任务"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            print("定时任务已停止")
    
    def get_status(self):
        """获取调度器状态"""
        return {
            'is_running': self.is_running,
            'jobs': [str(job) for job in self.scheduler.get_jobs()] if self.is_running else []
        }
