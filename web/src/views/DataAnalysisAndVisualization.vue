<template>
  <div class="dashboard-container">
    <div class="header-section">
      <PolicyTitle title="数据分析" />
    </div>

    <div v-if="loading" class="loading-state">
      <AgentLoader :size="46" />
      <span>正在分析您的海量数据...</span>
    </div>

    <div v-else class="dashboard-grid">
      <div class="col-left">
        <div class="widget widget-rag-trend">
          <div class="widget-header">
            <h3 class="widget-title">RAG 命中趋势</h3>
            <div class="widget-actions">
              <span class="action-tag" :class="{ active: ragChartType === 'line' }" @click="ragChartType = 'line'">曲线</span>
              <span class="action-tag" :class="{ active: ragChartType === 'bar' }" @click="ragChartType = 'bar'">柱状</span>
            </div>
            <div class="widget-actions scope-toggle" v-if="isAdmin">
              <span class="action-tag" :class="{ active: ragScope === 'me' }" @click="ragScope = 'me'">个人</span>
              <span class="action-tag" :class="{ active: ragScope === 'all' }" @click="ragScope = 'all'">全体</span>
            </div>
          </div>
          <div class="chart-content">
            <RagTrendChart :chartData="ragSeriesData" :compareData="isAdmin ? ragSeriesCompare : null" :chartType="ragChartType" />
          </div>
        </div>

        <div class="widget widget-rose-pie">
          <div class="widget-header">
            <h3 class="widget-title">通知类型分布</h3>
            <div class="widget-actions" v-if="isAdmin">
              <span class="action-tag" :class="{ active: noticeScope === 'me' }" @click="noticeScope = 'me'">个人</span>
              <span class="action-tag" :class="{ active: noticeScope === 'all' }" @click="noticeScope = 'all'">全体</span>
            </div>
          </div>
          <div class="chart-content">
            <NoticeTypeRoseChart :chartData="noticeChartData" />
          </div>
        </div>
      </div>

      <div class="col-center">
        <div class="center-grid">
          <div class="widget widget-time-curve span-2">
            <div class="widget-header">
              <h3 class="widget-title">节省时间趋势</h3>
              <div class="widget-actions">
                <span class="action-tag" :class="{ active: timeChartType === 'line' }" @click="timeChartType = 'line'">曲线</span>
                <span class="action-tag" :class="{ active: timeChartType === 'bar' }" @click="timeChartType = 'bar'">柱状</span>
              </div>
              <div class="widget-actions scope-toggle" v-if="isAdmin">
                <span class="action-tag" :class="{ active: timeScope === 'me' }" @click="timeScope = 'me'">个人</span>
                <span class="action-tag" :class="{ active: timeScope === 'all' }" @click="timeScope = 'all'">全体</span>
              </div>
            </div>
            <div class="chart-content">
              <TimeSavedChart
                :chartData="timeSeriesData"
                :compareData="isAdmin ? timeSeriesCompare : null"
                :chartType="timeChartType"
              />
            </div>
          </div>

          <div class="widget widget-vector-scatter">
            <div class="widget-header">
              <h3 class="widget-title">向量散点评估</h3>
              <div class="widget-actions scope-toggle" v-if="isAdmin">
                <span class="action-tag" :class="{ active: vectorScope === 'me' }" @click="vectorScope = 'me'">个人</span>
                <span class="action-tag" :class="{ active: vectorScope === 'all' }" @click="vectorScope = 'all'">全体</span>
              </div>
            </div>
            <div class="chart-content">
              <VectorScatterChart :chartData="vectorScatterData" />
            </div>
          </div>

          <div class="widget widget-materials-block">
            <div class="widget-header">
              <h3 class="widget-title">高频材料分析</h3>
              <div class="widget-actions">
                <span class="action-tag" :class="{ active: materialsChartType === 'pie' }" @click="materialsChartType = 'pie'">饼图</span>
                <span class="action-tag" :class="{ active: materialsChartType === 'scatter' }" @click="materialsChartType = 'scatter'">点云</span>
                <span class="action-tag" :class="{ active: materialsChartType === 'wordCloud' }" @click="materialsChartType = 'wordCloud'">词云</span>
              </div>
              <div class="widget-actions scope-toggle" v-if="isAdmin">
                <span class="action-tag" :class="{ active: materialsScope === 'me' }" @click="materialsScope = 'me'">个人</span>
                <span class="action-tag" :class="{ active: materialsScope === 'all' }" @click="materialsScope = 'all'">全体</span>
              </div>
            </div>
            <div class="chart-content">
              <MaterialsPieChart v-if="materialsChartType === 'pie'" :chartData="materialsChartData" />
              <MaterialsScatterChart v-else-if="materialsChartType === 'scatter'" :chartData="materialsChartData" />
              <MaterialsWordCloud v-else :chartData="materialsChartData" />
            </div>
          </div>
        </div>
      </div>

      <div class="col-right">
        <div class="widget widget-time-cards">
          <div v-if="isAdmin" class="time-cards-grid">
            <div class="time-card-grid card-personal-avg">
              <span class="card-label">个人平均节省时间</span>
              <span class="card-value">{{ statsData?.avg_time_saved_minutes || 0 }} <small>分钟/篇</small></span>
            </div>
            <div class="time-card-grid card-personal-total">
              <span class="card-label">个人总计节省时间</span>
              <span class="card-value">{{ statsData?.total_time_saved_minutes || 0 }} <small>分钟</small></span>
            </div>
            <div class="time-card-grid card-all-avg">
              <span class="card-label">全体用户平均节省时间</span>
              <span class="card-value">{{ statsAll?.avg_time_saved_minutes || 0 }} <small>分钟/篇</small></span>
            </div>
            <div class="time-card-grid card-all-total">
              <span class="card-label">全体用户总计节省时间</span>
              <span class="card-value">{{ statsAll?.total_time_saved_minutes || 0 }} <small>分钟</small></span>
            </div>
          </div>
          <div v-else class="time-cards-container">
            <div class="time-card card-bottom">
              <span class="card-label">总计节省时间</span>
              <span class="card-value">{{ statsData?.total_time_saved_minutes || 0 }} <small>分钟</small></span>
            </div>
            <div class="time-card card-top">
              <span class="card-label">平均节省时间</span>
              <span class="card-value">{{ statsData?.avg_time_saved_minutes || 0 }} <small>分钟/篇</small></span>
            </div>
          </div>
        </div>

        <div class="widget widget-difficulty-bar">
          <div class="widget-header">
            <h3 class="widget-title">通知难度评估</h3>
            <div class="widget-actions scope-toggle" v-if="isAdmin">
              <span class="action-tag" :class="{ active: difficultyScope === 'me' }" @click="difficultyScope = 'me'">个人</span>
              <span class="action-tag" :class="{ active: difficultyScope === 'all' }" @click="difficultyScope = 'all'">全体</span>
            </div>
          </div>
          <div class="chart-content">
            <DifficultyBarChart :chartData="difficultyChartData" />
          </div>
        </div>

        <div class="widget widget-recent-history">
          <h3 class="widget-title">最近处理</h3>
          <div class="history-content" v-if="recentHistory">
            <div class="mock-history-item">
              <span class="time">{{ formatDate(recentHistory.created_time) }}</span>
              <p class="text">{{ recentHistory.handling_matter || formatName(recentHistory.original_text) }}</p>
              <div class="history-tags">
                <span class="h-tag">{{ recentHistory.target_audience || '未知对象' }}</span>
              </div>
            </div>
          </div>
          <div class="chart-placeholder" v-else>暂无历史记录</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import PolicyTitle from '@/components/common/PolicyTitle.vue';
import AgentLoader from '@/components/ui/AgentLoader.vue';
import { useUserStore } from '@/stores/auth.js';
import { apiClient, API_ROUTES } from '@/router/api_routes';
import TimeSavedChart from '@/components/Analysis/TimeSavedChart.vue';
import NoticeTypeRoseChart from '@/components/Analysis/NoticeTypeRoseChart.vue';
import MaterialsPieChart from '@/components/Analysis/MaterialsPieChart.vue';
import MaterialsScatterChart from '@/components/Analysis/MaterialsScatterChart.vue';
import MaterialsWordCloud from '@/components/Analysis/MaterialsWordCloud.vue';
import DifficultyBarChart from '@/components/Analysis/DifficultyBarChart.vue';
import RagTrendChart from '@/components/Analysis/RagTrendChart.vue';
import VectorScatterChart from '@/components/Analysis/VectorScatterChart.vue';

const userStore = useUserStore();
const loading = ref(true);
const statsData = ref(null);
const statsAll = ref(null);
const recentHistory = ref(null);
const isAdmin = computed(() => userStore.isAdmin);

const noticeScope = ref('me');
const timeScope = ref('me');
const materialsScope = ref('me');
const difficultyScope = ref('me');
const ragScope = ref('me');
const vectorScope = ref('me');

const timeChartType = ref('line');
const materialsChartType = ref('scatter');
const ragChartType = ref('line');

const noticeChartData = computed(() => {
  if (noticeScope.value === 'all' && statsAll.value) return statsAll.value.notice_type_distribution;
  return statsData.value?.notice_type_distribution || {};
});

const timeSeriesData = computed(() => {
  if (timeScope.value === 'all' && statsAll.value) return statsAll.value.time_saved_distribution;
  return statsData.value?.time_saved_distribution || {};
});

const timeSeriesCompare = computed(() => {
  if (!statsAll.value) return null;
  return timeScope.value === 'me' ? (statsAll.value.time_saved_distribution || {}) : null;
});

const materialsChartData = computed(() => {
  if (materialsScope.value === 'all' && statsAll.value) return statsAll.value.materials_freq;
  return statsData.value?.materials_freq || {};
});

const difficultyChartData = computed(() => {
  if (difficultyScope.value === 'all' && statsAll.value) return statsAll.value.complexity_distribution;
  return statsData.value?.complexity_distribution || {};
});

const ragSeriesData = computed(() => {
  if (ragScope.value === 'all' && statsAll.value) return statsAll.value.rag_series || {};
  return statsData.value?.rag_series || {};
});

const ragSeriesCompare = computed(() => null);

const vectorScatterData = computed(() => {
  if (vectorScope.value === 'all' && statsAll.value) return statsAll.value.vector_scatter || [];
  return statsData.value?.vector_scatter || [];
});

const formatDate = (dateString) => {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return `${date.getMonth() + 1}-${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
};

const formatName = (text) => {
  if (!text) return '未命名文档';
  const cleanText = text.replace(/\s+/g, ' ');
  return cleanText.length > 20 ? `${cleanText.substring(0, 20)}...` : cleanText;
};

onMounted(async () => {
  if (!userStore.token) {
    alert('请先登录查看数据分析');
    loading.value = false;
    return;
  }

  try {
    const requests = [apiClient.get(API_ROUTES.ANALYSIS_ME)];
    if (isAdmin.value) {
      requests.push(apiClient.get(API_ROUTES.ADMIN_ANALYSIS_ALL));
    }

    const [meRes, allRes] = await Promise.all(requests);
    statsData.value = meRes.data;
    if (allRes) {
      statsAll.value = allRes.data;
    }

    const historyRes = await apiClient.get(API_ROUTES.CHAT_MESSAGE, { params: { limit: 1 } });
    if (historyRes.data?.length) {
      recentHistory.value = historyRes.data[0];
    }
  } catch (error) {
    console.error('获取统计数据失败:', error);
  } finally {
    setTimeout(() => {
      loading.value = false;
    }, 500);
  }
});
</script>

<style scoped>
.dashboard-container {
  padding: 14px 30px 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.header-section {
  margin: -4px 0 10px;
}

.loading-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid color-mix(in srgb, var(--border-color) 78%, transparent);
  border-radius: 50%;
  border-top-color: var(--color-primary);
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.dashboard-grid {
  flex: 1;
  display: grid;
  grid-template-columns: 2.8fr 4.4fr 2.8fr;
  gap: 20px;
  min-height: 0;
}

.col-left,
.col-center,
.col-right {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
}

.center-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  grid-template-rows: 1.2fr 1fr;
  gap: 20px;
  flex: 1;
  min-height: 0;
}

.center-grid .span-2 {
  grid-column: span 2;
}

.col-right {
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.col-right::-webkit-scrollbar {
  display: none;
}

.widget {
  background: var(--card-bg);
  border-radius: 0;
  box-shadow: none;
  border: 1px solid var(--border-color);
  border-top: 3px solid var(--color-primary);
  padding: 16px;
  display: flex;
  flex-direction: column;
  position: relative;
  transition: border-color 0.3s ease, background 0.3s ease;
}

.widget-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
  flex-shrink: 0;
  flex-wrap: wrap;
  gap: 8px;
}

.widget-title {
  font-size: 16px;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
  letter-spacing: 1px;
}

.widget-actions {
  display: flex;
  gap: 5px;
  background: color-mix(in srgb, var(--color-primary) 8%, var(--card-bg));
  border: 1px solid color-mix(in srgb, var(--color-primary) 14%, var(--border-color));
  padding: 4px;
  border-radius: 8px;
  z-index: 10;
}

.widget-actions.scope-toggle {
  background: transparent;
  border-color: transparent;
  padding: 0;
}

.action-tag {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 6px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: background 0.2s ease, color 0.2s ease, transform 0.2s ease;
}

.action-tag:hover {
  color: var(--text-primary);
  background: color-mix(in srgb, var(--color-primary) 12%, transparent);
}

.action-tag.active {
  background: var(--color-primary);
  color: #fff;
  font-weight: 700;
}

.chart-placeholder {
  flex: 1;
  background: color-mix(in srgb, var(--border-color) 18%, var(--card-bg));
  border: 1px dashed color-mix(in srgb, var(--text-secondary) 18%, var(--border-color));
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  font-size: 14px;
  margin-top: 10px;
}

.chart-content {
  flex: 1;
  width: 100%;
  height: 100%;
  min-height: 150px;
}

.widget-time-curve {
  flex: 5;
  min-height: 0;
}

.widget-rose-pie {
  flex: 7;
  min-height: 0;
}

.widget-time-cards {
  padding: 0;
  background: transparent;
  box-shadow: none;
  min-height: 0;
  border: none;
}

.widget-rag-trend,
.widget-vector-scatter,
.widget-materials-block {
  min-height: 0;
}

.widget-difficulty-bar,
.widget-recent-history {
  flex: 1;
  min-height: 0;
}

.time-cards-container {
  width: 100%;
}

.time-cards-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.time-card-grid {
  border-radius: 12px;
  padding: 16px;
  border: 1px solid var(--border-color);
  background: var(--card-bg);
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 100px;
}

.card-personal-avg {
  background: color-mix(in srgb, var(--color-primary) 10%, var(--card-bg));
}

.card-personal-total {
  background: linear-gradient(160deg, color-mix(in srgb, var(--color-primary-dark) 82%, #0f1116), color-mix(in srgb, var(--color-primary) 62%, #151922));
  color: #fff;
}

.card-all-avg {
  background: color-mix(in srgb, var(--color-accent-cool) 12%, var(--card-bg));
}

.card-all-total {
  background: linear-gradient(160deg, color-mix(in srgb, var(--color-accent-cool) 70%, #0f1720), color-mix(in srgb, var(--color-accent-mint) 44%, #12202b));
  color: #fff;
}

.time-card-grid .card-label {
  font-size: 12px;
  font-weight: 700;
}

.time-card-grid .card-value {
  font-size: 22px;
  font-weight: 900;
}

.time-card {
  position: relative;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  box-shadow: none;
  transition: border-color 0.22s ease, box-shadow 0.22s ease, transform 0.22s ease;
  border: 1px solid color-mix(in srgb, var(--color-primary) 14%, var(--border-color));
}

.card-bottom {
  background: linear-gradient(160deg, color-mix(in srgb, var(--color-primary-dark) 84%, #0f1116), color-mix(in srgb, var(--color-accent-cool) 30%, #151922));
  color: #fff;
}

.card-bottom .card-label {
  color: rgba(255, 255, 255, 0.72);
}

.card-top {
  background: linear-gradient(145deg, color-mix(in srgb, var(--color-primary) 80%, #ffffff), color-mix(in srgb, var(--color-secondary) 62%, #ffffff));
  color: var(--text-primary);
  border: 1px solid color-mix(in srgb, var(--color-primary) 18%, var(--border-color));
}

.time-cards-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
  height: auto;
  min-height: auto;
}

.time-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 24px color-mix(in srgb, var(--color-primary) 14%, transparent);
}

.card-label {
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 8px;
}

.card-value {
  font-size: 32px;
  font-weight: 900;
  line-height: 1;
}

.card-value small {
  font-size: 14px;
  font-weight: 400;
}

.history-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  margin-top: 10px;
}

.mock-history-item {
  background: color-mix(in srgb, var(--color-primary) 5%, var(--card-bg));
  padding: 15px;
  border-radius: 12px;
  border: 1px solid color-mix(in srgb, var(--color-primary) 12%, var(--border-color));
  cursor: pointer;
  transition: all 0.2s ease;
}

.mock-history-item:hover {
  background: var(--card-bg);
  border-color: var(--color-primary);
  box-shadow: 0 4px 12px color-mix(in srgb, var(--color-primary) 12%, transparent);
  transform: translateY(-2px);
}

.mock-history-item .time {
  font-size: 12px;
  color: var(--text-muted);
  display: block;
  margin-bottom: 8px;
}

.mock-history-item .text {
  margin: 0 0 10px;
  font-size: 15px;
  color: var(--text-primary);
  font-weight: 700;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
}

.history-tags {
  display: flex;
}

.h-tag {
  background: color-mix(in srgb, var(--color-primary) 90%, #111111);
  color: #fff;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 11px;
}

@media (max-width: 1400px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .col-right {
    overflow: visible;
  }
}
</style>
