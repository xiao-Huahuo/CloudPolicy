<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="echarts-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import * as echarts from 'echarts/core';
import {
  LineChart,
  BarChart
} from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent
} from 'echarts/components';
import { LabelLayout, UniversalTransition } from 'echarts/features';
import { CanvasRenderer } from 'echarts/renderers';

// 注册必须的组件
echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent,
  LineChart,
  BarChart,
  LabelLayout,
  UniversalTransition,
  CanvasRenderer
]);

const props = defineProps({
  chartData: {
    type: Object,
    default: () => ({})
  },
  chartType: {
    type: String,
    default: 'line' // 'line' 或 'bar'
  }
});

const chartRef = ref(null);
let myChart = null;

// 初始化 ECharts
const initChart = () => {
  if (chartRef.value) {
    // 销毁旧实例，确保干净渲染
    if (myChart != null && myChart != "" && myChart != undefined) {
      myChart.dispose();
    }
    myChart = echarts.init(chartRef.value);
    updateChart();
  }
};

// 更新图表配置
const updateChart = () => {
  if (!myChart) return;

  const xAxisData = Object.keys(props.chartData || {});
  const yAxisData = Object.values(props.chartData || {});

  const option = {
    animationDuration: 2000, // 动画持续时间 2秒
    animationEasing: 'cubicOut', // 平滑缓动效果
    grid: {
      left: '3%',
      right: '4%',
      bottom: '5%',
      top: '10%',
      containLabel: true
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderColor: '#eee',
      textStyle: {
        color: '#333'
      },
      formatter: '{b}: {c} 分钟' // 横轴现在是“第x次”，直接显示值即可
    },
    xAxis: {
      type: 'category',
      data: xAxisData,
      axisLine: {
        lineStyle: {
          color: '#eee'
        }
      },
      axisLabel: {
        color: '#999',
        fontFamily: 'sans-serif'
      },
      axisTick: {
        show: false
      }
    },
    yAxis: {
      type: 'value',
      name: '节省时间(分钟)',
      nameTextStyle: {
        color: '#ccc',
        align: 'right'
      },
      splitLine: {
        lineStyle: {
          color: '#f5f5f5',
          type: 'dashed'
        }
      },
      axisLabel: {
        color: '#999'
      }
    },
    series: [
      {
        data: yAxisData,
        type: props.chartType, // 动态使用 'line' 或 'bar'
        smooth: true, // 曲线平滑
        showSymbol: false, // 曲线隐藏节点，更极简
        itemStyle: {
          // 如果是柱状图，使用主色调从左往右渐变（此处为单柱颜色一致的效果模拟）
          color: props.chartType === 'bar' ? '#e67e22' : '#c0392b',
          borderRadius: props.chartType === 'bar' ? [4, 4, 0, 0] : 0
        },
        lineStyle: {
          width: 3,
          color: '#c0392b'
        },
        areaStyle: props.chartType === 'line' ? {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(192, 57, 43, 0.25)' },
            { offset: 1, color: 'rgba(192, 57, 43, 0)' }
          ])
        } : null,
        animationDelay: function (idx) {
          // 线条从左往右延伸的动画核心：让不同索引的数据点延迟出现
          return idx * 100;
        }
      }
    ]
  };

  // 如果是柱状图，根据 readme 规定设置渐变色
  // "主色调: 渐变色 #d4ff80-#00e2dc-#002059"
  if (props.chartType === 'bar') {
      option.series[0].itemStyle = {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#e67e22' },
            { offset: 0.5, color: '#c0392b' },
            { offset: 1, color: '#922b21' }
          ]),
          borderRadius: [4, 4, 0, 0]
      }
  }

  myChart.setOption(option, true); // true 表示不合并，全新渲染
};

// 监听数据和类型的变化
watch(() => props.chartData, () => {
  nextTick(() => {
    updateChart();
  });
}, { deep: true });

watch(() => props.chartType, () => {
  nextTick(() => {
    updateChart();
  });
});

// 监听窗口大小改变，重绘图表
const handleResize = () => {
  if (myChart) {
    myChart.resize();
  }
};

onMounted(() => {
  initChart();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  if (myChart) {
    myChart.dispose();
  }
});
</script>

<style scoped>
.chart-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.echarts-container {
  flex: 1;
  width: 100%;
  min-height: 200px;
}
</style>
