<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="echarts-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import * as echarts from 'echarts/core';
import { ScatterChart } from 'echarts/charts';
import { TooltipComponent, GridComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { getChartTheme, observeChartAppearance, withAlpha } from '@/utils/chartTheme';

echarts.use([ScatterChart, TooltipComponent, GridComponent, CanvasRenderer]);

const props = defineProps({
  chartData: { type: Array, default: () => [] },
});

const chartRef = ref(null);
let myChart = null;
let themeObserver = null;

const updateChart = () => {
  if (!myChart) return;

  const theme = getChartTheme();
  const points = (props.chartData || []).map((item, index) => ({
    value: [item.x || 0, item.y || 0, item.size || 8, item.label || ''],
    itemStyle: {
      color: theme.palette[index % theme.palette.length],
      opacity: 0.78,
      borderColor: withAlpha(theme.cardBg, theme.dark ? 0.72 : 0.9),
      borderWidth: 1,
    },
  }));

  myChart.setOption({
    grid: { left: '6%', right: '6%', bottom: '10%', top: '8%', containLabel: true },
    tooltip: {
      backgroundColor: theme.tooltipBg,
      borderColor: theme.tooltipBorder,
      textStyle: { color: theme.textPrimary },
      formatter: (params) => {
        const [x, y, size, label] = params.value;
        return `长度: ${x}<br/>难度: ${y}<br/>权重: ${size}<br/>类型: ${label}`;
      },
    },
    xAxis: {
      type: 'value',
      name: '文本长度',
      nameTextStyle: { color: theme.textSecondary },
      axisLabel: { color: theme.textSecondary },
      axisLine: { lineStyle: { color: theme.axisLine } },
      splitLine: { lineStyle: { color: theme.splitLine, type: 'dashed' } },
    },
    yAxis: {
      type: 'value',
      name: '综合难度',
      nameTextStyle: { color: theme.textSecondary },
      min: 0,
      max: 3.5,
      axisLabel: { color: theme.textSecondary },
      axisLine: { lineStyle: { color: theme.axisLine } },
      splitLine: { lineStyle: { color: theme.splitLine, type: 'dashed' } },
    },
    series: [
      {
        type: 'scatter',
        data: points,
        symbolSize: (val) => val[2],
      },
    ],
  }, true);
};

const initChart = () => {
  if (!chartRef.value) return;
  myChart?.dispose();
  myChart = echarts.init(chartRef.value);
  updateChart();
};

const handleResize = () => {
  myChart?.resize();
};

watch(() => props.chartData, () => nextTick(updateChart), { deep: true });

onMounted(() => {
  initChart();
  themeObserver = observeChartAppearance(() => nextTick(updateChart));
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  themeObserver?.disconnect();
  myChart?.dispose();
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
