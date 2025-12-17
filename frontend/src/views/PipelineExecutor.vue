<template>
  <div class="pipeline-executor">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>数据处理Pipeline</span>
          <el-tag :type="statusType">{{ statusText }}</el-tag>
        </div>
      </template>

      <!-- 模式选择 -->
      <el-form :model="form" label-width="100px">
        <el-form-item label="执行模式">
          <el-radio-group v-model="form.mode">
            <el-radio-button value="hot_topics">热点爬取</el-radio-button>
            <el-radio-button value="search">关键词搜索</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <!-- 热点模式参数 -->
        <el-form-item v-if="form.mode === 'hot_topics'" label="爬取数量">
          <el-input-number v-model="form.limit" :min="1" :max="20" />
          <span style="margin-left: 10px; color: #909399; font-size: 13px;">
            爬取前N个热点话题
          </span>
        </el-form-item>

        <!-- 搜索模式参数 -->
        <el-form-item v-if="form.mode === 'search'" label="搜索关键词">
          <el-input 
            v-model="form.keyword" 
            placeholder="输入要搜索的话题关键词"
            style="width: 300px;"
          />
        </el-form-item>

        <el-divider />

        <!-- 步骤配置 -->
        <el-form-item label="执行步骤">
          <el-checkbox-group v-model="selectedSteps">
            <el-checkbox label="crawl" border>
              <i class="el-icon-download"></i> 爬取数据
            </el-checkbox>
            <el-checkbox label="sync" border>
              <i class="el-icon-refresh"></i> 同步数据
            </el-checkbox>
            <el-checkbox label="keywords" border>
              <i class="el-icon-connection"></i> 提取关键词
            </el-checkbox>
            <el-checkbox label="sentiment" border>
              <i class="el-icon-data-analysis"></i> 情感分析
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item>
          <el-button 
            type="primary" 
            @click="runPipeline" 
            :loading="loading"
            size="large"
          >
            <i class="el-icon-video-play"></i>
            运行Pipeline
          </el-button>
          <el-button @click="resetForm" size="large">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 执行进度 -->
    <el-card v-if="executing" class="box-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>执行进度</span>
          <el-tag type="warning">运行中...</el-tag>
        </div>
      </template>
      <el-progress 
        :percentage="progress" 
        :status="progress === 100 ? 'success' : undefined"
        :stroke-width="20"
      />
      <p style="margin-top: 10px; color: #909399;">{{ progressText }}</p>
    </el-card>

    <!-- 执行结果 -->
    <el-card v-if="result" class="box-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>执行结果</span>
          <el-tag :type="result.status === 'success' ? 'success' : 'danger'">
            {{ result.status === 'success' ? '成功' : '失败' }}
          </el-tag>
        </div>
      </template>

      <el-alert
        :title="result.message"
        :type="result.status === 'success' ? 'success' : 'error'"
        :closable="false"
        style="margin-bottom: 20px;"
      />

      <el-descriptions v-if="result.results" title="详细统计" :column="2" border>
        <el-descriptions-item 
          v-if="result.results.topics_added !== undefined"
          label="新增话题"
        >
          <el-tag type="success">{{ result.results.topics_added }}</el-tag>
        </el-descriptions-item>

        <el-descriptions-item 
          v-if="result.results.posts_synced !== undefined"
          label="同步微博"
        >
          <el-tag type="primary">{{ result.results.posts_synced }}</el-tag>
        </el-descriptions-item>

        <el-descriptions-item 
          v-if="result.results.keywords_extracted !== undefined"
          label="提取关键词"
        >
          <el-tag type="info">{{ result.results.keywords_extracted }}</el-tag>
        </el-descriptions-item>

        <el-descriptions-item 
          v-if="result.results.sentiments_analyzed !== undefined"
          label="情感分析"
        >
          <el-tag type="warning">{{ result.results.sentiments_analyzed }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 错误信息 -->
      <div v-if="result.results && result.results.errors && result.results.errors.length > 0" style="margin-top: 20px;">
        <h4 style="color: #F56C6C;">错误信息</h4>
        <el-alert
          v-for="(error, index) in result.results.errors"
          :key="index"
          :title="error"
          type="error"
          :closable="false"
          style="margin-top: 10px;"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api/crawler'

const loading = ref(false)
const executing = ref(false)
const progress = ref(0)
const progressText = ref('')

// 表单数据
const form = ref({
  mode: 'hot_topics',
  limit: 10,
  keyword: ''
})

// 选中的步骤
const selectedSteps = ref(['crawl', 'sync', 'keywords', 'sentiment'])

// 执行结果
const result = ref(null)

// 状态计算
const statusType = computed(() => {
  if (executing.value) return 'warning'
  if (result.value?.status === 'success') return 'success'
  if (result.value?.status === 'error') return 'danger'
  return 'info'
})

const statusText = computed(() => {
  if (executing.value) return '执行中'
  if (result.value?.status === 'success') return '已完成'
  if (result.value?.status === 'error') return '执行失败'
  return '就绪'
})

// 监听模式切换,清空结果
watch(() => form.value.mode, () => {
  result.value = null
})

// 运行Pipeline
const runPipeline = async () => {
  // 验证
  if (form.value.mode === 'search' && !form.value.keyword) {
    ElMessage.warning('请输入搜索关键词')
    return
  }

  if (selectedSteps.value.length === 0) {
    ElMessage.warning('请至少选择一个执行步骤')
    return
  }

  loading.value = true
  executing.value = true
  progress.value = 0
  result.value = null

  try {
    // 构建步骤配置
    const steps = {
      crawl: selectedSteps.value.includes('crawl'),
      sync: selectedSteps.value.includes('sync'),
      keywords: selectedSteps.value.includes('keywords'),
      sentiment: selectedSteps.value.includes('sentiment')
    }

    // 模拟进度
    const progressInterval = setInterval(() => {
      if (progress.value < 90) {
        progress.value += 10
        updateProgressText()
      }
    }, 500)

    // 调用API
    const response = await api.pipeline.run({
      mode: form.value.mode,
      keyword: form.value.keyword || undefined,
      limit: form.value.limit,
      steps
    })

    clearInterval(progressInterval)
    progress.value = 100
    progressText.value = '执行完成!'

    result.value = response

    if (response.status === 'success') {
      ElMessage.success('Pipeline执行成功!')
    } else {
      ElMessage.error(response.message || 'Pipeline执行失败')
    }

  } catch (error) {
    progress.value = 0
    executing.value = false
    ElMessage.error('执行失败: ' + error.message)
    result.value = {
      status: 'error',
      message: error.message
    }
  } finally {
    loading.value = false
    setTimeout(() => {
      executing.value = false
    }, 1000)
  }
}

// 更新进度文本
const updateProgressText = () => {
  const step = Math.floor(progress.value / 25)
  const texts = [
    '准备爬取数据...',
    '正在同步数据...',
    '提取关键词中...',
    '进行情感分析...',
    '处理完成!'
  ]
  progressText.value = texts[step] || texts[0]
}

// 重置表单
const resetForm = () => {
  form.value = {
    mode: 'hot_topics',
    limit: 10,
    keyword: ''
  }
  selectedSteps.value = ['crawl', 'sync', 'keywords', 'sentiment']
  result.value = null
  executing.value = false
  progress.value = 0
}
</script>

<style scoped>
.pipeline-executor {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.box-card {
  width: 100%;
  margin-bottom: 20px;
}

.el-checkbox-group .el-checkbox {
  margin-right: 15px;
  margin-bottom: 10px;
}

.el-checkbox.is-bordered {
  padding: 10px 20px;
  border-radius: 8px;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
}
</style>
