<template>
  <div class="keyword-cloud-simple" :style="{ width: width, height: height }">
    <div class="keywords-container">
      <span
        v-for="(item, index) in data"
        :key="index"
        class="keyword-item"
        :style="getKeywordStyle(item.value)"
      >
        {{ item.name }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: {
    type: Array,
    default: () => [],
    // 期望格式: [{ name: '关键词', value: 100 }, ...]
  },
  width: {
    type: String,
    default: '100%'
  },
  height: {
    type: String,
    default: '400px'
  }
})

// 计算最大最小值，用于归一化字体大小
const maxValue = computed(() => {
  if (props.data.length === 0) return 1
  return Math.max(...props.data.map(item => item.value))
})

const minValue = computed(() => {
  if (props.data.length === 0) return 1
  return Math.min(...props.data.map(item => item.value))
})

// 颜色数组
const colors = [
  '#00d4ff',
  '#0095ff',
  '#8a2be2',
  '#ff00ff',
  '#00ffff',
  '#7b68ee',
  '#4169e1',
  '#1e90ff',
  '#0084ff',
  '#7b68ee'
]

// 获取关键词样式
const getKeywordStyle = (value) => {
  // 归一化字体大小 (12px - 48px)
  const normalized = (value - minValue.value) / (maxValue.value - minValue.value || 1)
  const fontSize = 12 + normalized * 36
  
  // 随机颜色
  const color = colors[Math.floor(Math.random() * colors.length)]
  
  return {
    fontSize: `${fontSize}px`,
    color: color,
    opacity: 0.7 + normalized * 0.3
  }
}
</script>

<style scoped>
.keyword-cloud-simple {
  background: transparent;
  border-radius: 12px;
  overflow: auto;
  padding: 20px;
}

.keywords-container {
  display: flex;
  flex-wrap: wrap;
  gap: 15px 20px;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.keyword-item {
  display: inline-block;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: bold;
  white-space: nowrap;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.keyword-item:hover {
  transform: scale(1.1);
  background: rgba(0, 212, 255, 0.1);
  box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3);
  opacity: 1 !important;
}
</style>
