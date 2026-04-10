<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="echarts-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import * as echarts from 'echarts/core';
import { PieChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  DatasetComponent,
  TransformComponent,
} from 'echarts/components';
import { LabelLayout } from 'echarts/features';
import { CanvasRenderer } from 'echarts/renderers';
import { getChartTheme, observeChartAppearance, withAlpha } from '@/utils/chartTheme';

echarts.use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  DatasetComponent,
  TransformComponent,
  PieChart,
  LabelLayout,
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
  const dataArray = Object.entries(props.chartData || {}).map(([name, value]) => ({ name, value }));
  if (dataArray.length === 0) {
    dataArray.push({ name: '暂无数据', value: 0 });
  }

  myChart.setOption({
    color: theme.palette,
    tooltip: {
      trigger: 'item',
      formatter: '{b} : {c} 件 ({d}%)',
      backgroundColor: theme.tooltipBg,
      borderColor: theme.tooltipBorder,
      textStyle: {
        color: theme.textPrimary,
      },
    },
    legend: {
      show: false,
    },
    series: [
      {
        name: '通知类型',
        type: 'pie',
        roseType: 'radius',
        radius: ['20%', '80%'],
        center: ['50%', '55%'],
        itemStyle: {
          borderRadius: 8,
          borderColor: 'transparent',
          borderWidth: 0,
        },
        label: {
          show: true,
          formatter: '{b}\n{c} 件',
          color: theme.dark ? '#ffffff' : theme.textPrimary,
          fontWeight: 'bold',
          lineHeight: 20,
        },
        labelLine: {
          show: true,
          length: 15,
          length2: 30,
          smooth: 0.2,
          lineStyle: {
            color: withAlpha(theme.textSecondary, theme.dark ? 0.74 : 0.42),
            width: 1.5,
          },
        },
        data: dataArray.sort((a, b) => a.value - b.value),
        animationType: 'expansion',
        animationEasing: 'cubicOut',
        animationDuration: 1200,
        animationDelay: (idx) => idx * 80,
        startAngle: 90,
        clockwise: true,
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
  min-height: 250px;
}
</style>
