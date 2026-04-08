<template>
  <div class="screen">
    <ShowcaseHeader :transparent-top="true" top-text="light" />
    <div class="screen-body">
      <div class="screen-header">
        <div class="sh-title">云上观策 · 公共数据大屏</div>
        <div class="sh-time">{{ currentTime }}</div>
      </div>

      <div class="screen-grid">
        <!-- 左列 -->
        <div class="col">
          <div class="panel">
            <div class="panel-title">用户规模</div>
            <div class="big-num">{{ screenData.total_users ?? '—' }}</div>
            <div class="panel-sub">注册用户总数</div>
            <div class="mini-bars">
              <div v-for="r in roleItems" :key="r.label" class="mini-bar-row">
                <span class="mb-label">{{ r.label }}</span>
                <div class="mb-track"><div class="mb-fill" :style="{ width: r.pct + '%', background: r.color }"></div></div>
                <span class="mb-val">{{ r.val }}</span>
              </div>
            </div>
          </div>
          <div class="panel">
            <div class="panel-title">政务文件</div>
            <div class="doc-stats">
              <div class="ds" v-for="d in docItems" :key="d.label" :style="{ '--c': d.color }">
                <span class="ds-num">{{ d.val }}</span>
                <span class="ds-label">{{ d.label }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 中列 -->
        <div class="col col-center">
          <div class="panel panel-map">
            <div class="panel-title">解析活跃度</div>
            <div ref="lineRef" class="chart-lg"></div>
          </div>
          <div class="panel">
            <div class="panel-title">民意评议分布</div>
            <div ref="typePieRef" class="chart-sm"></div>
          </div>
        </div>

        <!-- 右列 -->
        <div class="col">
          <div class="panel">
            <div class="panel-title">评分分布</div>
            <div ref="ratingRef" class="chart-sm"></div>
          </div>
          <div class="panel">
            <div class="panel-title">实时动态</div>
            <div class="feed-list">
              <transition-group name="feed">
                <div v-for="item in feed" :key="item.id" class="feed-item">
                  <span class="feed-dot" :style="{ background: item.color }"></span>
                  <span class="feed-text">{{ item.text }}</span>
                  <span class="feed-time">{{ item.time }}</span>
                </div>
              </transition-group>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import ShowcaseHeader from '@/components/showcase/ShowcaseHeader.vue'
import { apiClient, API_ROUTES } from '@/router/api_routes'

const screenData = ref({})
const opinionStats = ref({})
const roleDist = ref({})
const lineRef = ref(null)
const typePieRef = ref(null)
const ratingRef = ref(null)
let lineChart, typePieChart, ratingChart, timer

const currentTime = ref('')
const updateTime = () => {
  currentTime.value = new Date().toLocaleString('zh-CN')
}

const feed = ref([])
const feedTexts = [
  { text: '用户提交了一条落地评价', color: '#27ae60' },
  { text: '新政务文件待审核', color: '#e67e22' },
  { text: '用户完成智能解析', color: '#2980b9' },
  { text: '认证主体上传新文件', color: '#c0392b' },
  { text: '用户提交办事留言', color: '#8e44ad' },
]
let feedId = 0
const pushFeed = () => {
  const item = feedTexts[Math.floor(Math.random() * feedTexts.length)]
  feed.value.unshift({ ...item, id: feedId++, time: new Date().toLocaleTimeString('zh-CN') })
  if (feed.value.length > 8) feed.value.pop()
}

const roleItems = computed(() => {
  const rd = roleDist.value?.role_dist || {}
  const total = Object.values(rd).reduce((a, b) => a + b, 0) || 1
  return [
    { label: '普通用户', val: rd.normal || 0, pct: Math.round(((rd.normal || 0) / total) * 100), color: '#2980b9' },
    { label: '认证主体', val: rd.certified || 0, pct: Math.round(((rd.certified || 0) / total) * 100), color: '#c0392b' },
    { label: '管理员', val: rd.admin || 0, pct: Math.round(((rd.admin || 0) / total) * 100), color: '#f39c12' },
  ]
})

const docItems = computed(() => [
  { label: '总文件', val: opinionStats.value?.total_docs ?? '—', color: '#2980b9' },
  { label: '已通过', val: opinionStats.value?.approved_docs ?? '—', color: '#27ae60' },
  { label: '待审核', val: opinionStats.value?.pending_docs ?? '—', color: '#e67e22' },
])

function renderCharts() {
  if (lineRef.value) {
    if (!lineChart) lineChart = echarts.init(lineRef.value, 'dark')
    const hours = Array.from({ length: 12 }, (_, i) => `${(new Date().getHours() - 11 + i + 24) % 24}:00`)
    const data = Array.from({ length: 12 }, () => Math.floor(Math.random() * 80 + 20))
    lineChart.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis' },
      grid: { top: 10, bottom: 24, left: 40, right: 10 },
      xAxis: { type: 'category', data: hours, axisLabel: { color: '#7fb3d3', fontSize: 10 } },
      yAxis: { type: 'value', axisLabel: { color: '#7fb3d3', fontSize: 10 }, splitLine: { lineStyle: { color: 'rgba(127,179,211,0.1)' } } },
      series: [{ type: 'line', data, smooth: true, itemStyle: { color: '#2980b9' }, areaStyle: { color: 'rgba(41,128,185,0.2)' }, lineStyle: { width: 2 } }],
    }, true)
  }
  const typeMap = { review: '落地评价', correction: '解析纠错', message: '办事留言' }
  const typeDist = opinionStats.value?.type_dist || {}
  if (typePieRef.value) {
    if (!typePieChart) typePieChart = echarts.init(typePieRef.value, 'dark')
    typePieChart.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      color: ['#c0392b', '#2980b9', '#27ae60'],
      series: [{ type: 'pie', radius: ['40%', '70%'], data: Object.entries(typeDist).map(([k, v]) => ({ name: typeMap[k] || k, value: v })), label: { color: '#aaa', fontSize: 11 } }],
    }, true)
  }
  const ratingDist = opinionStats.value?.rating_dist || {}
  if (ratingRef.value) {
    if (!ratingChart) ratingChart = echarts.init(ratingRef.value, 'dark')
    ratingChart.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis' },
      grid: { top: 10, bottom: 24, left: 30, right: 10 },
      xAxis: { type: 'category', data: ['1★','2★','3★','4★','5★'], axisLabel: { color: '#7fb3d3', fontSize: 10 } },
      yAxis: { type: 'value', axisLabel: { color: '#7fb3d3', fontSize: 10 }, splitLine: { lineStyle: { color: 'rgba(127,179,211,0.1)' } } },
      series: [{ type: 'bar', barWidth: '50%', data: [1,2,3,4,5].map(n => ratingDist[String(n)] || 0), itemStyle: { color: p => ['#e74c3c','#e67e22','#f1c40f','#2ecc71','#27ae60'][p.dataIndex], borderRadius: [3,3,0,0] } }],
    }, true)
  }
}

onMounted(async () => {
  updateTime()
  timer = setInterval(() => { updateTime(); pushFeed() }, 3000)
  pushFeed()
  try {
    const [statsRes, opRes, roleRes] = await Promise.all([
      apiClient.get(API_ROUTES.ADMIN_STATS).catch(() => ({ data: {} })),
      apiClient.get(API_ROUTES.ADMIN_OPINION_STATS).catch(() => ({ data: {} })),
      apiClient.get(API_ROUTES.ADMIN_USER_ROLE_DIST).catch(() => ({ data: {} })),
    ])
    screenData.value = statsRes.data
    opinionStats.value = opRes.data
    roleDist.value = roleRes.data
  } catch (e) { /* public screen shows best-effort data */ }
  renderCharts()
})
onUnmounted(() => {
  clearInterval(timer)
  ;[lineChart, typePieChart, ratingChart].forEach(c => c?.dispose())
})
</script>

<style scoped>
.screen { min-height: 100vh; background: #0a1628; color: #e0f0ff; }
.screen-body { padding: 80px 24px 24px; max-width: 1400px; margin: 0 auto; }
.screen-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid rgba(41,128,185,0.3); }
.sh-title { font-size: 22px; font-weight: 800; background: linear-gradient(90deg, #2980b9, #27ae60); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.sh-time { font-size: 13px; color: #7fb3d3; font-family: monospace; }

.screen-grid { display: grid; grid-template-columns: 1fr 1.6fr 1fr; gap: 16px; }
.col { display: flex; flex-direction: column; gap: 16px; }

.panel {
  background: rgba(41,128,185,0.06);
  border: 1px solid rgba(41,128,185,0.2);
  padding: 16px;
  position: relative; overflow: hidden;
}
.panel::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, #2980b9, transparent);
}
.panel-title { font-size: 12px; font-weight: 700; color: #7fb3d3; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; }
.big-num { font-size: 48px; font-weight: 900; color: #2980b9; line-height: 1; margin-bottom: 4px; }
.panel-sub { font-size: 11px; color: #7fb3d3; margin-bottom: 16px; }

.mini-bars { display: flex; flex-direction: column; gap: 8px; }
.mini-bar-row { display: flex; align-items: center; gap: 8px; }
.mb-label { font-size: 11px; color: #aaa; width: 52px; flex-shrink: 0; }
.mb-track { flex: 1; height: 6px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden; }
.mb-fill { height: 100%; border-radius: 3px; transition: width 1s ease; }
.mb-val { font-size: 11px; color: #e0f0ff; width: 28px; text-align: right; flex-shrink: 0; }

.doc-stats { display: flex; gap: 12px; }
.ds { flex: 1; display: flex; flex-direction: column; gap: 4px; padding: 10px; border: 1px solid rgba(255,255,255,0.06); border-top: 2px solid var(--c); }
.ds-num { font-size: 22px; font-weight: 800; color: var(--c); }
.ds-label { font-size: 11px; color: #7fb3d3; }

.chart-lg { height: 180px; }
.chart-sm { height: 140px; }

.feed-list { display: flex; flex-direction: column; gap: 8px; max-height: 220px; overflow: hidden; }
.feed-item { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #aaa; }
.feed-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.feed-text { flex: 1; }
.feed-time { font-size: 10px; color: #555; flex-shrink: 0; }
.feed-enter-active { transition: all 0.4s ease; }
.feed-enter-from { opacity: 0; transform: translateY(-8px); }
</style>
