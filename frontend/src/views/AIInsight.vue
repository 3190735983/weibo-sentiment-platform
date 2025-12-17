<template>
  <div class="ai-insight">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>AI 智能洞察</h1>
      <p class="subtitle">AI-Powered Sentiment Analysis Insights</p>
    </div>

    <!-- AI功能卡片网格 -->
    <div class="features-grid">
      <!-- 智能报告生成 -->
      <el-card class="feature-card report-card">
        <div class="feature-icon">
          <i class="el-icon-document"></i>
        </div>
        <h3>智能报告生成</h3>
        <p>AI自动分析话题数据，生成专业的情感分析报告</p>
        <el-select v-model="selectedTopic" placeholder="选择话题" style="width: 100%; margin: 16px 0;">
          <el-option label="人工智能" value="ai"></el-option>
          <el-option label="ChatGPT" value="gpt"></el-option>
          <el-option label="春节" value="spring"></el-option>
        </el-select>
        <el-button class="gradient-btn" style="width: 100%;" @click="generateReport">
          <i class="el-icon-magic-stick"></i>
          生成报告
        </el-button>
      </el-card>

      <!-- 异常检测 -->
      <el-card class="feature-card anomaly-card">
        <div class="feature-icon">
          <i class="el-icon-warning"></i>
        </div>
        <h3>情感异常检测</h3>
        <p>自动识别情感突变和异常评论，及时预警风险</p>
        <div class="anomaly-stats">
          <div class="anomaly-stat">
            <span class="label">检测到异常</span>
            <span class="value warning">3</span>
          </div>
          <div class="anomaly-stat">
            <span class="label">风险级别</span>
            <span class="value medium">中等</span>
          </div>
        </div>
        <el-button class="detect-btn" style="width: 100%;" @click="detectAnomaly">
          <i class="el-icon-search"></i>
          开始检测
        </el-button>
      </el-card>

      <!-- AI对话助手 -->
      <el-card class="feature-card chat-card">
        <div class="feature-icon">
          <i class="el-icon-chat-dot-round"></i>
        </div>
        <h3>AI 对话分析</h3>
        <p>与AI助手交流，获取深度数据洞察和建议</p>
        <div class="quick-questions">
          <div class="question-tag" @click="askQuestion('总体情感如何？')">
            总体情感如何？
          </div>
          <div class="question-tag" @click="askQuestion('有什么趋势？')">
            有什么趋势？
          </div>
        </div>
        <el-button class="chat-btn" style="width: 100%;" @click="showChatDialog">
          <i class="el-icon-message"></i>
          开始对话
        </el-button>
      </el-card>
    </div>

    <!-- AI生成的报告展示区 -->
    <el-card class="report-display-card" v-if="reportContent">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <i class="el-icon-document-checked"></i>
            <span>AI 分析报告</span>
          </div>
          <div class="header-actions">
            <el-button size="small" @click="downloadReport">
              <i class="el-icon-download"></i>
              下载
            </el-button>
            <el-button size="small" @click="shareReport">
              <i class="el-icon-share"></i>
              分享
            </el-button>
          </div>
        </div>
      </template>

      <div class="report-content">
        <div class="report-section">
          <h3>📊 数据概览</h3>
          <p>{{ reportContent.overview }}</p>
        </div>

        <div class="report-section">
          <h3>💡 关键发现</h3>
          <ul>
            <li v-for="(insight, index) in reportContent.insights" :key="index">
              {{ insight }}
            </li>
          </ul>
        </div>

        <div class="report-section">
          <h3>🎯 趋势分析</h3>
          <p>{{ reportContent.trend }}</p>
        </div>

        <div class="report-section">
          <h3>⚡ 行动建议</h3>
          <ul>
            <li v-for="(suggestion, index) in reportContent.suggestions" :key="index">
              {{ suggestion }}
            </li>
          </ul>
        </div>
      </div>
    </el-card>

    <!-- 空状态提示 -->
    <el-card class="empty-state-card" v-else>
      <div class="empty-state">
        <i class="el-icon-magic-stick"></i>
        <h3>准备好探索数据洞察了吗？</h3>
        <p>选择上方任一功能开始使用AI分析</p>
      </div>
    </el-card>

    <!-- AI对话框 -->
    <el-dialog
      v-model="chatDialogVisible"
      title="AI 对话助手"
      width="700px"
      class="chat-dialog"
    >
      <div class="chat-container">
        <div class="chat-messages" ref="chatMessagesRef">
          <div 
            v-for="(msg, index) in chatMessages" 
            :key="index" 
            class="message"
            :class="msg.role === 'user' ? 'user-message' : 'ai-message'"
          >
            <div class="message-avatar">
              <i :class="msg.role === 'user' ? 'el-icon-user' : 'el-icon-magic-stick'"></i>
            </div>
            <div class="message-content">
              <div class="message-text">{{ msg.content }}</div>
              <div class="message-time">{{ msg.time }}</div>
            </div>
          </div>
        </div>

        <div class="chat-input">
          <el-input
            v-model="userInput"
            placeholder="输入您的问题..."
            @keyup.enter="sendMessage"
          >
            <template #suffix>
              <el-button 
                circle 
                type="primary" 
                :icon="'el-icon-d-arrow-right'"
                @click="sendMessage"
              />
            </template>
          </el-input>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'

// 数据
const selectedTopic = ref('ai')
const reportContent = ref(null)
const chatDialogVisible = ref(false)
const chatMessages = ref([
  {
    role: 'ai',
    content: '您好！我是AI分析助手，很高兴为您服务。您想了解什么数据洞察呢？',
    time: '14:30'
  }
])
const userInput = ref('')
const chatMessagesRef = ref(null)

// 生成报告
const generateReport = () => {
  const loading = ElMessage({
    message: 'AI正在分析数据...',
    type: 'info',
    duration: 0
  })

  setTimeout(() => {
    loading.close()
    
    reportContent.value = {
      overview: '本次分析基于过去7天内收集的1,234条评论数据。总体情感倾向为正面（52%），中性占比35%，负面评论占比13%。数据质量良好，样本分布均匀。',
      insights: [
        '正面评论主要集中在产品功能和用户体验方面，用户满意度较高',
        '负面评论多与价格和售后服务相关，需要重点关注',
        '周末时段的评论活跃度明显高于工作日，互动率提升40%',
        '北京、上海、深圳三个城市贡献了60%的评论量'
      ],
      trend: '从趋势来看，正面情感呈稳步上升趋势（环比+8%），负面情感略有下降（环比-3%）。预计未来一周将保持积极态势。建议持续监控用户反馈，及时响应负面评论。',
      suggestions: [
        '加强售后服务体系建设，提升用户满意度',
        '针对高活跃度城市制定精准营销策略',
        '在周末时段增加互动活动，提高用户粘性',
        '定期收集用户反馈，持续优化产品功能'
      ]
    }

    ElNotification({
      title: '报告生成成功',
      message: 'AI已完成数据分析，请查看报告内容',
      type: 'success',
      duration: 3000
    })
  }, 2000)
}

// 异常检测
const detectAnomaly = () => {
  ElMessage.success('异常检测已启动，将在后台运行')
  
  setTimeout(() => {
    ElNotification({
      title: '检测到异常',
      message: '发现3处情感突变点，建议查看详情',
      type: 'warning',
      duration: 5000
    })
  }, 3000)
}

// 显示对话框
const showChatDialog = () => {
  chatDialogVisible.value = true
}

// 快速提问
const askQuestion = (question) => {
  userInput.value = question
  sendMessage()
}

// 发送消息
const sendMessage = () => {
  if (!userInput.value.trim()) return

  // 添加用户消息
  chatMessages.value.push({
    role: 'user',
    content: userInput.value,
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  })

  const question = userInput.value
  userInput.value = ''

  // 模拟AI回复
  setTimeout(() => {
    let aiResponse = ''
    
    if (question.includes('情感') || question.includes('总体')) {
      aiResponse = '根据最新数据分析，整体情感倾向良好。正面评论占52%，主要集中在产品质量和用户体验方面。负面评论占13%，主要涉及价格和售后服务。建议重点关注负面反馈，持续改进。'
    } else if (question.includes('趋势')) {
      aiResponse = '从近期趋势来看，正面情感呈现稳步上升态势（周环比+8%），用户满意度持续提升。预计未来一周将保持积极走势。建议继续保持现有服务水平，同时加强用户互动。'
    } else {
      aiResponse = '感谢您的提问。我正在分析相关数据，请稍等片刻...'
    }

    chatMessages.value.push({
      role: 'ai',
      content: aiResponse,
      time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    })

    // 滚动到底部
    if (chatMessagesRef.value) {
      chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
    }
  }, 1000)

  showChatDialog()
}

// 下载报告
const downloadReport = () => {
  ElMessage.success('报告下载功能开发中...')
}

// 分享报告
const shareReport = () => {
  ElMessage.success('报告分享功能开发中...')
}
</script>

<style scoped>
.ai-insight {
  width: 100%;
}

/* 页面标题 */
.page-header {
  margin-bottom: 40px;
  text-align: center;
}

.page-header h1 {
  margin: 0 0 12px 0;
  font-size: 36px;
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

/* 功能卡片网格 */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
  margin-bottom: 30px;
}

.feature-card {
  text-align: center;
  padding: 30px 20px;
  transition: all 0.3s;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 16px 40px rgba(0, 212, 255, 0.2);
}

.feature-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  color: white;
  background: linear-gradient(135deg, #00d4ff 0%, #8a2be2 100%);
  box-shadow: 0 8px 24px rgba(0, 212, 255, 0.3);
}

.feature-card h3 {
  margin: 0 0 12px 0;
  font-size: 20px;
  font-weight: 600;
  color: #f1f5f9;
}

.feature-card p {
  margin: 0 0 20px 0;
  font-size: 14px;
  color: #94a3b8;
  line-height: 1.6;
}

.gradient-btn {
  background: linear-gradient(135deg, #00d4ff 0%, #8a2be2 100%);
  border: none;
  color: white;
  font-weight: 600;
}

.detect-btn {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  border: none;
  color: white;
  font-weight: 600;
}

.chat-btn {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border: none;
  color: white;
  font-weight: 600;
}

/* 异常统计 */
.anomaly-stats {
  display: flex;
  justify-content: space-around;
  margin: 20px 0;
  padding: 16px;
  background: rgba(30, 41, 59, 0.4);
  border-radius: 12px;
}

.anomaly-stat {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.anomaly-stat .label {
  font-size: 12px;
  color: #94a3b8;
}

.anomaly-stat .value {
  font-size: 24px;
  font-weight: 700;
}

.anomaly-stat .value.warning {
  color: #fa709a;
}

.anomaly-stat .value.medium {
  color: #fee140;
}

/* 快速问题 */
.quick-questions {
  display: flex;
  gap: 8px;
  margin: 16px 0;
  flex-wrap: wrap;
  justify-content: center;
}

.question-tag {
  padding: 8px 16px;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 20px;
  font-size: 13px;
  color: #00d4ff;
  cursor: pointer;
  transition: all 0.3s;
}

.question-tag:hover {
  background: rgba(0, 212, 255, 0.2);
  transform: scale(1.05);
}

/* 报告展示 */
.report-display-card,
.empty-state-card {
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
  font-size: 18px;
  font-weight: 600;
  color: #f1f5f9;
}

.header-title i {
  font-size: 20px;
  color: #00d4ff;
}

.report-content {
  line-height: 1.8;
  color: #e0e0e0;
}

.report-section {
  margin-bottom: 32px;
}

.report-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: #f1f5f9;
  margin: 0 0 16px 0;
}

.report-section p {
  margin: 0;
  color: #94a3b8;
}

.report-section ul {
  margin: 0;
  padding-left: 24px;
}

.report-section li {
  margin-bottom: 12px;
  color: #94a3b8;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: #64748b;
}

.empty-state i {
  font-size: 80px;
  margin-bottom: 20px;
  opacity: 0.3;
  background: linear-gradient(135deg, #00d4ff 0%, #8a2be2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.empty-state h3 {
  margin: 0 0 12px 0;
  font-size: 20px;
  color: #94a3b8;
}

/* 对话框 */
.chat-container {
  height: 500px;
  display: flex;
  flex-direction: column;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: rgba(30, 41, 59, 0.3);
  border-radius: 12px;
  margin-bottom: 16px;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #00d4ff 0%, #8a2be2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  flex-shrink: 0;
}

.user-message .message-avatar {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.message-content {
  flex: 1;
  max-width: 70%;
}

.message-text {
  padding: 12px 16px;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 12px;
  color: #e0e0e0;
  line-height: 1.6;
}

.user-message .message-text {
  background: rgba(0, 212, 255, 0.15);
}

.message-time {
  margin-top: 4px;
  font-size: 12px;
  color: #64748b;
}

.user-message .message-time {
  text-align: right;
}

.chat-input {
  padding: 0;
}

/* 深色主题对话框 */
:deep(.chat-dialog .el-dialog) {
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(0, 212, 255, 0.2);
}

:deep(.chat-dialog .el-dialog__title) {
  color: #f1f5f9;
  font-size: 18px;
  font-weight: 600;
}

:deep(.el-input__inner) {
  background: rgba(30, 41, 59, 0.6);
  border-color: rgba(255, 255, 255, 0.1);
  color: #f1f5f9;
}
</style>
