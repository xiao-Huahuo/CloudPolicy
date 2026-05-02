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
        <div class="stat-card stat-card--primary">
          <div class="stat-icon stat-icon--primary">
            <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="9" cy="7" r="4"></circle>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
            </svg>
          </div>
          <div class="stat-copy">
            <span class="stat-num">{{ stats.total_users ?? '-' }}</span>
            <span class="stat-label">注册用户</span>
          </div>
        </div>

        <div class="stat-card stat-card--cool">
          <div class="stat-icon stat-icon--cool">
            <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
            </svg>
          </div>
          <div class="stat-copy">
            <span class="stat-num">{{ stats.total_messages ?? '-' }}</span>
            <span class="stat-label">总解析次数</span>
          </div>
        </div>

        <div class="stat-card stat-card--mint">
          <div class="stat-icon stat-icon--mint">
            <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </div>
          <div class="stat-copy">
            <span class="stat-num">{{ stats.active_users ?? '-' }}</span>
            <span class="stat-label">活跃用户</span>
          </div>
        </div>
      </div>

      <div class="time-cards-row">
        <div class="time-card time-card--primary">
          <span class="tc-label">个人平均节省</span>
          <span class="tc-value">{{ myStats?.avg_time_saved_minutes || 0 }} <small>分钟/篇</small></span>
        </div>
        <div class="time-card time-card--primary-dark">
          <span class="tc-label">个人总计节省</span>
          <span class="tc-value">{{ myStats?.total_time_saved_minutes || 0 }} <small>分钟</small></span>
        </div>
        <div class="time-card time-card--cool">
          <span class="tc-label">全体平均节省</span>
          <span class="tc-value">{{ allStats?.avg_time_saved_minutes || 0 }} <small>分钟/篇</small></span>
        </div>
        <div class="time-card time-card--cool-dark">
          <span class="tc-label">全体总计节省</span>
          <span class="tc-value">{{ allStats?.total_time_saved_minutes || 0 }} <small>分钟</small></span>
        </div>
      </div>

      <div class="section">
        <div class="section-head">
          <span class="section-label">政务文件状态</span>
        </div>
        <div class="doc-status-row">
          <div class="metric-card metric-card--mint">
            <span class="metric-value">{{ opinionStats?.approved_docs ?? '-' }}</span>
            <span class="metric-label">已通过</span>
          </div>
          <div class="metric-card metric-card--secondary">
            <span class="metric-value">{{ opinionStats?.pending_docs ?? '-' }}</span>
            <span class="metric-label">待审核</span>
          </div>
          <div class="metric-card metric-card--cool">
            <span class="metric-value">{{ opinionStats?.total_docs ?? '-' }}</span>
            <span class="metric-label">总文件数</span>
          </div>
        </div>
      </div>

      <div class="section">
        <div class="section-head">
          <span class="section-label">节省时间趋势</span>
          <div class="toggle-group">
            <span class="action-tag" :class="{ active: timeChartType === 'line' }" @click="timeChartType = 'line'">曲线</span>
            <span class="action-tag" :class="{ active: timeChartType === 'bar' }" @click="timeChartType = 'bar'">柱状</span>
          </div>
        </div>
        <div ref="timeChartRef" class="chart-area"></div>
      </div>

      <div class="section">
        <div class="section-head">
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
        <div class="section-head">
          <span class="section-label">民意评议分析</span>
        </div>
        <div class="opinion-overview">
          <div v-for="card in opinionCards" :key="card.label" class="metric-card" :class="`metric-card--${card.tone}`">
            <span class="metric-value">{{ card.value }}</span>
            <span class="metric-label">{{ card.label }}</span>
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
              <span
                v-for="(word, index) in (opinionStats?.hot_words || []).slice(0, 20)"
                :key="word.word"
                class="hot-word"
                :class="`hot-word--${['primary', 'secondary', 'cool'][index % 3]}`"
                :style="{ fontSize: `${Math.max(11, Math.min(20, 11 + word.count))}px` }"
              >
                {{ word.word }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="section">
        <div class="section-head">
          <span class="section-label">用户管理</span>
        </div>
        <div v-if="usersLoading" class="loading-text">
          <AgentLoader :size="24" compact :center="false" />
          <span>加载中...</span>
        </div>
        <table v-else class="user-table">
          <thead>
            <tr>
              <th>头像</th>
              <th>UID</th>
              <th>用户名</th>
              <th>邮箱</th>
              <th>验证</th>
              <th>注册时间</th>
              <th>身份</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.uid">
              <td>
                <img v-if="resolveAvatarUrl(user.avatar_url)" :src="resolveAvatarUrl(user.avatar_url)" class="user-avatar-thumb" alt="avatar" />
                <div v-else class="avatar-placeholder-sm">
                  <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                  </svg>
                </div>
              </td>
              <td>{{ user.uid }}</td>
              <td>{{ user.uname }}</td>
              <td>{{ user.email }}</td>
              <td>{{ user.email_verified ? '已验证' : '未验证' }}</td>
              <td>{{ user.created_time?.slice(0, 10) }}</td>
              <td>
                <span :class="user.role === 'admin' ? 'badge-admin' : user.role === 'certified' ? 'badge-certified' : 'badge-user'">
                  {{ user.role === 'admin' ? '管理员' : user.role === 'certified' ? '认证主体' : '普通用户' }}
                </span>
              </td>
              <td class="action-cell">
                <button class="tbl-btn" @click="toggleAdmin(user.uid)" :disabled="user.uid === selfUid">
                  {{ user.role === 'admin' ? '撤销管理员' : '设为管理员' }}
                </button>
                <button class="tbl-btn danger" @click="deleteUser(user.uid)" :disabled="user.uid === selfUid">删除</button>
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

    </template>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue';
import PolicyTitle from '@/components/common/PolicyTitle.vue';
import AgentLoader from '@/components/ui/AgentLoader.vue';
import * as echarts from 'echarts/core';
import { BarChart, LineChart, PieChart } from 'echarts/charts';
import { GridComponent, LegendComponent, TitleComponent, TooltipComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { apiClient, API_ROUTES } from '@/router/api_routes.js';
import { useUserStore } from '@/stores/auth.js';
import { getChartTheme, observeChartAppearance, withAlpha } from '@/utils/chartTheme';
import { resolveAvatarUrl } from '@/utils/avatar.js';
echarts.use([LineChart, BarChart, PieChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent, CanvasRenderer]);

const userStore = useUserStore();
const isAdmin = computed(() => Boolean(userStore.isAdmin));
const selfUid = computed(() => userStore.user?.uid);
const users = ref([]);
const stats = ref({});
const myStats = ref(null);
const allStats = ref(null);
const opinionStats = ref(null);
const roleDist = ref(null);
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
let timeChart = null;
let roseChart = null;
let materialsComboChart = null;
let barChart = null;
let diffChart = null;
let opTypePieChart = null;
let opRatingBarChart = null;
let rolePieChart = null;
let statsEventSource = null;
let themeObserver = null;

const opinionCards = computed(() => [
  { label: '总评议数', value: opinionStats.value?.total_opinions ?? '-', tone: 'primary' },
  { label: '总文件数', value: opinionStats.value?.total_docs ?? '-', tone: 'cool' },
  { label: '已通过文件', value: opinionStats.value?.approved_docs ?? '-', tone: 'mint' },
  { label: '待审核文件', value: opinionStats.value?.pending_docs ?? '-', tone: 'secondary' },
]);

const getDistData = () => (distScope.value === 'personal' ? myStats.value : allStats.value);

async function loadAll() {
  usersLoading.value = true;
  try {
    const [usersRes, statsRes, myRes, allRes, opinionRes, roleRes] = await Promise.all([
      apiClient.get(API_ROUTES.ADMIN_USERS),
      apiClient.get(API_ROUTES.ADMIN_STATS),
      apiClient.get(API_ROUTES.ANALYSIS_ME),
      apiClient.get(API_ROUTES.ADMIN_ANALYSIS_ALL),
      apiClient.get(API_ROUTES.ADMIN_OPINION_STATS),
      apiClient.get(API_ROUTES.ADMIN_USER_ROLE_DIST),
    ]);
    users.value = usersRes.data;
    stats.value = statsRes.data;
    myStats.value = myRes.data;
    allStats.value = allRes.data;
    opinionStats.value = opinionRes.data;
    roleDist.value = roleRes.data;
    await nextTick();
    renderAllCharts();
    connectRealtimeStream();
  } catch (error) {
    console.warn('管理员数据加载失败', error);
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
      stats.value = JSON.parse(event.data);
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
}

function renderTimeChart() {
  if (!timeChartRef.value) return;
  const theme = getChartTheme();
  if (!timeChart) timeChart = echarts.init(timeChartRef.value);

  const myDist = myStats.value?.time_saved_distribution || {};
  const allDist = allStats.value?.time_saved_distribution || {};
  const keys = Array.from(new Set([...Object.keys(myDist), ...Object.keys(allDist)]));
  const area = (color) => (timeChartType.value === 'line'
    ? {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: withAlpha(color, theme.dark ? 0.32 : 0.18) },
          { offset: 1, color: withAlpha(color, 0) },
        ]),
      }
    : undefined);

  timeChart.setOption({
    tooltip: { trigger: 'axis', backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.textPrimary } },
    legend: { data: ['个人节省', '全体节省'], top: 0, textStyle: { color: theme.textSecondary } },
    grid: { top: 36, bottom: 24, left: 40, right: 20 },
    xAxis: { type: 'category', data: keys, axisLabel: { fontSize: 10, color: theme.textSecondary }, axisLine: { lineStyle: { color: theme.axisLine } }, axisTick: { show: false } },
    yAxis: { type: 'value', name: '分钟', nameTextStyle: { color: theme.textMuted }, axisLabel: { color: theme.textSecondary }, splitLine: { lineStyle: { color: theme.splitLine, type: 'dashed' } } },
    series: [
      { name: '个人节省', type: timeChartType.value, data: keys.map((key) => myDist[key] || 0), itemStyle: { color: theme.primary }, lineStyle: { color: theme.primary, width: 2.5 }, smooth: true, areaStyle: area(theme.primary), barMaxWidth: 24 },
      { name: '全体节省', type: timeChartType.value, data: keys.map((key) => allDist[key] || 0), itemStyle: { color: theme.accentCool }, lineStyle: { color: theme.accentCool, width: 2.5 }, smooth: true, areaStyle: area(theme.accentCool), barMaxWidth: 24 },
    ],
  }, true);
}

function renderDistributionCharts() {
  const distData = getDistData();
  if (!distData) return;
  const theme = getChartTheme();

  if (roseChartRef.value) {
    if (!roseChart) roseChart = echarts.init(roseChartRef.value);
    const roseData = Object.entries(distData.notice_type_distribution || {}).map(([name, value]) => ({ name, value }));
    roseChart.setOption({
      color: theme.palette,
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)', backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.textPrimary } },
      series: [{ type: 'pie', roseType: 'radius', radius: ['15%', '75%'], center: ['50%', '55%'], itemStyle: { borderRadius: 6, borderColor: 'transparent', borderWidth: 0 }, label: { show: true, formatter: '{b}\n{c}', fontSize: 10, color: theme.dark ? '#fff' : theme.textPrimary }, startAngle: 90, clockwise: true, data: roseData.sort((a, b) => a.value - b.value) }],
    }, true);
  }

  if (materialsComboChartRef.value) {
    if (!materialsComboChart) materialsComboChart = echarts.init(materialsComboChartRef.value);
    const topMaterials = Object.entries(distData.materials_freq || {}).slice(0, 8);
    materialsComboChart.setOption({
      tooltip: { trigger: 'axis', backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.textPrimary } },
      legend: { data: ['材料频次', '变化曲线'], top: 0, textStyle: { fontSize: 10, color: theme.textSecondary } },
      grid: { top: 30, bottom: 35, left: 35, right: 10 },
      xAxis: { type: 'category', data: topMaterials.map(([name]) => name), axisLabel: { interval: 0, rotate: 25, fontSize: 9, color: theme.textSecondary }, axisLine: { lineStyle: { color: theme.axisLine } } },
      yAxis: { type: 'value', axisLabel: { color: theme.textSecondary }, splitLine: { lineStyle: { color: theme.splitLine, type: 'dashed' } } },
      series: [
        { name: '材料频次', type: 'bar', barWidth: '42%', data: topMaterials.map(([, value]) => value), itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: theme.primary }, { offset: 1, color: theme.secondary }]), borderRadius: [6, 6, 0, 0] } },
        { name: '变化曲线', type: 'line', smooth: true, data: topMaterials.map(([, value]) => value), itemStyle: { color: theme.accentCool }, lineStyle: { color: theme.accentCool, width: 2 } },
      ],
    }, true);
  }

  if (barChartRef.value) {
    if (!barChart) barChart = echarts.init(barChartRef.value);
    const top5 = Object.entries(distData.materials_freq || {}).sort((a, b) => b[1] - a[1]).slice(0, 5);
    barChart.setOption({
      tooltip: { trigger: 'axis', backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.textPrimary } },
      grid: { top: 10, bottom: 30, left: 60, right: 10 },
      xAxis: { type: 'value', axisLabel: { color: theme.textSecondary }, splitLine: { lineStyle: { color: theme.splitLine, type: 'dashed' } } },
      yAxis: { type: 'category', data: top5.map((item) => item[0]), axisLabel: { fontSize: 10, color: theme.textSecondary }, axisLine: { lineStyle: { color: theme.axisLine } }, axisTick: { show: false } },
      series: [{ type: 'bar', data: top5.map((item) => item[1]), itemStyle: { color: (params) => theme.palette[params.dataIndex % theme.palette.length], borderRadius: [0, 6, 6, 0] } }],
    }, true);
  }

  if (diffChartRef.value) {
    if (!diffChart) diffChart = echarts.init(diffChartRef.value);
    const complexity = distData.complexity_distribution || {};
    const categories = [...new Set(Object.keys(complexity).map((key) => key.split('-')[0]))];
    const levels = [
      { label: '高', color: theme.primary },
      { label: '中', color: theme.secondary },
      { label: '低', color: theme.accentCool },
    ];
    diffChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.textPrimary } },
      legend: { data: levels.map((level) => level.label), top: 0, textStyle: { fontSize: 10, color: theme.textSecondary } },
      grid: { top: 30, bottom: 24, left: 50, right: 10 },
      xAxis: { type: 'category', data: categories, axisLabel: { fontSize: 9, color: theme.textSecondary }, axisLine: { lineStyle: { color: theme.axisLine } } },
      yAxis: { type: 'value', axisLabel: { color: theme.textSecondary }, splitLine: { lineStyle: { color: theme.splitLine, type: 'dashed' } } },
      series: levels.map((level) => ({ name: level.label, type: 'bar', stack: 'total', data: categories.map((category) => complexity[`${category}-${level.label}`] || 0), itemStyle: { color: level.color } })),
    }, true);
  }
}

function renderOpinionCharts() {
  const theme = getChartTheme();
  const typeMap = { review: '落地评价', correction: '解析纠错', message: '办事留言' };
  const typeDist = opinionStats.value?.type_dist || {};

  if (opTypePieRef.value) {
    if (!opTypePieChart) opTypePieChart = echarts.init(opTypePieRef.value);
    opTypePieChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)', backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.textPrimary } },
      color: [theme.primary, theme.secondary, theme.accentCool],
      series: [{ type: 'pie', radius: ['35%', '68%'], data: Object.entries(typeDist).map(([key, value]) => ({ name: typeMap[key] || key, value })), label: { fontSize: 11, color: theme.textSecondary }, itemStyle: { borderColor: 'transparent', borderWidth: 0 }, emphasis: { itemStyle: { shadowBlur: 8, shadowColor: withAlpha(theme.primaryDark, 0.2) } } }],
    }, true);
  }

  const ratingDist = opinionStats.value?.rating_dist || {};
  if (opRatingBarRef.value) {
    if (!opRatingBarChart) opRatingBarChart = echarts.init(opRatingBarRef.value);
    opRatingBarChart.setOption({
      tooltip: { trigger: 'axis', backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.textPrimary } },
      grid: { top: 10, bottom: 30, left: 36, right: 10 },
      xAxis: { type: 'category', data: ['1星', '2星', '3星', '4星', '5星'], axisLabel: { color: theme.textSecondary }, axisLine: { lineStyle: { color: theme.axisLine } }, axisTick: { show: false } },
      yAxis: { type: 'value', minInterval: 1, axisLabel: { color: theme.textSecondary }, splitLine: { lineStyle: { color: theme.splitLine, type: 'dashed' } } },
      series: [{ type: 'bar', barWidth: '50%', data: [1, 2, 3, 4, 5].map((num) => ratingDist[String(num)] || 0), itemStyle: { color: (params) => [theme.primaryLight, theme.primary, theme.secondary, theme.accentCool, theme.accentMint][params.dataIndex], borderRadius: [4, 4, 0, 0] } }],
    }, true);
  }

  const roleLabels = { normal: '普通用户', certified: '认证主体', admin: '管理员' };
  const roles = roleDist.value?.role_dist || {};
  if (rolePieRef.value) {
    if (!rolePieChart) rolePieChart = echarts.init(rolePieRef.value);
    rolePieChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)', backgroundColor: theme.tooltipBg, borderColor: theme.tooltipBorder, textStyle: { color: theme.textPrimary } },
      color: [withAlpha(theme.textSecondary, 0.6), theme.secondary, theme.primary],
      series: [{ type: 'pie', radius: ['35%', '68%'], data: Object.entries(roles).map(([key, value]) => ({ name: roleLabels[key] || key, value })), label: { fontSize: 11, color: theme.textSecondary }, itemStyle: { borderColor: 'transparent', borderWidth: 0 }, emphasis: { itemStyle: { shadowBlur: 8, shadowColor: withAlpha(theme.primaryDark, 0.2) } } }],
    }, true);
  }
}

async function toggleAdmin(uid) {
  try {
    const response = await apiClient.patch(API_ROUTES.ADMIN_TOGGLE_ADMIN(uid));
    const target = users.value.find((item) => item.uid === uid);
    if (target) target.role = response.data.role;
  } catch (error) {
    console.warn(error);
  }
}

async function deleteUser(uid) {
  if (!confirm('确认删除该用户？此操作不可撤销。')) return;
  try {
    await apiClient.delete(`${API_ROUTES.ADMIN_USERS}/${uid}`);
    users.value = users.value.filter((item) => item.uid !== uid);
  } catch (error) {
    console.warn(error);
  }
}

function resizeCharts() {
  [timeChart, roseChart, materialsComboChart, barChart, diffChart, opTypePieChart, opRatingBarChart, rolePieChart].forEach((chart) => chart?.resize());
}

const maxCount = computed(() => Math.max(...(stats.value.user_message_counts || []).map((item) => item.count), 1));
const barWidth = (count) => `${Math.round((count / maxCount.value) * 100)}%`;

watch(isAdmin, (value) => {
  if (value && !users.value.length) loadAll();
});
watch([timeChartType, myStats, allStats], () => nextTick(renderTimeChart), { deep: true });
watch([distScope, myStats, allStats], () => nextTick(renderDistributionCharts), { deep: true });
watch([opinionStats, roleDist], () => nextTick(renderOpinionCharts), { deep: true });

onMounted(() => {
  if (isAdmin.value) loadAll();
  themeObserver = observeChartAppearance(() => nextTick(renderAllCharts));
  window.addEventListener('resize', resizeCharts);
});

onUnmounted(() => {
  themeObserver?.disconnect();
  window.removeEventListener('resize', resizeCharts);
  [timeChart, roseChart, materialsComboChart, barChart, diffChart, opTypePieChart, opRatingBarChart, rolePieChart].forEach((chart) => chart?.dispose());
  statsEventSource?.close();
});
</script>

<style scoped>
.admin-page { display: flex; flex-direction: column; gap: 16px; padding: 16px 20px 20px; overflow-y: auto; height: 100%; box-sizing: border-box; }
.admin-header, .section-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.header-left { display: flex; align-items: center; gap: 12px; }
.live-badge, .toggle-group, .tbl-btn { border: 1px solid color-mix(in srgb, var(--color-primary) 12%, var(--border-color)); }
.live-badge, .toggle-group { background: color-mix(in srgb, var(--color-primary) 7%, var(--card-bg)); }
.live-badge { font-size: 12px; padding: 4px 10px; border-radius: 999px; color: var(--text-secondary); }
.live-badge.connected, .action-tag.active, .badge-admin, .refresh-btn { background: var(--color-primary); color: #fff; }
.refresh-btn { border: none; border-bottom: 3px solid var(--color-primary-dark); border-radius: 999px; padding: 7px 18px; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.2s ease; }
.refresh-btn:hover { background: var(--color-primary-light); border-bottom-color: var(--color-primary); }
.no-permission, .loading-text { color: var(--text-muted); font-size: 14px; }
.loading-text { display: flex; align-items: center; gap: 10px; }
.no-permission { text-align: center; padding: 60px 0; }
.stats-row, .doc-status-row { display: flex; gap: 12px; }
.stat-card, .time-card, .section, .metric-card { background: var(--card-bg); border: 1px solid var(--border-color); }
.stat-card { flex: 1; border-radius: 16px; padding: 16px; display: flex; align-items: center; gap: 14px; }
.stat-card--primary { background: color-mix(in srgb, var(--color-primary) 10%, var(--card-bg)); }
.stat-card--cool { background: color-mix(in srgb, var(--color-accent-cool) 10%, var(--card-bg)); }
.stat-card--mint { background: color-mix(in srgb, var(--color-accent-mint) 10%, var(--card-bg)); }
.stat-icon { width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-icon--primary { background: color-mix(in srgb, var(--color-primary) 18%, transparent); color: var(--color-primary-dark); }
.stat-icon--cool { background: color-mix(in srgb, var(--color-accent-cool) 18%, transparent); color: color-mix(in srgb, var(--color-accent-cool) 72%, #0d2033); }
.stat-icon--mint { background: color-mix(in srgb, var(--color-accent-mint) 18%, transparent); color: color-mix(in srgb, var(--color-accent-mint) 68%, #12321f); }
.stat-copy, .time-card, .metric-card { display: flex; flex-direction: column; }
.stat-copy { gap: 4px; }
.stat-num, .metric-value { font-size: 28px; font-weight: 800; color: var(--text-primary); line-height: 1; }
.stat-label, .tc-label, .metric-label, .chart-sub-label, .bar-uid { color: var(--text-secondary); }
.stat-label, .metric-label { font-size: 12px; }
.time-cards-row, .dist-grid, .opinion-overview { display: grid; gap: 12px; }
.time-cards-row { grid-template-columns: repeat(4, 1fr); }
.time-card { padding: 16px; gap: 6px; }
.time-card--primary { border-top: 3px solid var(--color-primary); background: color-mix(in srgb, var(--color-primary) 8%, var(--card-bg)); }
.time-card--primary-dark { border-top: 3px solid var(--color-primary-dark); background: linear-gradient(160deg, color-mix(in srgb, var(--color-primary-dark) 82%, #0f1116), color-mix(in srgb, var(--color-primary) 62%, #151922)); color: #fff; }
.time-card--cool { border-top: 3px solid var(--color-accent-cool); background: color-mix(in srgb, var(--color-accent-cool) 8%, var(--card-bg)); }
.time-card--cool-dark { border-top: 3px solid var(--color-accent-cool); background: linear-gradient(160deg, color-mix(in srgb, var(--color-accent-cool) 70%, #0f1720), color-mix(in srgb, var(--color-accent-mint) 44%, #12202b)); color: #fff; }
.tc-label { font-size: 11px; }
.time-card--primary-dark .tc-label, .time-card--cool-dark .tc-label { color: rgba(255, 255, 255, 0.74); }
.tc-value { font-size: 22px; font-weight: 800; color: var(--text-primary); line-height: 1; }
.time-card--primary-dark .tc-value, .time-card--cool-dark .tc-value { color: #fff; }
.tc-value small { font-size: 11px; font-weight: 400; color: var(--text-muted); }
.time-card--primary-dark .tc-value small, .time-card--cool-dark .tc-value small { color: rgba(255, 255, 255, 0.7); }
.section { padding: 16px; display: flex; flex-direction: column; gap: 12px; }
.section-label { font-size: 13px; font-weight: 700; color: var(--text-primary); }
.toggle-group { display: flex; gap: 4px; padding: 4px; border-radius: 10px; }
.action-tag { font-size: 11px; padding: 3px 10px; border-radius: 8px; color: var(--text-secondary); cursor: pointer; transition: all 0.2s ease; }
.action-tag:hover, .tbl-btn:hover { background: color-mix(in srgb, var(--color-primary) 14%, var(--card-bg)); color: var(--text-primary); }
.chart-area { width: 100%; height: 220px; }
.chart-area-sm { width: 100%; height: 180px; }
.dist-grid, .opinion-overview { grid-template-columns: repeat(4, 1fr); }
.user-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.user-table th { padding: 8px 10px; background: color-mix(in srgb, var(--border-color) 24%, var(--card-bg)); color: var(--text-secondary); font-weight: 600; border-bottom: 1px solid var(--border-color); text-align: left; }
.user-table td { padding: 8px 10px; border-bottom: 1px solid color-mix(in srgb, var(--border-color) 74%, transparent); color: var(--text-primary); vertical-align: middle; }
.badge-admin, .badge-certified, .badge-user { padding: 2px 8px; font-size: 11px; font-weight: 700; border-radius: 999px; }
.badge-certified { background: var(--color-accent-cool); color: #fff; }
.badge-user { background: color-mix(in srgb, var(--border-color) 40%, var(--card-bg)); color: var(--text-secondary); }
.action-cell { display: flex; gap: 6px; }
.tbl-btn { background: color-mix(in srgb, var(--color-primary) 7%, var(--card-bg)); padding: 4px 10px; font-size: 11px; cursor: pointer; transition: all 0.2s ease; color: var(--text-primary); }
.tbl-btn.danger:hover { background: var(--color-primary); border-color: var(--color-primary); color: #fff; }
.tbl-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.user-avatar-thumb, .avatar-placeholder-sm { width: 28px; height: 28px; border-radius: 50%; }
.user-avatar-thumb { object-fit: cover; }
.avatar-placeholder-sm { background: color-mix(in srgb, var(--border-color) 40%, var(--card-bg)); display: flex; align-items: center; justify-content: center; color: var(--text-muted); }
.bar-list { display: flex; flex-direction: column; gap: 8px; }
.bar-row { display: flex; align-items: center; gap: 10px; }
.bar-uid { font-size: 12px; width: 60px; flex-shrink: 0; }
.bar-track { flex: 1; background: color-mix(in srgb, var(--border-color) 30%, var(--card-bg)); height: 12px; }
.bar-fill { height: 100%; background: linear-gradient(to right, var(--color-primary), var(--color-secondary), var(--color-accent-cool)); transition: width 0.4s ease; }
.bar-count { font-size: 12px; color: var(--text-primary); width: 30px; text-align: right; flex-shrink: 0; }
.metric-card { flex: 1; padding: 12px 16px; gap: 4px; border-left: 3px solid var(--ac); background: color-mix(in srgb, var(--ac) 8%, var(--card-bg)); }
.metric-card--primary { --ac: var(--color-primary); }
.metric-card--secondary { --ac: var(--color-secondary); }
.metric-card--cool { --ac: var(--color-accent-cool); }
.metric-card--mint { --ac: var(--color-accent-mint); }
.metric-value { color: var(--ac); }
.hot-words { display: flex; flex-wrap: wrap; gap: 6px; padding: 8px 0; align-content: flex-start; height: 180px; overflow: hidden; }
.hot-word { padding: 2px 8px; border-radius: 12px; color: var(--text-primary); cursor: default; transition: transform 0.2s ease; }
.hot-word--primary { background: color-mix(in srgb, var(--color-primary) 12%, transparent); }
.hot-word--secondary { background: color-mix(in srgb, var(--color-secondary) 12%, transparent); }
.hot-word--cool { background: color-mix(in srgb, var(--color-accent-cool) 12%, transparent); }
.hot-word:hover { transform: scale(1.08); }
@media (max-width: 1280px) { .time-cards-row, .dist-grid, .opinion-overview { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 900px) { .stats-row, .doc-status-row { flex-direction: column; } .time-cards-row, .dist-grid, .opinion-overview { grid-template-columns: 1fr; } }
</style>
