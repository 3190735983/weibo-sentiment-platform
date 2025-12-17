# 完整测试流程指南

## 状态检查

看起来之前启动的Flask服务可能已经停止了。让我们重新启动并测试。

## 步骤1: 启动Flask后端服务

```bash
# 在backend目录
cd backend
.\venv\Scripts\python.exe run.py
```

**应该看到**:
```
Starting Flask server on http://0.0.0.0:5000
 * Running on http://0.0.0.0:5000
 * Restarting with stat
 * Debugger is active!
```

**保持这个终端运行！** 不要关闭

## 步骤2: 在新终端测试API

打开**新的**PowerShell终端，执行：

```bash
cd backend
.\venv\Scripts\python.exe test_api.py
```

## 步骤3: 或使用浏览器测试

### 3.1 基础测试
在浏览器打开:
- http://localhost:5000/ （应该返回API信息）
- http://localhost:5000/health （健康检查）
- http://localhost:5000/api/manage/topics （话题列表）

### 3.2 使用浏览器开发者工具

按F12打开开发者工具，在Console中执行：

```javascript
// 1. 获取话题列表
fetch('http://localhost:5000/api/manage/topics')
  .then(r => r.json())
  .then(d => console.log('话题列表:', d))

// 2. 执行情感分析
fetch('http://localhost:5000/api/sentiment/analyze', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({topic_id: 1})
})
  .then(r => r.json())
  .then(d => console.log('分析结果:', d))

// 3. 查看情感分布
fetch('http://localhost:5000/api/sentiment/results?topic_id=1')
  .then(r => r.json())
  .then(d => console.log('情感分布:', d))

// 4. 单条预测
fetch('http://localhost:5000/api/sentiment/predict', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({text: '这个产品真的很好用！'})
})
  .then(r => r.json())
  .then(d => console.log('预测结果:', d))
```

## 步骤4: 使用curl（如果有）

```bash
# 获取话题列表
curl http://localhost:5000/api/manage/topics

# 执行情感分析
curl -X POST http://localhost:5000/api/sentiment/analyze -H "Content-Type: application/json" -d "{\"topic_id\": 1}"

# 查看结果
curl http://localhost:5000/api/sentiment/results?topic_id=1

# 单条预测
curl -X POST http://localhost:5000/api/sentiment/predict -H "Content-Type: application/json" -d "{\"text\": \"这个产品真的很好用！\"}"
```

## 预期结果

### 1. 话题列表
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "topic_name": "人工智能",
      "topic_tag": "#人工智能#",
      "is_active": true
    },
    // ...更多话题
  ]
}
```

### 2. 情感分析
```json
{
  "success": true,
  "message": "情感分析完成，分析了15条评论",
  "data": {
    "analyzed_count": 15,
    "success": true
  }
}
```

### 3. 情感分布
```json
{
  "success": true,
  "data": {
    "distribution": {
      "正面": 5,
      "负面": 5,
      "中性": 5
    },
    "percentages": {
      "正面": 33.33,
      "负面": 33.33,
      "中性": 33.33
    },
    "total": 15
  }
}
```

### 4. 单条预测
```json
{
  "success": true,
  "data": {
    "label": "正面",
    "score": 0.95,
    "intensity": 0.95
  }
}
```

## 故障排查

### 问题1: 端口被占用
```
Error: Address already in use
```
**解决**: 
```bash
# 找到占用5000端口的进程
netstat -ano | findstr :5000
# 杀掉进程（替换PID）
taskkill /PID <PID> /F
```

### 问题2: 模块导入错误
```
ModuleNotFoundError: No module named 'app'
```
**解决**: 确保在backend目录下运行

### 问题3: 数据库错误
```
OperationalError: no such table
```
**解决**: 删除数据库重新创建
```bash
del weibo_sentiment.db
.\venv\Scripts\python.exe run.py
```

## 快速验证命令

在浏览器中访问这些URL快速验证：

1. ✅ 基础: http://localhost:5000/
2. ✅ 健康: http://localhost:5000/health
3. ✅ 话题: http://localhost:5000/api/manage/topics

如果这3个都能正常访问，说明后端服务运行正常！
