<template>
  <div class="admin-page">
    <div class="admin-header">
      <div class="header-left">
        <PolicyTitle title="管理员控制台" />
        <span class="live-badge" :class="{ connected: streamConnected }">
          {{ streamConnected ? '实时监测中' : '实时连接断开' }}
        </span>
      </div>
      <button class="refresh-btn" @click="loadAll">刷新</button>
    </div>

    <div v-if="!isAdmin" class="no-permission">无权限访问</div>
    <template v-else>
      <div class="stats-row">
        <div class="stat-card stat-card--yellow">
          <div class="stat-icon-circle" style="background:#f9a825">
            <svg viewBox="0 0 24 24" width="20" height="20" stroke="#f57f17" stroke-width="2" fill="none"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
          </div>
          <div class="stat-text">
            <span class="stat-num">{{ stats.total_users ?? '-' }}</span>
            <span class="stat-label">注册用户</span>
          </div>
        </div>
        <div class="stat-card stat-card--blue">
          <div class="stat-icon-circle" style="background:#1565c0">
            <svg viewBox="0 0 24 24" width="20" height="20" stroke="#0d47a1" stroke-width="2" fill="none"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
          </div>
          <div class="stat-text">
            <span class="stat-num">{{ stats.total_messages ?? '-' }}</span>
            <span class="stat-label">总解析次数</span>
          </div>
        </div>
        <div class="stat-card stat-card--green">
          <div class="stat-icon-circle" style="background:#2e7d32">
            <svg viewBox="0 0 24 24" width="20" height="20" stroke="#1b5e20" stroke-width="2" fill="none"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
          </div>
          <div class="stat-text">
            <span class="stat-num">{{ stats.active_users ?? '-' }}</span>
            <span class="stat-label">活跃用户</span>
          </div>
        </div>
      </div>

      <div class="time-cards-row">
        <div class="time-card personal">
          <span class="tc-label">个人平均节省</span>
          <span class="tc-value">{{ myStats?.avg_time_saved_minutes || 0 }} <small>分钟/篇</small></span>
        </div>
        <div class="time-card personal">
          <span class="tc-label">个人总计节省</span>
          <span class="tc-value">{{ myStats?.total_time_saved_minutes || 0 }} <small>分钟</small></span>
        </div>
        <div class="time-card global">
          <span class="tc-label">全体平均节省</span>
          <span class="tc-value">{{ allStats?.avg_time_saved_minutes || 0 }} <small>分钟/篇</small></span>
        </div>
        <div class="time-card global">
          <span class="tc-label">全体总计节省</span>
          <span class="tc-value">{{ allStats?.total_time_saved_minutes || 0 }} <small>分钟</small></span>
        </div>
      </div>

      <div class="section">
        <div class="section-label-row">
          <span class="section-label">节省时间趋势</span>
          <div class="toggle-group">
            <span class="action-tag" :class="{ active: timeChartType === 'line' }" @click="timeChartType = 'line'">曲线</span>
            <span class="action-tag" :class="{ active: timeChartType === 'bar' }" @click="timeChartType = 'bar'">柱状</span>
          </div>
        </div>
        <div ref="timeChartRef" class="chart-area"></div>
      </div>

      <div class="section">
        <div class="section-label-row">
          <span class="section-label">分布分析</span>
          <div class="toggle-group">
            <span class="action-tag" :class="{ active: distScope === 'personal' }" @click="distScope = 'personal'">个人</span>
            <span class="action-tag" :class="{ active: distScope === 'all' }" @click="distScope = 'all'">全体</span>
          </div>
        </div>
        <div class="dist-grid">
          <div>
            <div class="chart-sub-label">通知类型分布</div>
            <div ref="roseChartRef" class="chart-area-sm"></div>
          </div>
          <div>
            <div class="chart-sub-label">高频材料分析</div>
            <div ref="materialsComboChartRef" class="chart-area-sm"></div>
          </div>
          <div>
            <div class="chart-sub-label">核心材料 Top5</div>
            <div ref="barChartRef" class="chart-area-sm"></div>
          </div>
          <div>
            <div class="chart-sub-label">通知难度评估</div>
            <div ref="diffChartRef" class="chart-area-sm"></div>
          </div>
        </div>
      </div>

      <div class="section">
        <div class="section-label-row">
          <span class="section-label">用户管理</span>
        </div>
        <div v-if="usersLoading" class="loading-text">加载中...</div>
        <table v-else class="user-table">
          <thead>
            <tr>
              <th>头像</th><th>UID</th><th>用户名</th><th>邮箱</th><th>验证</th><th>注册时间</th><th>身份</th><th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.uid">
              <td>
                <img v-if="u.avatar_url" :src="u.avatar_url" class="user-avatar-thumb" alt="avatar" />
                <div v-else class="avatar-placeholder-sm">
                  <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                </div>
              </td>
              <td>{{ u.uid }}</td>
              <td>{{ u.uname }}</td>
              <td>{{ u.email }}</td>
              <td>{{ u.email_verified ? '已验证' : '未验证' }}</td>
              <td>{{ u.created_time?.slice(0, 10) }}</td>
              <td>
                <span :class="u.role === 'admin' ? 'badge-admin' : u.role === 'certified' ? 'badge-certified' : 'badge-user'">
                  {{ u.role === 'admin' ? '管理员' : u.role === 'certified' ? '认证主体' : '普通用户' }}
                </span>
              </td>
              <td class="action-cell">
                <button class="tbl-btn" @click="toggleAdmin(u.uid)" :disabled="u.uid === selfUid">
                  {{ u.role === 'admin' ? '撤销管理员' : '设为管理员' }}
                </button>
                <button class="tbl-btn danger" @click="deleteUser(u.uid)" :disabled="u.uid === selfUid">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="section">
        <span class="section-label">各用户解析量</span>
        <div class="bar-list">
          <div v-for="item in stats.user_message_counts || []" :key="item.user_id" class="bar-row">
            <span class="bar-uid">UID {{ item.user_id }}</span>
            <div class="bar-track">
              <div class="bar-fill" :style="{ width: barWidth(item.count) }"></div>
            </div>
            <span class="bar-count">{{ item.count }}</span>
          </div>
        </div>
      </div>

      <!-- 民意评议分析 -->
      <div class="section">
        <div class="section-label-row">
          <span class="section-label">民意评议分析</span>
        </div>
        <div class="opinion-overview">
          <div class="ov-mini" v-for="card in opinionCards" :key="card.label" :style="{'--ac': card.color}">
            <span class="ov-mini-val">{{ card.value }}</span>
            <span class="ov-mini-label">{{ card.label }}</span>
          </div>
        </div>
        <div class="dist-grid">
          <div>
            <div class="chart-sub-label">评议类型分布</div>
            <div ref="opTypePieRef" class="chart-area-sm"></div>
          </div>
          <div>
            <div class="chart-sub-label">评分分布</div>
            <div ref="opRatingBarRef" class="chart-area-sm"></div>
          </div>
          <div>
            <div class="chart-sub-label">用户角色分布</div>
            <div ref="rolePieRef" class="chart-area-sm"></div>
          </div>
          <div>
            <div class="chart-sub-label">热词 Top20</div>
            <div class="hot-words">
              <span v-for="w in (opinionStats?.hot_words || []).slice(0,20)" :key="w.word"
                class="hot-word" :style="{ fontSize: Math.max(11, Math.min(20, 11 + w.count)) + 'px' }">
                {{ w.word }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 政务文件状态 -->
      <div class="section">
        <div class="section-label-row">
          <span class="section-label">政务文件状态</span>
        </div>
        <div class="doc-status-row">
          <div class="ds-card" style="--ac:#27ae60">
            <span class="ds-val">{{ opinionStats?.approved_docs ?? '-' }}</span>
            <span class="ds-label">已通过</span>
          </div>
          <div class="ds-card" style="--ac:#e67e22">
            <span class="ds-val">{{ opinionStats?.pending_docs ?? '-' }}</span>
            <span class="ds-label">待审核</span>
          </div>
          <div class="ds-card" style="--ac:#2980b9">
            <span class="ds-val">{{ opinionStats?.total_docs ?? '-' }}</span>
            <span class="ds-label">总文件数</span>
          </div>
        </div>
      </div>

      <!-- 用户IP地理分布 -->
      <div class="section">
        <div class="section-label-row">
          <span class="section-label">用户IP地理分布</span>
        </div>
        <div ref="chinaMapRef" class="china-map-area"></div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue';
import PolicyTitle from '@/components/common/PolicyTitle.vue';
import * as echarts from 'echarts/core';
import { BarChart, LineChart, PieChart } from 'echarts/charts';
import { GridComponent, LegendComponent, TitleComponent, TooltipComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { apiClient, API_ROUTES } from '@/router/api_routes.js';
import { useUserStore } from '@/stores/auth.js';

echarts.use([LineChart, BarChart, PieChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent, CanvasRenderer]);

const userStore = useUserStore();
const isAdmin = computed(() => userStore.user?.is_admin);
const selfUid = computed(() => userStore.user?.uid);

const users = ref([]);
const stats = ref({});
const myStats = ref(null);
const allStats = ref(null);
const usersLoading = ref(true);
const timeChartType = ref('line');
const distScope = ref('personal');
const streamConnected = ref(false);

const timeChartRef = ref(null);
const roseChartRef = ref(null);
const materialsComboChartRef = ref(null);
const barChartRef = ref(null);
const diffChartRef = ref(null);
const opTypePieRef = ref(null);
const opRatingBarRef = ref(null);
const rolePieRef = ref(null);
const chinaMapRef = ref(null);

const opinionStats = ref(null);
const roleDist = ref(null);
const geoData = ref([]);

let timeChart = null;
let roseChart = null;
let materialsComboChart = null;
let barChart = null;
let diffChart = null;
let opTypePieChart = null;
let opRatingBarChart = null;
let rolePieChart = null;
let chinaMapChart = null;
let statsEventSource = null;

const getDistData = () => (distScope.value === 'personal' ? myStats.value : allStats.value);

async function loadAll() {
  usersLoading.value = true;
  try {
    const [usersRes, statsRes, myRes, allRes, opRes, roleRes, geoRes] = await Promise.all([
      apiClient.get(API_ROUTES.ADMIN_USERS),
      apiClient.get(API_ROUTES.ADMIN_STATS),
      apiClient.get(API_ROUTES.ANALYSIS_ME),
      apiClient.get(API_ROUTES.ADMIN_ANALYSIS_ALL),
      apiClient.get(API_ROUTES.ADMIN_OPINION_STATS),
      apiClient.get(API_ROUTES.ADMIN_USER_ROLE_DIST),
      apiClient.get(API_ROUTES.ADMIN_USER_GEO),
    ]);
    users.value = usersRes.data;
    stats.value = statsRes.data;
    myStats.value = myRes.data;
    allStats.value = allRes.data;
    opinionStats.value = opRes.data;
    roleDist.value = roleRes.data;
    geoData.value = geoRes.data.geo_dist || [];
    await nextTick();
    renderAllCharts();
    connectRealtimeStream();
  } catch (e) {
    console.warn('管理员数据加载失败', e);
  } finally {
    usersLoading.value = false;
  }
}

function connectRealtimeStream() {
  if (!userStore.token || statsEventSource) return;
  const url = `/api${API_ROUTES.ADMIN_STATS_STREAM}?token=${encodeURIComponent(userStore.token)}`;
  statsEventSource = new EventSource(url);
  statsEventSource.onopen = () => {
    streamConnected.value = true;
  };
  statsEventSource.onmessage = (event) => {
    try {
      const payload = JSON.parse(event.data);
      stats.value = payload;
    } catch (error) {
      console.warn('实时数据解析失败', error);
    }
  };
  statsEventSource.onerror = () => {
    streamConnected.value = false;
    statsEventSource?.close();
    statsEventSource = null;
  };
}

function renderAllCharts() {
  renderTimeChart();
  renderDistributionCharts();
  renderOpinionCharts();
  renderChinaMap();
}

function renderTimeChart() {
  if (!timeChartRef.value) return;
  if (!timeChart) timeChart = echarts.init(timeChartRef.value);
  const myDist = myStats.value?.time_saved_distribution || {};
  const allDist = allStats.value?.time_saved_distribution || {};
  const keys = Array.from(new Set([...Object.keys(myDist), ...Object.keys(allDist)]));
  timeChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['个人节省', '全体节省'], top: 0 },
    grid: { top: 36, bottom: 24, left: 40, right: 20 },
    xAxis: { type: 'category', data: keys, axisLabel: { fontSize: 10 } },
    yAxis: { type: 'value', name: '分钟' },
    series: [
      {
        name: '个人节省',
        type: timeChartType.value,
        data: keys.map((key) => myDist[key] || 0),
        itemStyle: { color: '#c0392b' },
        smooth: true,
        areaStyle: timeChartType.value === 'line' ? { color: 'rgba(192,57,43,0.1)' } : undefined,
      },
      {
        name: '全体节省',
        type: timeChartType.value,
        data: keys.map((key) => allDist[key] || 0),
        itemStyle: { color: '#2980b9' },
        smooth: true,
        areaStyle: timeChartType.value === 'line' ? { color: 'rgba(41,128,185,0.1)' } : undefined,
      },
    ],
  }, true);
}

function renderDistributionCharts() {
  const distData = getDistData();
  if (!distData) return;

  if (roseChartRef.value) {
    if (!roseChart) roseChart = echarts.init(roseChartRef.value);
    const roseData = Object.entries(distData.notice_type_distribution || {}).map(([name, value]) => ({ name, value }));
    roseChart.setOption({
      color: ['#c0392b', '#e67e22', '#f1c40f', '#7f8c8d', '#95a5a6'],
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      series: [{
        type: 'pie',
        roseType: 'radius',
        radius: ['15%', '75%'],
        center: ['50%', '55%'],
        itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
        label: { show: true, formatter: '{b}\n{c}', fontSize: 10 },
        animationType: 'expansion',
        animationEasing: 'cubicOut',
        startAngle: 90,
        clockwise: true,
        data: roseData.sort((a, b) => a.value - b.value),
      }],
    }, true);
  }

  if (materialsComboChartRef.value) {
    if (!materialsComboChart) materialsComboChart = echarts.init(materialsComboChartRef.value);
    const topMaterials = Object.entries(distData.materials_freq || {}).slice(0, 8);
    materialsComboChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['材料频次', '变化曲线'], top: 0, textStyle: { fontSize: 10 } },
      grid: { top: 30, bottom: 35, left: 35, right: 10 },
      xAxis: {
        type: 'category',
        data: topMaterials.map(([name]) => name),
        axisLabel: { interval: 0, rotate: 25, fontSize: 9 },
      },
      yAxis: { type: 'value' },
      series: [
        {
          name: '材料频次',
          type: 'bar',
          barWidth: '42%',
          data: topMaterials.map(([, value]) => value),
          itemStyle: { color: '#c0392b' },
        },
        {
          name: '变化曲线',
          type: 'line',
          smooth: true,
          data: topMaterials.map(([, value]) => value),
          itemStyle: { color: '#2980b9' },
          lineStyle: { width: 2 },
        },
      ],
    }, true);
  }

  if (barChartRef.value) {
    if (!barChart) barChart = echarts.init(barChartRef.value);
    const top5 = Object.entries(distData.materials_freq || {}).sort((a, b) => b[1] - a[1]).slice(0, 5);
    barChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { top: 10, bottom: 30, left: 60, right: 10 },
      xAxis: { type: 'value' },
      yAxis: { type: 'category', data: top5.map((item) => item[0]), axisLabel: { fontSize: 10 } },
      series: [{
        type: 'bar',
        data: top5.map((item) => item[1]),
        itemStyle: {
          color: (params) => ['#c0392b', '#e67e22', '#f1c40f', '#7f8c8d', '#922b21'][params.dataIndex % 5],
        },
      }],
    }, true);
  }

  if (diffChartRef.value) {
    if (!diffChart) diffChart = echarts.init(diffChartRef.value);
    const cd = distData.complexity_distribution || {};
    const cats = [...new Set(Object.keys(cd).map((key) => key.split('-')[0]))];
    const levels = ['高', '中', '低'];
    diffChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: levels, top: 0, textStyle: { fontSize: 10 } },
      grid: { top: 30, bottom: 24, left: 50, right: 10 },
      xAxis: { type: 'category', data: cats, axisLabel: { fontSize: 9 } },
      yAxis: { type: 'value' },
      series: levels.map((level, index) => ({
        name: level,
        type: 'bar',
        stack: 'total',
        data: cats.map((cat) => cd[`${cat}-${level}`] || 0),
        itemStyle: { color: ['#c0392b', '#e67e22', '#27ae60'][index] },
      })),
    }, true);
  }
}

async function renderChinaMap() {
  if (!chinaMapRef.value) return;
  if (!echarts.getMap('china')) {
    try {
      const res = await fetch('https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json');
      const geoJson = await res.json();
      echarts.registerMap('china', geoJson);
    } catch (e) { console.warn('China map load failed', e); return; }
  }
  if (!chinaMapChart) chinaMapChart = echarts.init(chinaMapRef.value);
  const data = geoData.value;
  const max = Math.max(...data.map(d => d.value), 1);
  chinaMapChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} 人' },
    visualMap: {
      min: 0, max,
      left: 'left', bottom: 20,
      text: ['多', '少'],
      inRange: { color: ['#fde8e8', '#c0392b'] },
      textStyle: { fontSize: 11 },
    },
    series: [{
      type: 'map', map: 'china',
      roam: true,
      emphasis: { itemStyle: { areaColor: '#e74c3c' }, label: { show: true } },
      data,
      itemStyle: { borderColor: '#fff', borderWidth: 0.5 },
    }],
  }, true);
}

const opinionCards = computed(() => [
  { label: '总评议数', value: opinionStats.value?.total_opinions ?? '-', color: '#8e44ad' },
  { label: '总文件数', value: opinionStats.value?.total_docs ?? '-', color: '#2980b9' },
  { label: '已通过文件', value: opinionStats.value?.approved_docs ?? '-', color: '#27ae60' },
  { label: '待审核文件', value: opinionStats.value?.pending_docs ?? '-', color: '#e67e22' },
]);

function renderOpinionCharts() {
  const typeMap = { review: '落地评价', correction: '解析纠错', message: '办事留言' };
  const typeDist = opinionStats.value?.type_dist || {};
  if (opTypePieRef.value) {
    if (!opTypePieChart) opTypePieChart = echarts.init(opTypePieRef.value);
    opTypePieChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      color: ['#c0392b', '#2980b9', '#27ae60'],
      series: [{
        type: 'pie', radius: ['35%', '68%'],
        data: Object.entries(typeDist).map(([k, v]) => ({ name: typeMap[k] || k, value: v })),
        label: { fontSize: 11 },
        emphasis: { itemStyle: { shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.2)' } },
      }],
    }, true);
  }
  const ratingDist = opinionStats.value?.rating_dist || {};
  if (opRatingBarRef.value) {
    if (!opRatingBarChart) opRatingBarChart = echarts.init(opRatingBarRef.value);
    opRatingBarChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { top: 10, bottom: 30, left: 36, right: 10 },
      xAxis: { type: 'category', data: ['1星','2星','3星','4星','5星'] },
      yAxis: { type: 'value', minInterval: 1 },
      series: [{
        type: 'bar', barWidth: '50%',
        data: [1,2,3,4,5].map(n => ratingDist[String(n)] || 0),
        itemStyle: {
          color: p => ['#e74c3c','#e67e22','#f1c40f','#2ecc71','#27ae60'][p.dataIndex],
          borderRadius: [4,4,0,0],
        },
      }],
    }, true);
  }
  const roleLabels = { normal: '普通用户', certified: '认证主体', admin: '管理员' };
  const rd = roleDist.value?.role_dist || {};
  if (rolePieRef.value) {
    if (!rolePieChart) rolePieChart = echarts.init(rolePieRef.value);
    rolePieChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      color: ['#bdc3c7', '#c0392b', '#2980b9'],
      series: [{
        type: 'pie', radius: ['35%', '68%'],
        data: Object.entries(rd).map(([k, v]) => ({ name: roleLabels[k] || k, value: v })),
        label: { fontSize: 11 },
        emphasis: { itemStyle: { shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.2)' } },
      }],
    }, true);
  }
}

async function toggleAdmin(uid) {
  try {
    const res = await apiClient.patch(`${API_ROUTES.ADMIN_USERS}/${uid}/toggle-admin`);
    const user = users.value.find((item) => item.uid === uid);
    if (user) user.role = res.data.role;
  } catch (e) {
    console.warn(e);
  }
}

async function deleteUser(uid) {
  if (!confirm('确认删除该用户？此操作不可撤销。')) return;
  try {
    await apiClient.delete(`${API_ROUTES.ADMIN_USERS}/${uid}`);
    users.value = users.value.filter((item) => item.uid !== uid);
  } catch (e) {
    console.warn(e);
  }
}

const maxCount = computed(() => Math.max(...(stats.value.user_message_counts || []).map((item) => item.count), 1));
const barWidth = (count) => `${Math.round((count / maxCount.value) * 100)}%`;

onMounted(() => {
  if (isAdmin.value) loadAll();
});

onUnmounted(() => {
  [timeChart, roseChart, materialsComboChart, barChart, diffChart, opTypePieChart, opRatingBarChart, rolePieChart, chinaMapChart].forEach((chart) => chart?.dispose());
  statsEventSource?.close();
});
</script>

<style scoped>
.admin-page { display: flex; flex-direction: column; gap: 16px; padding: 20px; overflow-y: auto; height: 100%; box-sizing: border-box; }
.admin-header { display: flex; align-items: center; justify-content: space-between; }
.header-left { display: flex; align-items: center; gap: 12px; }
.page-title { font-size: 20px; font-weight: 800; color: #111; margin: 0; }
.live-badge { font-size: 12px; padding: 4px 10px; background: #eee; color: #666; }
.live-badge.connected { background: #c0392b; color: #fff; }
.no-permission { text-align: center; color: #aaa; padding: 60px 0; font-size: 14px; }

.stats-row { display: flex; gap: 12px; }
.stat-card { flex: 1; border-radius: 16px; border: none; padding: 16px; display: flex; align-items: center; gap: 14px; }
.stat-card--yellow { background: #fffde7; }
.stat-card--blue { background: #e3f2fd; }
.stat-card--green { background: #e8f5e9; }
.stat-icon-circle { width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-text { display: flex; flex-direction: column; gap: 4px; }
.stat-num { font-size: 28px; font-weight: 800; color: #111; line-height: 1; }
.stat-label { font-size: 12px; color: #888; }

.time-cards-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.time-card { background: #fff; border: 1px solid #eee; padding: 16px; display: flex; flex-direction: column; gap: 6px; }
.time-card.personal { border-top: 3px solid #c0392b; }
.time-card.global { border-top: 3px solid #2980b9; }
.tc-label { font-size: 11px; color: #888; }
.tc-value { font-size: 22px; font-weight: 800; color: #111; line-height: 1; }
.tc-value small { font-size: 11px; font-weight: 400; color: #aaa; }

.section { background: #fff; border: 1px solid #eee; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
.section-label-row { display: flex; align-items: center; justify-content: space-between; }
.section-label { font-size: 13px; font-weight: 700; color: #111; }
.refresh-btn { background: #c0392b; border: none; border-bottom: 3px solid #922b21; border-radius: 999px; color: #fff; padding: 7px 18px; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.refresh-btn:hover { background: #e74c3c; border-bottom-color: #c0392b; }
.loading-text { color: #aaa; font-size: 13px; }

.toggle-group { display: flex; gap: 4px; }
.action-tag { font-size: 11px; padding: 3px 10px; border-radius: 10px; background: #f0f0f0; color: #666; cursor: pointer; transition: all 0.2s; }
.action-tag.active { background: #c0392b; color: #fff; }

.chart-area { width: 100%; height: 220px; }
.dist-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.chart-sub-label { font-size: 11px; color: #888; font-weight: 600; margin-bottom: 6px; }
.chart-area-sm { width: 100%; height: 180px; }

.user-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.user-table th { text-align: left; padding: 8px 10px; background: #f9f9f9; color: #666; font-weight: 600; border-bottom: 1px solid #eee; }
.user-table td { padding: 8px 10px; border-bottom: 1px solid #f5f5f5; color: #333; vertical-align: middle; }
.badge-admin { background: #c0392b; color: #fff; padding: 2px 8px; font-size: 11px; font-weight: 700; }
.badge-certified { background: #2980b9; color: #fff; padding: 2px 8px; font-size: 11px; font-weight: 700; }
.badge-user { background: #f0f0f0; color: #666; padding: 2px 8px; font-size: 11px; }
.action-cell { display: flex; gap: 6px; }
.tbl-btn { background: #f5f5f5; border: none; padding: 4px 10px; font-size: 11px; cursor: pointer; transition: background 0.2s; }
.tbl-btn:hover { background: #e0e0e0; }
.tbl-btn.danger:hover { background: #c0392b; color: #fff; }
.tbl-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.user-avatar-thumb { width: 28px; height: 28px; border-radius: 50%; object-fit: cover; }
.avatar-placeholder-sm { width: 28px; height: 28px; border-radius: 50%; background: #f0f0f0; display: flex; align-items: center; justify-content: center; color: #bbb; }

.bar-list { display: flex; flex-direction: column; gap: 8px; }
.bar-row { display: flex; align-items: center; gap: 10px; }
.bar-uid { font-size: 12px; color: #888; width: 60px; flex-shrink: 0; }
.bar-track { flex: 1; background: #f5f5f5; height: 12px; }
.bar-fill { height: 100%; background: linear-gradient(to right, #c0392b, #e67e22); transition: width 0.4s; }
.bar-count { font-size: 12px; color: #333; width: 30px; text-align: right; flex-shrink: 0; }

.opinion-overview { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 16px; }
.ov-mini {
  border-left: 3px solid var(--ac);
  background: var(--card-bg, #fff);
  border: 1px solid #eee;
  border-left: 3px solid var(--ac);
  padding: 12px 16px;
  display: flex; flex-direction: column; gap: 4px;
}
.ov-mini-val { font-size: 24px; font-weight: 800; color: var(--ac); line-height: 1; }
.ov-mini-label { font-size: 11px; color: #888; }

.hot-words { display: flex; flex-wrap: wrap; gap: 6px; padding: 8px 0; align-content: flex-start; height: 180px; overflow: hidden; }
.hot-word {
  padding: 2px 8px; border-radius: 12px;
  background: linear-gradient(135deg, rgba(192,57,43,0.08), rgba(41,128,185,0.08));
  color: var(--text-primary, #333); cursor: default;
  transition: transform 0.2s, background 0.2s;
}
.hot-word:hover { transform: scale(1.1); background: rgba(192,57,43,0.15); }

.doc-status-row { display: flex; gap: 12px; }
.ds-card {
  flex: 1; padding: 16px 20px;
  border: 1px solid #eee; border-top: 3px solid var(--ac);
  display: flex; flex-direction: column; gap: 4px;
}
.ds-val { font-size: 28px; font-weight: 800; color: var(--ac); line-height: 1; }
.ds-label { font-size: 12px; color: #888; }

.china-map-area { width: 100%; height: 480px; }
</style>

