import request from './request'

// 话题管理相关API
export const topicApi = {
    // 获取话题列表
    getTopics: () => request.get('/api/manage/topics'),

    // 添加话题
    createTopic: (data) => request.post('/api/manage/topics', data),

    // 更新话题
    updateTopic: (id, data) => request.put(`/api/manage/topics/${id}`, data),

    // 删除话题
    deleteTopic: (id) => request.delete(`/api/manage/topics/${id}`)
}

// 爬虫相关API
export const crawlerApi = {
    // 启动爬虫
    start: (data) => request.post('/api/crawler/start', data),

    // 停止爬虫
    stop: () => request.post('/api/crawler/stop'),

    // 获取爬虫状态
    getStatus: () => request.get('/api/crawler/status')
}

// 情感分析相关API
export const sentimentApi = {
    // 执行情感分析
    analyze: (data) => request.post('/api/sentiment/analyze', data),

    // 获取情感分析结果
    getResults: (params) => request.get('/api/sentiment/results', { params })
}

// 关键词分析相关API
export const keywordApi = {
    // 提取关键词
    extract: (data) => request.post('/api/keyword/extract', data),

    // 获取关键词结果
    getResults: (params) => request.get('/api/keyword/results', { params })
}

// 可视化数据相关API
export const visualizationApi = {
    // 获取热度趋势数据
    getTrend: (params) => request.get('/api/visualization/trend', { params }),

    // 获取情感分布数据
    getSentiment: (params) => request.get('/api/visualization/sentiment', { params }),

    // 获取关键词数据
    getKeyword: (params) => request.get('/api/visualization/keyword', { params }),

    // 获取地域分析数据
    getGeographic: (params) => request.get('/api/visualization/geographic', { params })
}

// AI洞察相关API
export const aiApi = {
    // 生成AI分析报告
    generateReport: (data) => request.post('/api/ai/generate-report', data),

    // 异常检测
    detectAnomaly: (data) => request.post('/api/ai/detect-anomaly', data),

    // AI问答
    chat: (data) => request.post('/api/ai/chat', data)
}

// 数据管理相关API
export const dataApi = {
    // 导出数据
    exportData: (params) => request.get('/api/manage/data/export', { params }),

    // 查询历史数据
    queryData: (params) => request.get('/api/manage/data/query', { params })
}
