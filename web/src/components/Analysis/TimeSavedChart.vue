<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="echarts-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import * as echarts from 'echarts/core';
import { LineChart, BarChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent,
  LegendComponent,
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
  LegendComponent,
  LineChart,
  BarChart,
  LabelLayout,
  UniversalTransition,
  CanvasRenderer,
]);

const props = defineProps({
  chartData: { type: Object, default: () => ({}) },
  compareData: { type: Object, default: () => null },
  chartType: { type: String, default: 'line' },
});

const chartRef = ref(null);
let myChart = null;
let themeObserver = null;

const buildGradient = (theme, colors) => new echarts.graphic.LinearGradient(0, 0, 0, 1, colors.map(([offset, color]) => ({
  offset,
  color,
})));

const buildSeries = (name, values, colorStart, colorEnd, theme) => {
  const isBar = props.chartType === 'bar';
  const color = colorStart;

  return {
    name,
    type: props.chartType,
    data: values,
    smooth: true,
    showSymbol: false,
    itemStyle: {
      color: isBar
        ? buildGradient(theme, [
            [0, colorStart],
            [1, colorEnd],
          ])
        : color,
      borderRadius: isBar ? [6, 6, 0, 0] : 0,
    },
    lineStyle: {
      width: 3,
      color,
    },
    areaStyle: isBar ? undefined : {
      color: buildGradient(theme, [
        [0, withAlpha(colorStart, theme.dark ? 0.34 : 0.24)],
        [1, withAlpha(colorStart, 0)],
      ]),
    },
  };
};

const updateChart = () => {
  if (!myChart) return;

  const theme = getChartTheme();
  const keys = Object.keys(props.chartData || {});
  const values = Object.values(props.chartData || {});
  const compareValues = props.compareData ? keys.map((key) => props.compareData[key] ?? 0) : [];

  const series = [
    buildSeries('个人', values, theme.primary, theme.secondary, theme),
  ];

  if (props.compareData) {
    series.push(buildSeries('全体', compareValues, theme.accentCool, theme.accentMint, theme));
  }

  myChart.setOption({
    animationDuration: 1200,
    animationEasing: 'cubicOut',
    grid: {
      left: '3%',
      right: '4%',
      bottom: '5%',
      top: '10%',
      containLabel: true,
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: props.chartType === 'bar' ? 'shadow' : 'line',
      },
      backgroundColor: theme.tooltipBg,
      borderColor: theme.tooltipBorder,
      textStyle: {
        color: theme.textPrimary,
      },
      formatter: (params) => {
        const list = Array.isArray(params) ? params : [params];
        const header = list[0]?.name ?? '';
        const lines = list.map((item) => `${item.seriesName}: ${item.value} 分钟`);
        return [header, ...lines].join('<br/>');
      },
    },
    legend: props.compareData ? {
      data: ['个人', '全体'],
      right: 0,
      textStyle: { color: theme.textSecondary, fontSize: 11 },
    } : undefined,
    xAxis: {
      type: 'category',
      data: keys,
      axisLine: {
        lineStyle: {
          color: theme.axisLine,
        },
      },
      axisLabel: {
        color: theme.textSecondary,
      },
      axisTick: {
        show: false,
      },
    },
    yAxis: {
      type: 'value',
      name: '节省时间(分钟)',
      nameTextStyle: {
        color: theme.textMuted,
      },
      splitLine: {
        lineStyle: {
          color: theme.splitLine,
          type: 'dashed',
        },
      },
      axisLabel: {
        color: theme.textSecondary,
      },
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
