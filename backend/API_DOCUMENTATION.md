# API接口文档

## 爬虫API (`/api/crawler`)

### 1. 爬取热点话题
```http
POST /api/crawler/hot-topics
Content-Type: application/json

{
  "limit": 10,
  "filter_sensitive": true
}
```

**响应**:
```json
{
  "status": "success",
  "topics_added": 5,
  "topics_filtered": 2,
  "topics": [
    {
      "name": "春节",
      "tag": "#春节#",
      "id": 10,
      "is_new": true
    }
  ],
  "message": "成功添加 5 个新话题, 过滤 2 个敏感话题"
}
```

### 2. 搜索话题
```http
POST /api/crawler/search
Content-Type: application/json

{
  "keyword": "春节"
}
```

**响应**:
```json
{
  "status": "success",
  "topic_id": 10,
  "topic_name": "春节",
  "is_new": true,
  "message": "创建新话题: 春节"
}
```

### 3. 同步数据
```http
POST /api/crawler/sync
```

**响应**:
```json
{
  "status": "success",
  "posts_added": 150,
  "posts_skipped": 10,
  "message": "同步完成: 新增150条, 跳过10条"
}
```

### 4. 获取状态
```http
GET /api/crawler/status
```

**响应**:
```json
{
  "status": "ready",
  "mediacrawler_db_exists": true,
  "topics_count": 42,
  "posts_count": 1250,
  "is_running": false
}
```

---

## Pipeline API (`/api/pipeline`)

### 1. 运行完整Pipeline
```http
POST /api/pipeline/run
Content-Type: application/json

{
  "mode": "hot_topics",
  "limit": 10,
  "steps": {
    "crawl": true,
    "sync": true,
    "keywords": true,
    "sentiment": true
  }
}
```

**响应**:
```json
{
  "status": "success",
  "results": {
    "topics_added": 5,
    "posts_synced": 150,
    "keywords_extracted": 400,
    "sentiments_analyzed": 150,
    "errors": []
  },
  "message": "Pipeline完成: 新增5话题, 同步150微博, 提取400关键词, 分析150情感"
}
```

### 2. 处理单个话题
```http
POST /api/pipeline/process/5
```

**响应**:
```json
{
  "status": "success",
  "results": {
    "keywords_count": 50,
    "sentiments_count": 100,
    "errors": []
  },
  "message": "处理完成: 提取50关键词, 分析100情感"
}
```

### 3. 获取Pipeline状态
```http
GET /api/pipeline/status
```

**响应**:
```json
{
  "is_running": false,
  "crawler_status": {
    "status": "ready",
    "topics_count": 42,
    "posts_count": 1250
  }
}
```

---

## 前端Vue调用示例

### 1. 爬取热点话题

```vue
<template>
  <div>
    <el-button @click="crawlHotTopics" :loading="crawling">
      爬取热点话题
    </el-button>
    
    <div v-if="result">
      <p>新增话题: {{ result.topics_added }}</p>
      <ul>
        <li v-for="topic in result.topics" :key="topic.id">
          {{ topic.name }} ({{ topic.is_new ? '新' : '已存在' }})
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      crawling: false,
      result: null
    }
  },
  methods: {
    async crawlHotTopics() {
      this.crawling = true
      try {
        const response = await axios.post('/api/crawler/hot-topics', {
          limit: 10,
          filter_sensitive: true
        })
        
        if (response.data.status === 'success') {
          this.result = response.data
          this.$message.success(response.data.message)
        } else {
          this.$message.error(response.data.message)
        }
      } catch (error) {
        this.$message.error('爬取失败: ' + error.message)
      } finally {
        this.crawling = false
      }
    }
  }
}
</script>
```

### 2. 搜索话题并处理

```vue
<template>
  <div>
    <el-input v-model="keyword" placeholder="输入话题关键词"></el-input>
    <el-button @click="searchAndProcess" :loading="processing">
      搜索并分析
    </el-button>
    
    <div v-if="result">
      <p>{{ result.message }}</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      keyword: '',
      processing: false,
      result: null
    }
  },
  methods:  {
    async searchAndProcess() {
      if (!this.keyword) {
        this.$message.warning('请输入关键词')
        return
      }
      
      this. processing = true
      try {
        // Step 1: 搜索话题
        const searchResponse = await axios.post('/api/crawler/search', {
          keyword: this.keyword
        })
        
        if (searchResponse.data.status !== 'success') {
          throw new Error(searchResponse.data.message)
        }
        
        const topicId = searchResponse.data.topic_id
        
        // Step 2: 处理话题
        const processResponse = await axios.post(`/api/pipeline/process/${topicId}`)
        
        if (processResponse.data.status === 'success') {
          this.result = processResponse.data
          this.$message.success('处理完成！')
        } else {
          this.$message.error(processResponse.data.message)
        }
      } catch (error) {
        this.$message.error('处理失败: ' + error.message)
      } finally {
        this.processing = false
      }
    }
  }
}
</script>
```

### 3. 运行完整Pipeline

```vue
<template>
  <div>
    <el-card>
      <h3>数据爬取与分析</h3>
      
      <el-radio-group v-model="mode">
        <el-radio label="hot_topics">爬取热点话题</el-radio>
        <el-radio label="search">搜索指定话题</el-radio>
      </el-radio-group>
      
      <el-input 
        v-if="mode === 'search'" 
        v-model="keyword" 
        placeholder="输入话题关键词"
      ></el-input>
      
      <el-input-number 
        v-if="mode === 'hot_topics'" 
        v-model="limit" 
        :min="1" 
        :max="20"
      ></el-input-number>
      
      <el-checkbox-group v-model="steps">
        <el-checkbox label="crawl">爬取</el-checkbox>
        <el-checkbox label="sync">同步</el-checkbox>
        <el-checkbox label="keywords">关键词</el-checkbox>
        <el-checkbox label="sentiment">情感</el-checkbox>
      </el-checkbox-group>
      
      <el-button 
        type="primary" 
        @click="runPipeline" 
        :loading="running"
      >
        运行Pipeline
      </el-button>
      
      <div v-if="pipelineResult" class="result">
        <h4>执行结果</h4>
        <p>新增话题: {{ pipelineResult.results.topics_added }}</p>
        <p>同步微博: {{ pipelineResult.results.posts_synced }}</p>
        <p>提取关键词: {{ pipelineResult.results.keywords_extracted }}</p>
        <p>情感分析: {{ pipelineResult.results.sentiments_analyzed }}</p>
        
        <div v-if="pipelineResult.results.errors.length > 0">
          <h5>错误:</h5>
          <ul>
            <li v-for="(error, index) in pipelineResult.results.errors" :key="index">
              {{ error }}
            </li>
          </ul>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      mode: 'hot_topics',
      keyword: '',
      limit: 10,
      steps: ['crawl', 'sync', 'keywords', 'sentiment'],
      running: false,
      pipelineResult: null
    }
  },
  methods: {
    async runPipeline() {
      if (this.mode === 'search' && !this.keyword) {
        this.$message.warning('请输入关键词')
        return
      }
      
      this.running = true
      try {
        const requestBody = {
          mode: this.mode,
          limit: this.limit,
          steps: {
            crawl: this.steps.includes('crawl'),
            sync: this.steps.includes('sync'),
            keywords: this.steps.includes('keywords'),
            sentiment: this.steps.includes('sentiment')
          }
        }
        
        if (this.mode === 'search') {
          requestBody.keyword = this.keyword
        }
        
        const response = await axios.post('/api/pipeline/run', requestBody)
        
        if (response.data.status === 'success') {
          this.pipelineResult = response.data
          this.$message.success('Pipeline执行成功！')
        } else {
          this.$message.error(response.data.message)
        }
      } catch (error) {
        this.$message.error('Pipeline执行失败: ' + error.message)
      } finally {
        this.running = false
      }
    }
  }
}
</script>

<style scoped>
.result {
  margin-top: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 4px;
}
</style>
```

---

## Axios配置

在Vue项目中配置axios基础URL：

```javascript
// src/api/index.js
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:5000',  // Flask后端地址
  timeout: 60000,  // 60秒超时（pipeline可能需要较长时间）
  headers: {
    'Content-Type': 'application/json'
  }
})

// 响应拦截器
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      console.error('API Error:', error.response.data)
    }
    return Promise.reject(error)
  }
)

export default api
```

然后在组件中使用：
```javascript
import api from '@/api'

// 使用
const response = await api.post('/api/crawler/hot-topics', { limit: 10 })
```
