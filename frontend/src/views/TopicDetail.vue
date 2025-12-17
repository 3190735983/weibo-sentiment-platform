<template>
  <div class="topic-detail">
    <!-- 顶部话题信息 -->
    <div class="topic-header-card">
      <div class="topic-info">
        <div class="topic-title">
          <h1>{{ topic.topic_name }}</h1>
          <el-tag :type="topic.is_active ? 'success' : 'info'" size="large">
            {{ topic.is_active ? '活跃中' : '已暂停' }}
          </el-tag>
        </div>
        <div class="topic-meta">
          <span class="topic-tag">{{ topic.topic_tag }}</span>
          <span class="divider">|</span>
          <span class="created-time">
            <i class="el-icon-time"></i>
            创建于 {{ formatDate(topic.created_at) }}
          </span>
        </div>
      </div>
      <div class="topic-actions">
        <el-button class="gradient-btn" @click="analyzeSentiment">
          <i class="el-icon-data-analysis"></i>
          重新分析
        </el-button>
        <el-button class="export-btn" @click="exportData">
          <i class="el-icon-download"></i>
          导出报告
        </el-button>
      </div>
    </div>

    <!-- 数据可视化区域 -->
    <div class="charts-grid">
      <!-- 情感分布饼图 -->
      <el-card class="chart-card">
        <template #header>
          <div class="chart-header">
            <i class="el-icon-pie-chart"></i>
            <span>情感分布</span>
          </div>
        </template>
        <div class="chart-container" ref="pieChartRef"></div>
        <div class="chart-stats">
          <div class="stat-item positive">
            <div class="stat-label">正面</div>
            <div class="stat-value">{{ sentimentData.positive }}条</div>
            <div class="stat-percent">{{ getPercent('positive') }}%</div>
          </div>
          <div class="stat-item negative">
            <div class="stat-label">负面</div>
            <div class="stat-value">{{ sentimentData.negative }}条</div>
            <div class="stat-percent">{{ getPercent('negative') }}%</div>
          </div>
          <div class="stat-item neutral">
            <div class="stat-label">中性</div>
            <div class="stat-value">{{ sentimentData.neutral }}条</div>
            <div class="stat-percent">{{ getPercent('neutral') }}%</div>
          </div>
        </div>
      </el-card>

      <!-- 情感趋势图 -->
      <el-card class="chart-card trend-card">
        <template #header>
          <div class="chart-header">
            <i class="el-icon-data-line"></i>
            <span>情感趋势</span>
          </div>
        </template>
        <div class="chart-container" ref="trendChartRef"></div>
      </el-card>
    </div>

    <!-- 评论列表 -->
    <el-card class="comments-card">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <i class="el-icon-chat-dot-round"></i>
            <span>评论详情</span>
          </div>
          <el-radio-group v-model="filterType" size="small">
            <el-radio-button label="all">全部</el-radio-button>
            <el-radio-button label="positive">正面</el-radio-button>
            <el-radio-button label="negative">负面</el-radio-button>
            <el-radio-button label="neutral">中性</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      
      <div class="comments-list">
        <div v-for="comment in filteredComments" :key="comment.id" class="comment-item">
          <div class="comment-header">
            <div class="user-info">
              <div class="avatar">{{ comment.user_nickname[0] }}</div>
              <span class="username">{{ comment.user_nickname }}</span>
            </div>
            <el-tag 
              :type="getSentimentTagType(comment.sentiment)" 
              size="small"
              effect="dark"
            >
              {{ comment.sentiment }}
            </el-tag>
          </div>
          <div class="comment-content">{{ comment.comment_text }}</div>
          <div class="comment-meta">
            <span><i class="el-icon-location"></i> {{ comment.location || '未知' }}</span>
            <span><i class="el-icon-time"></i> {{ formatDate(comment.publish_time) }}</span>
            <span><i class="el-icon-star-on"></i> {{ comment.likes_count }}</span>
          </div>
        </div>
      </div>

      <div v-if="filteredComments.length === 0" class="empty-state">
        <i class="el-icon-box"></i>
        <p>暂无评论数据</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { topicAPI, sentimentAPI } from '../api'

const route = useRoute()
const topicId = route.params.id

// 数据
const topic = ref({
  topic_name: '',
  topic_tag: '',
  is_active: true,
  created_at: null
})

const sentimentData = ref({
  positive: 0,
  negative: 0,
  neutral: 0,
  total: 0
})

const comments = ref([])
const filterType = ref('all')

// 图表引用
const pieChartRef = ref(null)
const trendChartRef = ref(null)
let pieChart = null
let trendChart = null

// 计算百分比
const getPercent = (type) => {
  if (sentimentData.value.total === 0) return 0
  const map = {
    positive: sentimentData.value.positive,
    negative: sentimentData.value.negative,
    neutral: sentimentData.value.neutral
  }
  return ((map[type] / sentimentData.value.total) * 100).toFixed(1)
}

// 过滤评论
const filteredComments = computed(() => {
  if (filterType.value === 'all') return comments.value
  
  const typeMap = {
    positive: '正面',
    negative: '负面',
    neutral: '中性'
  }
  
  return comments.value.filter(c => c.sentiment === typeMap[filterType.value])
})

// 获取情感标签类型
const getSentimentTagType = (sentiment) => {
  const map = {
    '正面': 'success',
    '负面': 'danger',
    '中性': 'info'
  }
  return map[sentiment] || 'info'
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return '未知'
  return new Date(date).toLocaleString('zh-CN')
}

// 初始化饼图
const initPieChart = () => {
  if (!pieChartRef.value) return
  
  pieChart = echarts.init(pieChartRef.value)
  
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderColor: 'rgba(0, 212, 255, 0.3)',
      textStyle: {
        color: '#f1f5f9'
      }
    },
    legend: {
      bottom: '5%',
      left: 'center',
      textStyle: {
        color: '#94a3b8'
      }
    },
    series: [
      {
        name: '情感分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#0a0e27',
          borderWidth: 2
        },
        label: {
          show: false
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold',
            color: '#f1f5f9'
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 212, 255, 0.5)'
          }
        },
        data: [
          { 
            value: sentimentData.value.positive, 
            name: '正面',
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#4facfe' },
                { offset: 1, color: '#00f2fe' }
              ])
            }
          },
          { 
            value: sentimentData.value.negative, 
            name: '负面',
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#fa709a' },
                { offset: 1, color: '#fee140' }
              ])
            }
          },
          { 
            value: sentimentData.value.neutral, 
            name: '中性',
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#667eea' },
                { offset: 1, color: '#764ba2' }
              ])
            }
          }
        ]
      }
    ]
  }
  
  pieChart.setOption(option)
}

// 初始化趋势图
const initTrendChart = () => {
  if (!trendChartRef.value) return
  
  trendChart = echarts.init(trendChartRef.value)
  
  // 模拟数据
  const dates = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderColor: 'rgba(0, 212, 255, 0.3)',
      textStyle: {
        color: '#f1f5f9'
      }
    },
    legend: {
      data: ['正面', '负面', '中性'],
      top: '5%',
      textStyle: {
        color: '#94a3b8'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      },
      axisLabel: {
        color: '#94a3b8'
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.05)'
        }
      },
      axisLabel: {
        color: '#94a3b8'
      }
    },
    series: [
      {
        name: '正面',
        type: 'line',
        smooth: true,
        data: [5, 8, 12, 15, 10, 14, 18],
        itemStyle: {
          color: '#4facfe'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(79, 172, 254, 0.3)' },
            { offset: 1, color: 'rgba(79, 172, 254, 0.05)' }
          ])
        }
      },
      {
        name: '负面',
        type: 'line',
        smooth: true,
        data: [3, 5, 4, 6, 8, 5, 7],
        itemStyle: {
          color: '#fa709a'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(250, 112, 154, 0.3)' },
            { offset: 1, color: 'rgba(250, 112, 154, 0.05)' }
          ])
        }
      },
      {
        name: '中性',
        type: 'line',
        smooth: true,
        data: [7, 6, 9, 8, 7, 10, 9],
        itemStyle: {
          color: '#667eea'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
            { offset: 1, color: 'rgba(102, 126, 234, 0.05)' }
          ])
        }
      }
    ]
  }
  
  trendChart.setOption(option)
}

// 加载话题数据
const loadTopicData = async () => {
  try {
    // 获取话题信息
    const topicRes = await topicAPI.getTopics()
    if (topicRes.data.success) {
      const found = topicRes.data.data.find(t => t.id == topicId)
      if (found) {
        topic.value = found
      }
    }
    
    // 获取情感分析结果
    const sentimentRes = await sentimentAPI.getResults(topicId)
    if (sentimentRes.data.success) {
      const data = sentimentRes.data.data
      sentimentData.value = {
        positive: data.distribution['正面'] || 0,
        negative: data.distribution['负面'] || 0,
        neutral: data.distribution['中性'] || 0,
        total: data.total || 0
      }
    }
    
    // 模拟评论数据
    comments.value = generateMockComments()
    
    // 初始化图表
    await nextTick()
    initPieChart()
    initTrendChart()
    
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  }
}

// 生成模拟评论
const generateMockComments = () => {
  const sentiments = ['正面', '负面', '中性']
  const users = ['用户A', '用户B', '用户C', '用户D', '用户E']
  const locations = ['北京', '上海', '广州', '深圳', '']
  const total = sentimentData.value.total
  
  const result = []
  const positive = sentimentData.value.positive
  const negative = sentimentData.value.negative
  const neutral = sentimentData.value.neutral
  
  // 生成正面评论
  for (let i = 0; i < positive; i++) {
    result.push({
      id: `pos-${i}`,
      user_nickname: users[i % users.length],
      comment_text: `这是一条正面评论 ${i + 1}`,
      sentiment: '正面',
      location: locations[i % locations.length],
      publish_time: new Date(Date.now() - i * 3600000).toISOString(),
      likes_count: Math.floor(Math.random() * 100)
    })
  }
  
  // 生成负面评论
  for (let i = 0; i < negative; i++) {
    result.push({
      id: `neg-${i}`,
      user_nickname: users[i % users.length],
      comment_text: `这是一条负面评论 ${i + 1}`,
      sentiment: '负面',
      location: locations[i % locations.length],
      publish_time: new Date(Date.now() - i * 3600000).toISOString(),
      likes_count: Math.floor(Math.random() * 100)
    })
  }
  
  // 生成中性评论
  for (let i = 0; i < neutral; i++) {
    result.push({
      id: `neu-${i}`,
      user_nickname: users[i % users.length],
      comment_text: `这是一条中性评论 ${i + 1}`,
      sentiment: '中性',
      location: locations[i % locations.length],
      publish_time: new Date(Date.now() - i * 3600000).toISOString(),
      likes_count: Math.floor(Math.random() * 100)
    })
  }
  
  return result
}

// 重新分析
const analyzeSentiment = () => {
  ElMessage.info('正在重新分析...')
}

// 导出数据
const exportData = () => {
  ElMessage.info('数据导出功能开发中...')
}

// 窗口大小调整
const handleResize = () => {
  pieChart?.resize()
  trendChart?.resize()
}

onMounted(() => {
  loadTopicData()
  window.addEventListener('resize', handleResize)
})
</script>

<style scoped>
.topic-detail {
  width: 100%;
}

/* 话题头部卡片 */
.topic-header-card {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 30px;
  margin-bottom: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.topic-title {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

.topic-title h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff 0%, #8a2be2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.topic-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: #64748b;
}

.topic-tag {
  color: #00d4ff;
  font-weight: 500;
}

.divider {
  color: rgba(255, 255, 255, 0.1);
}

.topic-actions {
  display: flex;
  gap: 12px;
}

.gradient-btn {
  background: linear-gradient(135deg, #00d4ff 0%, #8a2be2 100%);
  border: none;
  color: white;
  font-weight: 600;
}

.export-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #e0e0e0;
}

.export-btn:hover {
  background: rgba(138, 43, 226, 0.2);
  border-color: #8a2be2;
  color: #8a2be2;
}

/* 图表网格 */
.charts-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 24px;
  margin-bottom: 30px;
}

.chart-card {
  min-height: 400px;
}

.chart-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
  font-weight: 600;
  color: #f1f5f9;
}

.chart-header i {
  font-size: 18px;
  color: #00d4ff;
}

.chart-container {
  width: 100%;
  height: 280px;
}

/* 统计数据 */
.chart-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-top: 20px;
}

.stat-item {
  background: rgba(30, 41, 59, 0.4);
  border-radius: 12px;
  padding: 16px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.stat-item.positive {
  border-left: 3px solid #4facfe;
}

.stat-item.negative {
  border-left: 3px solid #fa709a;
}

.stat-item.neutral {
  border-left: 3px solid #667eea;
}

.stat-label {
  font-size: 13px;
  color: #94a3b8;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #f1f5f9;
  margin-bottom: 4px;
}

.stat-percent {
  font-size: 14px;
  color: #64748b;
}

/* 评论列表 */
.comments-card {
  min-height: 400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
  font-weight: 600;
  color: #f1f5f9;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-item {
  background: rgba(30, 41, 59, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s;
}

.comment-item:hover {
  background: rgba(30, 41, 59, 0.6);
  border-color: rgba(0, 212, 255, 0.2);
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #00d4ff 0%, #8a2be2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
}

.username {
  color: #f1f5f9;
  font-weight: 500;
}

.comment-content {
  color: #e0e0e0;
  line-height: 1.6;
  margin-bottom: 12px;
}

.comment-meta {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: #64748b;
}

.comment-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  color: #64748b;
}

.empty-state i {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.4;
}

/* 响应式 */
@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
