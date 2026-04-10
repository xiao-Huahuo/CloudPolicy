<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="echarts-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import * as echarts from 'echarts/core';
import { LineChart, BarChart } from 'echarts/charts';
import { TooltipComponent, GridComponent, LegendComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { getChartTheme, observeChartAppearance, withAlpha } from '@/utils/chartTheme';

echarts.use([LineChart, BarChart, TooltipComponent, GridComponent, LegendComponent, CanvasRenderer]);

const props = defineProps({
  chartData: { type: Object, default: () => ({}) },
  compareData: { type: Object, default: () => null },
  chartType: { type: String, default: 'line' },
});

const chartRef = ref(null);
let myChart = null;
let themeObserver = null;

const buildSeries = (dataMap, prefix, hitColor, scoreColor, theme) => {
  const keys = Object.keys(dataMap || {});
  const hitRate = keys.map((key) => dataMap[key]?.hit_rate ?? 0);
  const avgScore = keys.map((key) => dataMap[key]?.avg_score ?? 0);
  const isLine = props.chartType === 'line';

  const createAreaStyle = (color, alpha) => (
    isLine
      ? {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: withAlpha(color, alpha) },
            { offset: 1, color: withAlpha(color, 0) },
          ]),
        }
      : undefined
  );

  return [
    {
      name: `${prefix}命中率`,
      type: props.chartType,
      data: hitRate,
      smooth: true,
      showSymbol: false,
      itemStyle: { color: hitColor },
      lineStyle: { width: 2, color: hitColor },
      areaStyle: createAreaStyle(hitColor, theme.dark ? 0.32 : 0.2),
    },
    {
      name: `${prefix}相关度`,
      type: props.chartType,
      data: avgScore,
      smooth: true,
      showSymbol: false,
      itemStyle: { color: scoreColor },
      lineStyle: { width: 2, color: scoreColor },
      areaStyle: createAreaStyle(scoreColor, theme.dark ? 0.28 : 0.16),
    },
  ];
};

const updateChart = () => {
  if (!myChart) return;

  const theme = getChartTheme();
  const baseData = props.chartData || {};
  const compareData = props.compareData || null;
  let keys = Object.keys(baseData);
  let series = buildSeries(baseData, '个人', theme.primary, theme.secondary, theme);

  if (compareData) {
    const compareKeys = Object.keys(compareData);
    keys = Array.from(new Set([...keys, ...compareKeys])).sort();
    const align = (source) => Object.fromEntries(
      keys.map((key) => [key, source?.[key] || { hit_rate: 0, avg_score: 0 }]),
    );
    series = [
      ...buildSeries(align(baseData), '个人', theme.primary, theme.secondary, theme),
      ...buildSeries(align(compareData), '全体', theme.accentCool, theme.accentMint, theme),
    ];
  }

  myChart.setOption({
    grid: { left: '3%', right: '4%', bottom: '6%', top: '12%', containLabel: true },
    tooltip: {
      trigger: 'axis',
      backgroundColor: theme.tooltipBg,
      borderColor: theme.tooltipBorder,
      textStyle: { color: theme.textPrimary },
    },
    legend: {
      right: 0,
      textStyle: { color: theme.textSecondary, fontSize: 11 },
    },
    xAxis: {
      type: 'category',
      data: keys,
      axisLine: { lineStyle: { color: theme.axisLine } },
      axisLabel: { color: theme.textSecondary },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 1,
      axisLabel: { color: theme.textSecondary },
      splitLine: { lineStyle: { color: theme.splitLine, type: 'dashed' } },
    },
    series,
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
watch(() => props.compareData, () => nextTick(updateChart), { deep: true });
watch(() => props.chartType, () => nextTick(updateChart));

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
