<template>
  <div class="dashboard">
    <!-- 顶部统计卡片区 -->
    <div class="stats-grid">
      <div class="stat-card" v-for="(stat, index) in stats" :key="index">
        <div class="stat-icon" :style="{ background: stat.gradient }">
          <i :class="stat.icon"></i>
        </div>
        <div class="stat-content">
          <div class="stat-label">{{ stat.label }}</div>
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-trend" :class="stat.trendClass">
            <i :class="stat.trendIcon"></i>
            <span>{{ stat.trend }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 话题列表和快速操作 -->
    <div class="content-grid">
      <!-- 话题管理卡片 -->
      <el-card class="topic-card">
        <template #header>
          <div class="card-header">
            <div class="header-title">
              <i class="el-icon-s-order"></i>
              <span>话题管理</span>
            </div>
            <el-button type="primary" class="gradient-btn" @click="showAddDialog">
              <i class="el-icon-plus"></i>
              添加话题
            </el-button>
          </div>
        </template>

        <div class="topics-container">
          <div v-if="loading" class="loading-state">
            <i class="el-icon-loading"></i>
            <p>加载中...</p>
          </div>
          
          <div v-else-if="topics.length === 0" class="empty-state">
            <i class="el-icon-box"></i>
            <p>暂无话题，点击上方按钮添加</p>
          </div>

          <div v-else class="topic-list">
            <div v-for="topic in topics" :key="topic.id" class="topic-item">
              <div class="topic-info">
                <div class="topic-header">
                  <h4>{{ topic.topic_name }}</h4>
                  <el-tag :type="topic.is_active ? 'success' : 'info'" size="small">
                    {{ topic.is_active ? '活跃' : '暂停' }}
                  </el-tag>
                </div>
                <div class="topic-tag">{{ topic.topic_tag }}</div>
              </div>
              
              <div class="topic-actions">
                <el-button 
                  size="small" 
                  class="action-btn-small analyze-btn"
                  @click="analyzeTopic(topic)"
                >
                  <i class="el-icon-data-analysis"></i>
                  分析
                </el-button>
                <el-button 
                  size="small" 
                  class="action-btn-small view-btn"
                  @click="viewTopic(topic)"
                >
                  <i class="el-icon-view"></i>
                  查看
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 快速操作卡片 -->
      <el-card class="quick-actions-card">
        <template #header>
          <div class="card-header">
            <div class="header-title">
              <i class="el-icon-lightning"></i>
              <span>快速操作</span>
            </div>
          </div>
        </template>

        <div class="quick-actions">
          <div class="action-item" @click="discoverHotTopics">
            <div class="action-icon hot-icon">
              <i class="el-icon-star-on"></i>
            </div>
            <div class="action-text">
              <h4>发现热点</h4>
              <p>获取微博热搜话题</p>
            </div>
          </div>

          <div class="action-item" @click="analyzeAll">
            <div class="action-icon analyze-icon">
              <i class="el-icon-data-board"></i>
            </div>
            <div class="action-text">
              <h4>批量分析</h4>
              <p>分析所有话题情感</p>
            </div>
          </div>

          <div class="action-item" @click="exportData">
            <div class="action-icon export-icon">
              <i class="el-icon-download"></i>
            </div>
            <div class="action-text">
              <h4>导出数据</h4>
              <p>导出分析结果</p>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 添加话题对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="添加话题"
      width="500px"
      class="tech-dialog"
    >
      <el-form :model="form" label-width="100px">
        <el-form-item label="话题名称">
          <el-input v-model="form.topic_name" placeholder="请输入话题名称" />
        </el-form-item>
        <el-form-item label="话题标签">
          <el-input v-model="form.topic_tag" placeholder="#话题标签#" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" class="gradient-btn" @click="addTopic">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import { useRouter } from 'vue-router'
import { topicAPI, sentimentAPI } from '../api'

const router = useRouter()

// 数据
const topics = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const form = ref({
  topic_name: '',
  topic_tag: ''
})

// 统计数据
const stats = ref([
  {
    label: '总话题数',
    value: '0',
    trend: '+12% 本周',
    trendClass: 'trend-up',
    trendIcon: 'el-icon-top',
    icon: 'el-icon-s-order',
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  },
  {
    label: '已分析',
    value: '0',
    trend: '+8% 本周',
    trendClass: 'trend-up',
    trendIcon: 'el-icon-top',
    icon: 'el-icon-data-analysis',
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
  },
  {
    label: '正面情感',
    value: '0%',
    trend: '+5% 本周',
    trendClass: 'trend-up',
    trendIcon: 'el-icon-top',
    icon: 'el-icon-sunny',
    gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
  },
  {
    label: '负面情感',
    value: '0%',
    trend: '-3% 本周',
    trendClass: 'trend-down',
    trendIcon: 'el-icon-bottom',
    icon: 'el-icon-cloudy',
    gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
  }
])

// 加载话题列表
const loadTopics = async () => {
  loading.value = true
  try {
    const response = await topicAPI.getTopics()
    if (response.data.success) {
      topics.value = response.data.data
      updateStats()
    }
  } catch (error) {
    ElMessage.error('加载话题失败')
  } finally {
    loading.value = false
  }
}

// 更新统计数据
const updateStats = () => {
  stats.value[0].value = topics.value.length.toString()
  // TODO: 从API获取实际统计数据
}

// 显示添加对话框
const showAddDialog = () => {
  form.value = {
    topic_name: '',
    topic_tag: ''
  }
  dialogVisible.value = true
}

// 添加话题
const addTopic = async () => {
  if (!form.value.topic_name) {
    ElMessage.warning('请输入话题名称')
    return
  }
  
  try {
    const response = await topicAPI.addTopic(form.value)
    if (response.data.success) {
      ElNotification({
        title: '成功',
        message: '话题添加成功',
        type: 'success',
        duration: 2000
      })
      dialogVisible.value = false
      loadTopics()
    }
  } catch (error) {
    ElMessage.error('添加话题失败')
  }
}

// 分析话题
const analyzeTopic = async (topic) => {
  const loading = ElMessage({
    message: '正在分析情感...',
    type: 'info',
    duration: 0
  })
  
  try {
    const response = await sentimentAPI.analyze({ topic_id: topic.id })
    loading.close()
    
    if (response.data.success) {
      ElNotification({
        title: '分析完成',
        message: `成功分析了 ${response.data.data.analyzed_count} 条评论`,
        type: 'success'
      })
    }
  } catch (error) {
    loading.close()
    ElMessage.error('分析失败')
  }
}

// 查看话题详情
const viewTopic = (topic) => {
  router.push(`/topic/${topic.id}`)
}

// 发现热点话题
const discoverHotTopics = () => {
  ElMessage.info('热点话题功能开发中...')
}

// 批量分析
const analyzeAll = () => {
  ElMessage.info('批量分析功能开发中...')
}

// 导出数据
const exportData = () => {
  ElMessage.info('数据导出功能开发中...')
}

onMounted(() => {
  loadTopics()
})
</script>

<style scoped>
.dashboard {
  width: 100%;
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 30px;
}

.stat-card {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  gap: 20px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(138, 43, 226, 0.05) 100%);
  opacity: 0;
  transition: opacity 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  border-color: rgba(0, 212, 255, 0.3);
  box-shadow: 0 12px 40px rgba(0, 212, 255, 0.2);
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
  position: relative;
  z-index: 1;
}

.stat-label {
  font-size: 13px;
  color: #94a3b8;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #f1f5f9;
  margin-bottom: 8px;
  line-height: 1;
}

.stat-trend {
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.trend-up {
  color: #10b981;
}

.trend-down {
  color: #ef4444;
}

/* 内容网格 */
.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

/* 卡片头部 */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 600;
  color: #f1f5f9;
}

.header-title i {
  font-size: 20px;
  color: #00d4ff;
}

/* 渐变按钮 */
.gradient-btn {
  background: linear-gradient(135deg, #00d4ff 0%, #8a2be2 100%);
  border: none;
  color: white;
  font-weight: 600;
}

.gradient-btn:hover {
  opacity: 0.9;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 212, 255, 0.4);
}

/* 话题列表 */
.topics-container {
  min-height: 400px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: #64748b;
}

.loading-state i,
.empty-state i {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.4;
}

.topic-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.topic-item {
  background: rgba(30, 41, 59, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s;
}

.topic-item:hover {
  background: rgba(30, 41, 59, 0.6);
  border-color: rgba(0, 212, 255, 0.2);
  transform: translateX(4px);
}

.topic-info {
  flex: 1;
}

.topic-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.topic-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #f1f5f9;
}

.topic-tag {
  font-size: 13px;
  color: #64748b;
}

.topic-actions {
  display: flex;
  gap: 8px;
}

.action-btn-small {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #e0e0e0;
  transition: all 0.3s;
}

.analyze-btn:hover {
  background: rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
  color: #00d4ff;
}

.view-btn:hover {
  background: rgba(138, 43, 226, 0.2);
  border-color: #8a2be2;
  color: #8a2be2;
}

/* 快速操作 */
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(30, 41, 59, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.action-item:hover {
  background: rgba(30, 41, 59, 0.6);
  border-color: rgba(0, 212, 255, 0.2);
  transform: translateY(-2px);
}

.action-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.hot-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.analyze-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.export-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.action-text h4 {
  margin: 0 0 4px 0;
  font-size: 15px;
  font-weight: 600;
  color: #f1f5f9;
}

.action-text p {
  margin: 0;
  font-size: 13px;
  color: #64748b;
}

/* 对话框样式 */
:deep(.tech-dialog .el-dialog) {
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(0, 212, 255, 0.2);
}

:deep(.tech-dialog .el-dialog__title) {
  color: #f1f5f9;
  font-size: 18px;
  font-weight: 600;
}

:deep(.el-input__inner) {
  background: rgba(30, 41, 59, 0.6);
  border-color: rgba(255, 255, 255, 0.1);
  color: #f1f5f9;
}

:deep(.el-input__inner:focus) {
  border-color: #00d4ff;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
