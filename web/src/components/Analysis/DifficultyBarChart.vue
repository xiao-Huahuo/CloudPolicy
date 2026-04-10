<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="echarts-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import * as echarts from 'echarts/core';
import { BarChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent,
  GraphicComponent,
} from 'echarts/components';
import { LabelLayout, UniversalTransition } from 'echarts/features';
import { CanvasRenderer } from 'echarts/renderers';
import { getChartTheme, observeChartAppearance, withAlpha } from '@/utils/chartTheme';

echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent,
  GraphicComponent,
  BarChart,
  LabelLayout,
  UniversalTransition,
  CanvasRenderer,
]);

const props = defineProps({
  chartData: { type: Object, default: () => ({}) },
});

const chartRef = ref(null);
let myChart = null;
let themeObserver = null;

const updateChart = () => {
  if (!myChart) return;

  const theme = getChartTheme();
  const categories = [
    { key: 'language_complexity', name: '语言' },
    { key: 'handling_complexity', name: '办理' },
    { key: 'risk_level', name: '风险' },
  ];
  const levels = ['低', '中', '高'];
  const levelColors = {
    language_complexity: [withAlpha(theme.primary, 0.45), theme.primaryLight, theme.primary],
    handling_complexity: [withAlpha(theme.secondary, 0.45), theme.secondary, theme.primaryDark],
    risk_level: [withAlpha(theme.accentCool, 0.45), theme.accentCool, theme.accentMint],
  };

  const xAxisData = [];
  const seriesData = [];
  categories.forEach((category) => {
    levels.forEach((level, index) => {
      xAxisData.push(`${category.name}\n${level}`);
      seriesData.push({
        value: props.chartData?.[`${category.key}-${level}`] || 0,
        itemStyle: {
          color: levelColors[category.key][index],
          borderRadius: [4, 4, 0, 0],
        },
      });
    });
  });

  myChart.setOption({
    grid: {
      left: '0%',
      right: '0%',
      bottom: '15%',
      top: '15%',
      containLabel: true,
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const item = params[0];
        const [group, level] = item.name.split('\n');
        return `${group}复杂度(${level}): <strong>${item.value}</strong> 篇`;
      },
      backgroundColor: theme.tooltipBg,
      borderColor: theme.tooltipBorder,
      textStyle: { color: theme.textPrimary },
    },
    xAxis: {
      type: 'category',
      data: xAxisData,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: theme.textSecondary,
        fontSize: 11,
        formatter: (value) => value.split('\n')[1],
      },
    },
    yAxis: {
      type: 'value',
      show: false,
    },
    series: [
      {
        type: 'bar',
        data: seriesData,
        barWidth: '60%',
        label: {
          show: true,
          position: 'top',
          color: theme.textPrimary,
          fontWeight: 'bold',
          formatter: '{c}',
        },
        animationDelay: (idx) => idx * 50,
      },
    ],
    graphic: [
      {
        type: 'group',
        left: '5%',
        bottom: 0,
        children: [
          { type: 'line', shape: { x1: 0, y1: 0, x2: 60, y2: 0 }, style: { stroke: theme.axisLine } },
          { type: 'text', style: { text: '语言', fill: theme.textSecondary, font: '12px sans-serif', x: 18, y: 5 } },
        ],
      },
      {
        type: 'group',
        left: 'center',
        bottom: 0,
        children: [
          { type: 'line', shape: { x1: -30, y1: 0, x2: 30, y2: 0 }, style: { stroke: theme.axisLine } },
          { type: 'text', style: { text: '办理', fill: theme.textSecondary, font: '12px sans-serif', x: -12, y: 5 } },
        ],
      },
      {
        type: 'group',
        right: '5%',
        bottom: 0,
        children: [
          { type: 'line', shape: { x1: 0, y1: 0, x2: 60, y2: 0 }, style: { stroke: theme.axisLine } },
          { type: 'text', style: { text: '风险', fill: theme.textSecondary, font: '12px sans-serif', x: 18, y: 5 } },
        ],
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
  min-height: 180px;
}
</style>
