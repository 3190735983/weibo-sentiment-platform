<template>
  <div class="data-manage">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>数据管理</h1>
      <p class="subtitle">Data Management Center</p>
    </div>

    <!-- 数据统计概览 -->
    <div class="stats-overview">
      <div class="stat-card" v-for="stat in dataStats" :key="stat.label">
        <div class="stat-icon" :style="{ background: stat.gradient }">
          <i :class="stat.icon"></i>
        </div>
        <div class="stat-info">
          <div class="stat-label">{{ stat.label }}</div>
          <div class="stat-value">{{ stat.value }}</div>
        </div>
      </div>
    </div>

    <!-- 数据导出卡片 -->
    <el-card class="export-card">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <i class="el-icon-download"></i>
            <span>数据导出</span>
          </div>
        </div>
      </template>

      <div class="export-options">
        <div class="export-item" @click="exportData('csv')">
          <div class="export-icon csv-icon">
            <i class="el-icon-document"></i>
          </div>
          <div class="export-content">
            <h4>CSV 格式</h4>
            <p>导出为逗号分隔值文件</p>
          </div>
          <el-button type="primary" circle>
            <i class="el-icon-right"></i>
          </el-button>
        </div>

        <div class="export-item" @click="exportData('excel')">
          <div class="export-icon excel-icon">
            <i class="el-icon-files"></i>
          </div>
          <div class="export-content">
            <h4>Excel 格式</h4>
            <p>导出为Excel电子表格</p>
          </div>
          <el-button type="primary" circle>
            <i class="el-icon-right"></i>
          </el-button>
        </div>

        <div class="export-item" @click="exportData('json')">
          <div class="export-icon json-icon">
            <i class="el-icon-document-copy"></i>
          </div>
          <div class="export-content">
            <h4>JSON 格式</h4>
            <p>导出为JSON数据文件</p>
          </div>
          <el-button type="primary" circle>
            <i class="el-icon-right"></i>
          </el-button>
        </div>

        <div class="export-item" @click="exportData('pdf')">
          <div class="export-icon pdf-icon">
            <i class="el-icon-tickets"></i>
          </div>
          <div class="export-content">
            <h4>PDF 报告</h4>
            <p>生成完整分析报告</p>
          </div>
          <el-button type="primary" circle>
            <i class="el-icon-right"></i>
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 数据筛选和查询 -->
    <el-card class="filter-card">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <i class="el-icon-search"></i>
            <span>高级筛选</span>
          </div>
        </div>
      </template>

      <el-form :model="filterForm" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="话题">
              <el-select v-model="filterForm.topic" placeholder="选择话题" style="width: 100%">
                <el-option label="全部话题" value="all"></el-option>
                <el-option label="人工智能" value="ai"></el-option>
                <el-option label="ChatGPT" value="gpt"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="情感类型">
              <el-select v-model="filterForm.sentiment" placeholder="选择情感" style="width: 100%">
                <el-option label="全部" value="all"></el-option>
                <el-option label="正面" value="positive"></el-option>
                <el-option label="负面" value="negative"></el-option>
                <el-option label="中性" value="neutral"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="时间范围">
              <el-date-picker
                v-model="filterForm.dateRange"
                type="daterange"
                range-separator="-"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24" style="text-align: right;">
            <el-button @click="resetFilter">重置</el-button>
            <el-button type="primary" class="gradient-btn" @click="applyFilter">
              <i class="el-icon-search"></i>
              查询
            </el-button>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 数据预览表格 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <i class="el-icon-data-board"></i>
            <span>数据预览</span>
          </div>
          <div class="header-actions">
            <el-button size="small" @click="refreshData">
              <i class="el-icon-refresh"></i>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="tableData" style="width: 100%" stripe>
        <el-table-column prop="id" label="ID" width="80"></el-table-column>
        <el-table-column prop="topic" label="话题" width="150"></el-table-column>
        <el-table-column prop="content" label="内容" min-width="300"></el-table-column>
        <el-table-column prop="sentiment" label="情感" width="100">
          <template #default="scope">
            <el-tag :type="getSentimentType(scope.row.sentiment)" size="small">
              {{ scope.row.sentiment }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="time" label="时间" width="180"></el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="scope">
            <el-button type="text" size="small" @click="viewDetail(scope.row)">
              查看
            </el-button>
            <el-button type="text" size="small" @click="deleteRow(scope.row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next, jumper"
          :total="100"
          :page-sizes="[10, 20, 50, 100]"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

// 数据统计
const dataStats = ref([
  {
    label: '总数据量',
    value: '1,234',
    icon: 'el-icon-files',
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  },
  {
    label: '今日新增',
    value: '156',
    icon: 'el-icon-plus',
    gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
  },
  {
    label: '已导出',
    value: '89',
    icon: 'el-icon-download',
    gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
  },
  {
    label: '存储空间',
    value: '2.5 GB',
    icon: 'el-icon-folder-opened',
    gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
  }
])

// 筛选表单
const filterForm = ref({
  topic: 'all',
  sentiment: 'all',
  dateRange: null
})

// 表格数据
const tableData = ref([
  {
    id: 1,
    topic: '#人工智能#',
    content: '这是一条关于人工智能的评论...',
    sentiment: '正面',
    time: '2025-12-16 10:30:00'
  },
  {
    id: 2,
    topic: '#ChatGPT#',
    content: '关于ChatGPT的讨论内容...',
    sentiment: '中性',
    time: '2025-12-16 09:15:00'
  },
  {
    id: 3,
    topic: '#春节#',
    content: '春节相关的评论文本...',
    sentiment: '正面',
    time: '2025-12-16 08:00:00'
  }
])

// 导出数据
const exportData = (format) => {
  ElMessage.success(`正在导出${format.toUpperCase()}格式数据...`)
}

// 重置筛选
const resetFilter = () => {
  filterForm.value = {
    topic: 'all',
    sentiment: 'all',
    dateRange: null
  }
}

// 应用筛选
const applyFilter = () => {
  ElMessage.info('正在筛选数据...')
}

// 刷新数据
const refreshData = () => {
  ElMessage.success('数据已刷新')
}

// 查看详情
const viewDetail = (row) => {
  ElMessage.info(`查看数据 ID: ${row.id}`)
}

// 删除行
const deleteRow = (row) => {
  ElMessage.warning(`删除数据 ID: ${row.id}`)
}

// 获取情感标签类型
const getSentimentType = (sentiment) => {
  const map = {
    '正面': 'success',
    '负面': 'danger',
    '中性': 'info'
  }
  return map[sentiment] || 'info'
}
</script>

<style scoped>
.data-manage {
  width: 100%;
}

/* 页面标题 */
.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff 0%, #8a2be2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  margin: 0;
  font-size: 14px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 2px;
}

/* 统计卡片 */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  gap: 16px;
  align-items: center;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  border-color: rgba(0, 212, 255, 0.3);
  box-shadow: 0 12px 24px rgba(0, 212, 255, 0.15);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 13px;
  color: #94a3b8;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #f1f5f9;
}

/* 导出卡片 */
.export-card {
  margin-bottom: 30px;
}

.export-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

.export-item {
  background: rgba(30, 41, 59, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.export-item:hover {
  background: rgba(30, 41, 59, 0.6);
  border-color: rgba(0, 212, 255, 0.2);
  transform: translateX(4px);
}

.export-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.csv-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.excel-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.json-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.pdf-icon {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.export-content {
  flex: 1;
}

.export-content h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #f1f5f9;
}

.export-content p {
  margin: 0;
  font-size: 13px;
  color: #64748b;
}

/* 筛选卡片 */
.filter-card {
  margin-bottom: 30px;
}

/* 表格卡片 */
.table-card {
  margin-bottom: 30px;
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

.header-title i {
  font-size: 18px;
  color: #00d4ff;
}

.gradient-btn {
  background: linear-gradient(135deg, #00d4ff 0%, #8a2be2 100%);
  border: none;
  color: white;
  font-weight: 600;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 深色主题表格样式 */
:deep(.el-table) {
  background: transparent;
  color: #e0e0e0;
}

:deep(.el-table th),
:deep(.el-table tr) {
  background: transparent !important;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background: rgba(30, 41, 59, 0.3);
}

:deep(.el-table td),
:deep(.el-table th.is-leaf) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

:deep(.el-table::before) {
  background-color: transparent;
}

:deep(.el-table__body tr:hover > td) {
  background: rgba(0, 212, 255, 0.1) !important;
}

/* 表单深色样式 */
:deep(.el-input__inner),
:deep(.el-select .el-input__inner),
:deep(.el-date-editor .el-input__inner) {
  background: rgba(30, 41, 59, 0.6);
  border-color: rgba(255, 255, 255, 0.1);
  color: #f1f5f9;
}

:deep(.el-form-item__label) {
  color: #94a3b8;
}
</style>
