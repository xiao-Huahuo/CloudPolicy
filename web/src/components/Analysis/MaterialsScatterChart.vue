<template>
  <div class="chart-wrapper">
    <div ref="chartRef" class="echarts-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import * as echarts from 'echarts/core';
import { GraphChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent,
} from 'echarts/components';
import { LabelLayout, UniversalTransition } from 'echarts/features';
import { CanvasRenderer } from 'echarts/renderers';
import { getChartTheme, observeChartAppearance } from '@/utils/chartTheme';

echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent,
  GraphChart,
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
  const dataArray = Object.entries(props.chartData || {})
    .sort((a, b) => b[1] - a[1])
    .map(([name, value]) => ({ name, value }));

  const nodes = (dataArray.length ? dataArray : [{ name: '暂无数据', value: 0 }]).map((item, index) => ({
    name: item.name,
    value: item.value,
    symbolSize: Math.max(40, 30 + Math.sqrt(item.value) * 14),
    itemStyle: {
      color: theme.palette[index % theme.palette.length],
    },
    label: {
      show: true,
      position: 'bottom',
      formatter: '{b}',
      color: theme.dark ? '#ffffff' : theme.textSecondary,
      fontSize: 12,
      distance: 5,
    },
  }));

  myChart.setOption({
    tooltip: {
      formatter: (param) => (
        param.dataType === 'node' ? `${param.name}: ${param.value} 次` : ''
      ),
      backgroundColor: theme.tooltipBg,
      borderColor: theme.tooltipBorder,
      textStyle: { color: theme.textPrimary },
    },
    animationDuration: 1500,
    animationEasingUpdate: 'quinticInOut',
    series: [
      {
        name: '高频材料',
        type: 'graph',
        layout: 'force',
        data: nodes,
        force: {
          repulsion: 220,
          edgeLength: 60,
          gravity: 0.08,
          layoutAnimation: true,
        },
        roam: false,
        draggable: true,
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
