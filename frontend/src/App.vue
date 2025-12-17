<template>
  <div id="app" class="tech-container">
    <!-- 背景粒子效果 -->
    <div class="particles-bg"></div>
    
    <!-- 渐变背景层 -->
    <div class="gradient-overlay"></div>
    
    <el-container class="main-container">
      <!-- 顶部导航栏 - 玻璃态设计 -->
      <el-header class="tech-header">
        <div class="header-content">
          <div class="logo-section">
            <div class="logo-icon">
              <i class="el-icon-data-analysis"></i>
            </div>
            <div class="logo-text">
              <h1>微博情感分析平台</h1>
              <span class="subtitle">Weibo Sentiment Analysis Platform</span>
            </div>
          </div>
          
          <!-- 导航菜单 -->
          <el-menu
            :default-active="activeRoute"
            mode="horizontal"
            background-color="transparent"
            text-color="#e0e0e0"
            active-text-color="#00d4ff"
            router
            class="tech-menu"
          >
            <el-menu-item index="/">
              <i class="el-icon-monitor"></i>
              <span>仪表盘</span>
            </el-menu-item>
            <el-menu-item index="/manage">
              <i class="el-icon-setting"></i>
              <span>数据管理</span>
            </el-menu-item>
            <el-menu-item index="/crawler">
              <i class="el-icon-upload"></i>
              <span>爬虫管理</span>
            </el-menu-item>
            <el-menu-item index="/pipeline">
              <i class="el-icon-connection"></i>
              <span>Pipeline</span>
            </el-menu-item>
            <el-menu-item index="/visualization">
              <i class="el-icon-data-analysis"></i>
              <span>数据可视化</span>
            </el-menu-item>
            <el-menu-item index="/insight">
              <i class="el-icon-magic-stick"></i>
              <span>AI洞察</span>
            </el-menu-item>
          </el-menu>
          
          <!-- 右侧操作区 -->
          <div class="header-actions">
            <el-badge :value="3" class="notification-badge">
              <el-button circle class="action-btn">
                <i class="el-icon-bell"></i>
              </el-button>
            </el-badge>
          </div>
        </div>
      </el-header>
      
      <!-- 主内容区 -->
      <el-main class="tech-main">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeRoute = computed(() => route.path)
</script>

<style>
/* 全局重置和基础样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow-x: hidden;
}

#app {
  min-height: 100vh;
  position: relative;
}

/* 科技风容器 */
.tech-container {
  min-height: 100vh;
  background: #0a0e27;
  position: relative;
  overflow: hidden;
}

/* 粒子背景效果 */
.particles-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(circle at 10% 20%, rgba(0, 212, 255, 0.05) 0%, transparent 50%),
    radial-gradient(circle at 90% 80%, rgba(138, 43, 226, 0.05) 0%, transparent 50%);
  pointer-events: none;
  animation: pulse 8s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* 渐变遮罩层 */
.gradient-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, 
    rgba(0, 212, 255, 0.03) 0%,
    rgba(138, 43, 226, 0.03) 100%);
  pointer-events: none;
  z-index: 1;
}

.main-container {
  position: relative;
  z-index: 2;
  min-height: 100vh;
}

/* 顶部导航栏 - 玻璃态效果 */
.tech-header {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 212, 255, 0.1);
  padding: 0;
  height: 80px;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 40px;
  max-width: 1920px;
  margin: 0 auto;
}

/* Logo区域 */
.logo-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-icon {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #00d4ff 0%, #8a2be2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
  box-shadow: 0 8px 20px rgba(0, 212, 255, 0.3);
  animation: glow 3s ease-in-out infinite;
}

@keyframes glow {
  0%, 100% { box-shadow: 0 8px 20px rgba(0, 212, 255, 0.3); }
  50% { box-shadow: 0 8px 30px rgba(0, 212, 255, 0.6); }
}

.logo-text h1 {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff 0%, #8a2be2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
  letter-spacing: -0.5px;
}

.logo-text .subtitle {
  font-size: 11px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  display: block;
  margin-top: 2px;
}

/* 科技风菜单 */
.tech-menu {
  border: none !important;
  background: transparent !important;
}

.tech-menu .el-menu-item {
  border: none !important;
  font-size: 15px;
  font-weight: 500;
  padding: 0 24px;
  height: 50px;
  line-height: 50px;
  margin: 0 8px;
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.tech-menu .el-menu-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(138, 43, 226, 0.1) 100%);
  opacity: 0;
  transition: opacity 0.3s;
}

.tech-menu .el-menu-item:hover::before {
  opacity: 1;
}

.tech-menu .el-menu-item.is-active {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(138, 43, 226, 0.15) 100%);
  border: 1px solid rgba(0, 212, 255, 0.3);
}

.tech-menu .el-menu-item i {
  margin-right: 8px;
  font-size: 18px;
}

/* 右侧操作区 */
.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.action-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  color: #e0e0e0;
  width: 40px;
  height: 40px;
  transition: all 0.3s;
}

.action-btn:hover {
  background: rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
  color: #00d4ff;
  transform: translateY(-2px);
}

.notification-badge {
  margin-right: 8px;
}

/* 主内容区 */
.tech-main {
  padding: 30px;
  max-width: 1920px;
  margin: 0 auto;
  min-height: calc(100vh - 80px);
}

/* 页面切换动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* Element Plus 深色主题定制 */
.el-button {
  border-radius: 8px;
  font-weight: 500;
}

.el-card {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.el-table {
  background: transparent;
  color: #e0e0e0;
}

.el-table th,
.el-table tr {
  background: transparent !important;
}

.el-table td,
.el-table th.is-leaf {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.el-table::before {
  background-color: transparent;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}

::-webkit-scrollbar-thumb {
  background: rgba(0, 212, 255, 0.3);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 212, 255, 0.5);
}
</style>
