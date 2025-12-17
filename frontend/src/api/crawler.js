/**
 * 爬虫API服务
 */
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:5000',
  timeout: 300000,  // 5分钟超时，适应Pipeline长时间处理
  headers: {
    'Content-Type': 'application/json'
  }
})

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default {
  // 爬虫API
  crawler: {
    crawlHotTopics(limit = 10, filterSensitive = true) {
      return api.post('/api/crawler/hot-topics', {
        limit,
        filter_sensitive: filterSensitive
      })
    },

    searchTopic(keyword) {
      return api.post('/api/crawler/search', { keyword })
    },

    syncData() {
      return api.post('/api/crawler/sync')
    },

    getStatus() {
      return api.get('/api/crawler/status')
    }
  },

  // Pipeline API
  pipeline: {
    run(config) {
      return api.post('/api/pipeline/run', config)
    },

    process(topicId) {
      return api.post(`/api/pipeline/process/${topicId}`)
    },

    getStatus() {
      return api.get('/api/pipeline/status')
    }
  },

  // 数据可视化 API
  visualization: {
    getTopics() {
      return api.get('/api/visualization/topics')
    },

    getKeywords(topicId) {
      return api.get(`/api/visualization/topics/${topicId}/keywords`)
    },

    getSentiments(topicId) {
      return api.get(`/api/visualization/topics/${topicId}/sentiments`)
    }
  }
}
