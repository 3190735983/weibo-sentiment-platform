# 问题解答和解决方案

## 用户的三个问题

### 1. 第一个爬取热点为什么启动这么慢？

**原因**:
- Selenium需要启动一个真实的Chrome浏览器
- 浏览器需要加载页面、JavaScript等
- 这是正常的，第一次启动通常需要3-5秒

**优化建议**:
- 可以启用无头模式（headless）加快速度：
  ```python
  # 在 crawl_hot_topics.py 中
  self.browser_options.add_argument("--headless")
  ```
- 但建议第一次保持可见，方便调试

### 2. AUTO_CLOSE_BROWSER = True 但为什么还是启动了浏览器？

**说明**:
- `AUTO_CLOSE_BROWSER` 控制的是**程序结束时是否关闭浏览器**
- 不是控制**是否启动浏览器**
- 爬虫必须启动浏览器才能工作，这是正常的
- True = 爬取完成后自动关闭浏览器
- False = 爬取完成后保持浏览器打开（方便调试）

### 3. 为什么中断了？

**核心原因**: MediaCrawler数据库没有初始化

```
sqlite3.OperationalError: no such table: weibo_note
```

**解决方案**: 

#### 方法一：手动初始化（推荐）
```bash
cd MediaCrawler
python main.py --init_db sqlite
```

#### 方法二：使用修复后的脚本
我已经修复了 `run_full_crawler.py`，现在会自动初始化数据库。

## 正确的使用流程

1. **首次使用 - 初始化MediaCrawler数据库**:
   ```bash
   cd MediaCrawler
   python main.py --init_db sqlite
   ```

2. **运行完整爬取流程**:
   ```bash
   cd backend
   .\venv\Scripts\python.exe run_full_crawler.py
   ```

3. **同步数据到主数据库**:
   ```bash
   .\venv\Scripts\python.exe sync_crawler_data.py
   ```

## 修复记录

✅ 已手动初始化MediaCrawler数据库
✅ 数据库文件：`MediaCrawler/data/weibo.db`
✅ 现在可以正常爬取了

## 下次运行

直接运行即可，不需要再初始化：
```bash
cd backend
.\venv\Scripts\python.exe run_full_crawler.py
```
