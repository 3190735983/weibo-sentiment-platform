<template>
  <div class="data-visualization">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>数据可视化</span>
          <el-button size="small" @click="refreshTopics">
            <i class="el-icon-refresh"></i> 刷新
          </el-button>
        </div>
      </template>

      <!-- 话题选择器 -->
      <el-form label-width="100px">
        <el-form-item label="选择话题">
          <el-select 
            v-model="selectedTopicId" 
            placeholder="请选择要分析的话题"
            style="width: 400px;"
            @change="handleTopicChange"
            filterable
          >
            <el-option
              v-for="topic in topics"
              :key="topic.id"
              :label="topic.name"
              :value="topic.id"
            >
              <span style="float: left">{{ topic.name }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">
                {{ topic.post_count }} 条微博
              </span>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 可视化内容 -->
    <div v-if="selectedTopicId" class="visualization-content">
      <!-- 关键词云图 -->
      <el-card class="box-card" style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span>
              <i class="el-icon-connection"></i> 关键词云图
            </span>
            <el-tag v-if="keywords.length > 0">{{ keywords.length }} 个关键词</el-tag>
          </div>
        </template>

        <div v-loading="loadingKeywords">
          <KeywordCloud 
            v-if="keywords && keywords.length > 0"
            :data="keywords" 
            height="500px"
          />
          <el-empty 
            v-else-if="!loadingKeywords"
            description="暂无关键词数据" 
          />
        </div>
      </el-card>

      <!-- 情感分布图 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <el-card class="box-card">
            <template #header>
              <div class="card-header">
                <span>
                  <i class="el-icon-pie-chart"></i> 情感分布 - 饼图
                </span>
                <el-tag v-if="sentiments">
                  总计 {{ totalSentiments }} 条
                </el-tag>
              </div>
            </template>

            <div v-loading="loadingSentiments">
              <SentimentChart 
                v-if="sentiments"
                :data="sentiments" 
                chart-type="pie"
                height="400px"
              />
              <el-empty 
                v-else-if="!loadingSentiments"
                description="暂无情感数据" 
              />
            </div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card class="box-card">
            <template #header>
              <div class="card-header">
                <span>
                  <i class="el-icon-s-data"></i> 情感分布 - 柱状图
                </span>
              </div>
            </template>

            <div v-loading="loadingSentiments">
              <SentimentChart 
                v-if="sentiments"
                :data="sentiments" 
                chart-type="bar"
                height="400px"
              />
              <el-empty 
                v-else-if="!loadingSentiments"
                description="暂无情感数据" 
              />
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 详细统计 -->
      <el-card class="box-card" style="margin-top: 20px;">
        <template #header>
          <span>
            <i class="el-icon-data-analysis"></i> 详细统计
          </span>
        </template>

        <el-descriptions :column="3" border>
          <el-descriptions-item label="话题名称">
            {{ currentTopic?.name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="微博数量">
            <el-tag type="primary">{{ currentTopic?.post_count || 0 }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="关键词数量">
            <el-tag type="success">{{ keywords.length }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="正面情感">
            <el-tag type="success">
              {{ sentiments?.positive || 0 }} 
              ({{ getSentimentPercentage('positive') }}%)
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="负面情感">
            <el-tag type="danger">
              {{ sentiments?.negative || 0 }}
              ({{ getSentimentPercentage('negative') }}%)
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="中性情感">
            <el-tag type="info">
              {{ sentiments?.neutral || 0 }}
              ({{ getSentimentPercentage('neutral') }}%)
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>

    <!-- 空状态 -->
    <el-empty 
      v-else
      description="请选择一个话题查看可视化数据"
      style="margin-top: 50px;"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import KeywordCloud from '@/components/charts/KeywordCloud.vue'
import SentimentChart from '@/components/charts/SentimentChart.vue'
import api from '@/api/crawler'

// 数据
const topics = ref([])
const selectedTopicId = ref(null)
const keywords = ref([])
const sentiments = ref(null)

// 加载状态
const loadingTopics = ref(false)
const loadingKeywords = ref(false)
const loadingSentiments = ref(false)

// 当前选中的话题
const currentTopic = computed(() => {
  return topics.value.find(t => t.id === selectedTopicId.value)
})

// 情感总数
const totalSentiments = computed(() => {
  if (!sentiments.value) return 0
  return (sentiments.value.positive || 0) + 
         (sentiments.value.negative || 0) + 
         (sentiments.value.neutral || 0)
})

// 获取情感百分比
const getSentimentPercentage = (type) => {
  if (!sentiments.value || totalSentiments.value === 0) return 0
  const value = sentiments.value[type] || 0
  return ((value / totalSentiments.value) * 100).toFixed(1)
}

// 获取话题列表
const fetchTopics = async () => {
  loadingTopics.value = true
  try {
    const response = await api.visualization.getTopics()
    topics.value = response.topics || []
    
    // 如果有话题,默认选中第一个
    if (topics.value.length > 0 && !selectedTopicId.value) {
      selectedTopicId.value = topics.value[0].id
      await handleTopicChange()
    }
  } catch (error) {
    ElMessage.error('获取话题列表失败: ' + error.message)
  } finally {
    loadingTopics.value = false
  }
}

// 获取关键词数据
const fetchKeywords = async (topicId) => {
  loadingKeywords.value = true
  try {
    const response = await api.visualization.getKeywords(topicId)
    // 转换数据格式为 [{ name, value }]
    keywords.value = response.keywords || []
  } catch (error) {
    ElMessage.error('获取关键词失败: ' + error.message)
    keywords.value = []
  } finally {
    loadingKeywords.value = false
  }
}

// 获取情感数据
const fetchSentiments = async (topicId) => {
  loadingSentiments.value = true
  try {
    const response = await api.visualization.getSentiments(topicId)
    sentiments.value = response.sentiments || { positive: 0, negative: 0, neutral: 0 }
  } catch (error) {
    ElMessage.error('获取情感数据失败: ' + error.message)
    sentiments.value = null
  } finally {
    loadingSentiments.value = false
  }
}

// 话题改变处理
const handleTopicChange = async () => {
  if (!selectedTopicId.value) return
  
  // 并行加载关键词和情感数据
  await Promise.all([
    fetchKeywords(selectedTopicId.value),
    fetchSentiments(selectedTopicId.value)
  ])
}

// 刷新话题列表
const refreshTopics = () => {
  fetchTopics()
}

onMounted(() => {
  fetchTopics()
})
</script>

<style scoped>
.data-visualization {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.box-card {
  width: 100%;
}

.visualization-content {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

:deep(.el-select-dropdown__item) {
  height: auto;
  padding: 10px 20px;
}
</style>
