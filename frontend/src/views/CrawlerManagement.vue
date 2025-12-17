<template>
  <div class="crawler-management">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>爬虫管理</span>
          <el-tag :type="statusType">{{ statusText }}</el-tag>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <!-- 热点爬取 -->
        <el-tab-pane label="热点爬取" name="hot">
          <el-form :model="hotForm" label-width="100px">
            <el-form-item label="爬取数量">
              <el-input-number v-model="hotForm.limit" :min="1" :max="20" />
            </el-form-item>
            <el-form-item label="过滤敏感">
              <el-switch v-model="hotForm.filterSensitive" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="crawlHotTopics" :loading="loading">
                开始爬取
              </el-button>
            </el-form-item>
          </el-form>

          <el-divider />

          <div v-if="hotResult">
            <h4>爬取结果</h4>
            <p>新增话题: {{ hotResult.topics_added }}</p>
            <p>过滤话题: {{ hotResult.topics_filtered }}</p>
            <el-table :data="hotResult.topics" style="width: 100%">
              <el-table-column prop="name" label="话题名称" />
              <el-table-column prop="tag" label="话题标签" />
              <el-table-column label="状态">
                <template #default="scope">
                  <el-tag :type="scope.row.is_new ? 'success' : 'info'">
                    {{ scope.row.is_new ? '新增' : '已存在' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 关键词搜索 -->
        <el-tab-pane label="关键词搜索" name="search">
          <el-form :model="searchForm" label-width="100px">
            <el-form-item label="关键词">
              <el-input v-model="searchForm.keyword" placeholder="输入话题关键词" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="searchTopic" :loading="loading">
                搜索话题
              </el-button>
            </el-form-item>
          </el-form>

          <div v-if="searchResult">
            <el-alert
              :title="searchResult.message"
              :type="searchResult.status === 'success' ? 'success' : 'error'"
              :closable="false"
            />
          </div>
        </el-tab-pane>

        <!-- 数据同步 -->
        <el-tab-pane label="数据同步" name="sync">
          <el-button type="warning" @click="syncData" :loading="loading">
            同步MediaCrawler数据
          </el-button>

          <div v-if="syncResult" style="margin-top: 20px">
            <el-descriptions title="同步结果" :column="2" border>
              <el-descriptions-item label="状态">
                <el-tag :type="syncResult.status === 'success' ? 'success' : 'error'">
                  {{ syncResult.status }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="消息">{{ syncResult.message }}</el-descriptions-item>
              <el-descriptions-item label="新增">{{ syncResult.posts_added }}</el-descriptions-item>
              <el-descriptions-item label="跳过">{{ syncResult.posts_skipped }}</el-descriptions-item>
            </el-descriptions>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 爬虫状态 -->
    <el-card class="box-card" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>爬虫状态</span>
          <el-button size="small" @click="refreshStatus">刷新</el-button>
        </div>
      </template>

      <el-descriptions v-if="crawlerStatus" :column="3" border>
        <el-descriptions-item label="运行状态">
          <el-tag :type="crawlerStatus.is_running ? 'warning' : 'success'">
            {{ crawlerStatus.is_running ? '运行中' : '就绪' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="话题数">{{ crawlerStatus.topics_count }}</el-descriptions-item>
        <el-descriptions-item label="微博数">{{ crawlerStatus.posts_count }}</el-descriptions-item>
        <el-descriptions-item label="MediaCrawler数据库">
          <el-tag :type="crawlerStatus.mediacrawler_db_exists ? 'success' : 'info'">
            {{ crawlerStatus.mediacrawler_db_exists ? '存在' : '不存在' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api/crawler'

const activeTab = ref('hot')
const loading = ref(false)

// 热点爬取
const hotForm = ref({
  limit: 10,
  filterSensitive: true
})
const hotResult = ref(null)

// 关键词搜索
const searchForm = ref({
  keyword: ''
})
const searchResult = ref(null)

// 数据同步
const syncResult = ref(null)

// 爬虫状态
const crawlerStatus = ref(null)

const statusType = computed(() => {
  if (!crawlerStatus.value) return 'info'
  return crawlerStatus.value.is_running ? 'warning' : 'success'
})

const statusText = computed(() => {
  if (!crawlerStatus.value) return '未知'
  return crawlerStatus.value.is_running ? '运行中' : '就绪'
})

// 爬取热点话题
const crawlHotTopics = async () => {
  loading.value = true
  try {
    const result = await api.crawler.crawlHotTopics(
      hotForm.value.limit,
      hotForm.value.filterSensitive
    )
    
    if (result.status === 'success') {
      hotResult.value = result
      ElMessage.success(result.message)
      await refreshStatus()
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('爬取失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 搜索话题
const searchTopic = async () => {
  if (!searchForm.value.keyword) {
    ElMessage.warning('请输入关键词')
    return
  }
  
  loading.value = true
  try {
    const result = await api.crawler.searchTopic(searchForm.value.keyword)
    searchResult.value = result
    
    if (result.status === 'success') {
      ElMessage.success(result.message)
      await refreshStatus()
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('搜索失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 同步数据
const syncData = async () => {
  loading.value = true
  try {
    const result = await api.crawler.syncData()
    syncResult.value = result
    
    if (result.status === 'success') {
      ElMessage.success(result.message)
      await refreshStatus()
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('同步失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 刷新状态
const refreshStatus = async () => {
  try {
    crawlerStatus.value = await api.crawler.getStatus()
  } catch (error) {
    console.error('获取状态失败:', error)
  }
}

onMounted(() => {
  refreshStatus()
})
</script>

<style scoped>
.crawler-management {
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
</style>
