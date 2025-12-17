<template>
  <div ref="chartContainer" class="sentiment-chart" :style="{ width: width, height: height }"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: {
    type: Object,
    default: () => ({
      positive: 0,
      negative: 0,
      neutral: 0
    }),
    // 期望格式: { positive: 50, negative: 20, neutral: 30 }
  },
  chartType: {
    type: String,
    default: 'pie', // 'pie' 或 'bar'
    validator: (value) => ['pie', 'bar'].includes(value)
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

const chartContainer = ref(null)
let chartInstance = null

const initChart = () => {
  if (!chartContainer.value) return

  // 销毁旧实例
  if (chartInstance) {
    chartInstance.dispose()
  }

  // 创建图表实例
  chartInstance = echarts.init(chartContainer.value)

  const option = props.chartType === 'pie' ? getPieOption() : getBarOption()
  chartInstance.setOption(option)
}

// 饼图配置
const getPieOption = () => {
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderColor: 'rgba(0, 212, 255, 0.3)',
      textStyle: {
        color: '#e0e0e0'
      },
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '10%',
      top: 'center',
      textStyle: {
        color: '#e0e0e0',
        fontSize: 14
      },
      itemWidth: 20,
      itemHeight: 14
    },
    series: [
      {
        name: '情感分布',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['40%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: 'rgba(15, 23, 42, 0.8)',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold',
            color: '#e0e0e0'
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { 
            value: props.data.positive, 
            name: '正面',
            itemStyle: { color: '#67C23A' }
          },
          { 
            value: props.data.negative, 
            name: '负面',
            itemStyle: { color: '#F56C6C' }
          },
          { 
            value: props.data.neutral, 
            name: '中性',
            itemStyle: { color: '#909399' }
          }
        ]
      }
    ]
  }
}

// 柱状图配置
const getBarOption = () => {
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderColor: 'rgba(0, 212, 255, 0.3)',
      textStyle: {
        color: '#e0e0e0'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['正面', '负面', '中性'],
      axisLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      },
      axisLabel: {
        color: '#e0e0e0',
        fontSize: 14
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      },
      axisLabel: {
        color: '#e0e0e0'
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.05)'
        }
      }
    },
    series: [
      {
        name: '数量',
        type: 'bar',
        barWidth: '40%',
        data: [
          {
            value: props.data.positive,
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#67C23A' },
                { offset: 1, color: '#4a8f2a' }
              ])
            }
          },
          {
            value: props.data.negative,
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#F56C6C' },
                { offset: 1, color: '#c54646' }
              ])
            }
          },
          {
            value: props.data.neutral,
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#909399' },
                { offset: 1, color: '#6b6f76' }
              ])
            }
          }
        ],
        itemStyle: {
          borderRadius: [8, 8, 0, 0]
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 212, 255, 0.5)'
          }
        }
      }
    ]
  }
}

// 监听数据变化
watch(() => props.data, () => {
  nextTick(() => {
    initChart()
  })
}, { deep: true })

// 监听图表类型变化
watch(() => props.chartType, () => {
  nextTick(() => {
    initChart()
  })
})

// 窗口大小改变时重绘
const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.sentiment-chart {
  background: transparent;
  border-radius: 12px;
}
</style>
