<template>
  <div class="chart-wrapper">
    <div v-if="loading" class="placeholder-text">词云组件加载中...</div>
    <div ref="chartRef" class="echarts-container" v-show="!loading"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick, shallowRef } from 'vue';
import { useRouter } from 'vue-router';
import * as echarts from 'echarts/core';
import { TitleComponent, TooltipComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { getChartTheme, observeChartAppearance } from '@/utils/chartTheme';

echarts.use([TitleComponent, TooltipComponent, CanvasRenderer]);

const props = defineProps({
  chartData: { type: Object, default: () => ({}) },
});

const router = useRouter();
const chartRef = ref(null);
const myChart = shallowRef(null);
const loading = ref(true);
let themeObserver = null;

const updateChart = () => {
  if (!myChart.value) return;

  const theme = getChartTheme();
  const colors = [
    theme.primary,
    theme.secondary,
    theme.accentCool,
    theme.accentMint,
    theme.primaryLight,
    theme.primaryDark,
  ];
  const dataArray = Object.entries(props.chartData || {}).map(([name, value]) => ({ name, value }));
  if (dataArray.length === 0) {
    dataArray.push({ name: '暂无数据', value: 0 });
  }

  myChart.value.setOption({
    tooltip: {
      show: true,
      formatter: '{b}: {c} 次',
      backgroundColor: theme.tooltipBg,
      borderColor: theme.tooltipBorder,
      textStyle: { color: theme.textPrimary },
    },
    series: [{
      type: 'wordCloud',
      shape: 'square',
      keepAspect: false,
      left: 0,
      top: 0,
      right: 0,
      bottom: 0,
      width: '100%',
      height: '100%',
      sizeRange: [14, 52],
      rotationRange: [-30, 30],
      rotationStep: 15,
      gridSize: 4,
      drawOutOfBound: false,
      layoutAnimation: true,
      textStyle: {
        fontFamily: 'sans-serif',
        fontWeight: 'bold',
        color: () => colors[Math.floor(Math.random() * colors.length)],
      },
      emphasis: {
        focus: 'self',
        textStyle: {
          textShadowBlur: 8,
          textShadowColor: theme.dark ? 'rgba(0, 0, 0, 0.55)' : 'rgba(17, 17, 17, 0.28)',
        },
      },
      data: dataArray,
    }],
  }, true);
};

const initChart = async () => {
  try {
    await import('echarts-wordcloud');
    loading.value = false;
    await nextTick();
    if (chartRef.value) {
      myChart.value?.dispose();
      myChart.value = echarts.init(chartRef.value);
      updateChart();
      myChart.value.on('click', (params) => {
        if (params.name && params.name !== '暂无数据') {
          router.push({ path: '/search', query: { q: params.name } });
        }
      });
    }
  } catch (error) {
    console.error('加载 echarts-wordcloud 失败', error);
  }
};

const handleResize = () => {
  myChart.value?.resize();
};

watch(() => props.chartData, () => {
  if (!loading.value) {
    nextTick(updateChart);
  }
}, { deep: true });

onMounted(() => {
  initChart();
  themeObserver = observeChartAppearance(() => {
    if (!loading.value) {
      nextTick(updateChart);
    }
  });
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  themeObserver?.disconnect();
  myChart.value?.dispose();
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
  min-height: 250px;
}

.placeholder-text {
  color: var(--text-secondary);
  font-size: 14px;
  text-align: center;
  padding: 20px;
}
</style>
