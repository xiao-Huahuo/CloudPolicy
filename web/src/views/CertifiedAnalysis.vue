<template>
  <div class="ca-page">
    <div class="ca-header">
      <PolicyTitle title="发布数据追踪" />
      <p class="ca-desc">查看您上传的政务文件的触达效果与用户反馈</p>
    </div>

    <div v-if="!userStore.isCertified && !userStore.isAdmin" class="no-perm">
      <svg viewBox="0 0 24 24" width="48" height="48" stroke="#ccc" stroke-width="1.5" fill="none"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      <p>需要认证主体权限才能访问此页面</p>
    </div>

    <template v-else>
      <!-- 概览卡片 -->
      <div class="overview-grid">
        <div class="ov-card" v-for="card in overviewCards" :key="card.label" :style="{ '--accent': card.color }">
          <div class="ov-icon" :style="{ background: card.color + '22' }">
            <svg viewBox="0 0 24 24" width="22" height="22" :stroke="card.color" stroke-width="2" fill="none" v-html="card.icon"></svg>
          </div>
          <div class="ov-text">
            <span class="ov-value">{{ card.value }}</span>
            <span class="ov-label">{{ card.label }}</span>
          </div>
          <div class="ov-bar" :style="{ background: `linear-gradient(90deg, ${card.color}33, transparent)` }"></div>
        </div>
      </div>

      <!-- 对比区 -->
      <div class="compare-section">
        <div class="section-title"><span class="dot"></span>与全站对比</div>
        <div class="compare-grid">
          <div class="compare-item">
            <span class="ci-label">我的平均浏览量</span>
            <div class="ci-bar-wrap">
              <div class="ci-bar mine" :style="{ width: myViewPct + '%' }"></div>
              <div class="ci-bar global" :style="{ width: globalViewPct + '%' }"></div>
            </div>
            <div class="ci-nums">
              <span class="mine-num">我: {{ myAvgViews }}</span>
              <span class="global-num">全站均: {{ stats?.global_avg_views || 0 }}</span>
            </div>
          </div>
          <div class="compare-item">
            <span class="ci-label">我的平均点赞量</span>
            <div class="ci-bar-wrap">
              <div class="ci-bar mine" :style="{ width: myLikePct + '%' }"></div>
              <div class="ci-bar global" :style="{ width: globalLikePct + '%' }"></div>
            </div>
            <div class="ci-nums">
              <span class="mine-num">我: {{ myAvgLikes }}</span>
              <span class="global-num">全站均: {{ stats?.global_avg_likes || 0 }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 评议类型分布 -->
      <div class="charts-row">
        <div class="chart-card">
          <div class="section-title"><span class="dot"></span>评议类型分布</div>
          <div ref="opTypePieRef" class="chart-box"></div>
        </div>
        <div class="chart-card">
          <div class="section-title"><span class="dot"></span>评分分布</div>
          <div ref="ratingBarRef" class="chart-box"></div>
        </div>
      </div>

      <!-- 逐文件反馈表 -->
      <div class="feedback-section">
        <div class="section-title"><span class="dot"></span>逐文件触达数据</div>
        <div class="feedback-table">
          <div class="ft-head">
            <span>文件标题</span><span>状态</span><span>浏览</span><span>点赞</span><span>评议</span><span>均分</span>
          </div>
          <transition-group name="row-fade" tag="div">
            <div v-for="doc in stats?.doc_feedback || []" :key="doc.id" class="ft-row">
              <span class="ft-title">{{ doc.title }}</span>
              <span class="ft-status" :class="doc.status">{{ statusLabel(doc.status) }}</span>
              <span class="ft-num">
                <svg viewBox="0 0 24 24" width="11" height="11" stroke="currentColor" stroke-width="2" fill="none"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                {{ doc.view_count }}
              </span>
              <span class="ft-num">
                <svg viewBox="0 0 24 24" width="11" height="11" stroke="currentColor" stroke-width="2" fill="none"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3H14z"/></svg>
                {{ doc.like_count }}
              </span>
              <span class="ft-num">{{ doc.opinion_count }}</span>
              <span class="ft-rating">
                <span v-for="n in 5" :key="n" class="star" :class="{ filled: n <= Math.round(doc.avg_rating) }">★</span>
              </span>
            </div>
          </transition-group>
          <div v-if="!stats?.doc_feedback?.length" class="empty-tip">暂无数据</div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import PolicyTitle from '@/components/common/PolicyTitle.vue'
import { useUserStore } from '@/stores/auth.js'
import { apiClient, API_ROUTES } from '@/router/api_routes'

const userStore = useUserStore()
const stats = ref(null)
const opTypePieRef = ref(null)
const ratingBarRef = ref(null)

const statusLabel = (s) => ({ approved: '已通过', pending: '待审核', rejected: '已拒绝' }[s] || s)

const overviewCards = computed(() => [
  { label: '总文件数', value: stats.value?.total ?? '-', color: '#c0392b', icon: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>' },
  { label: '已审核通过', value: stats.value?.approved ?? '-', color: '#27ae60', icon: '<polyline points="20 6 9 17 4 12"/>' },
  { label: '总浏览量', value: stats.value?.total_views ?? '-', color: '#2980b9', icon: '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>' },
  { label: '总点赞数', value: stats.value?.total_likes ?? '-', color: '#e67e22', icon: '<path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3H14z"/>' },
  { label: '收到评议', value: stats.value?.opinion_count ?? '-', color: '#8e44ad', icon: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>' },
  { label: '平均评分', value: stats.value?.rating_avg ?? '-', color: '#f39c12', icon: '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>' },
])

const myAvgViews = computed(() => {
  const approved = stats.value?.approved || 0
  return approved ? Math.round((stats.value?.total_views || 0) / approved) : 0
})
const myAvgLikes = computed(() => {
  const approved = stats.value?.approved || 0
  return approved ? Math.round((stats.value?.total_likes || 0) / approved) : 0
})
const myViewPct = computed(() => {
  const max = Math.max(myAvgViews.value, stats.value?.global_avg_views || 0, 1)
  return Math.round((myAvgViews.value / max) * 100)
})
const globalViewPct = computed(() => {
  const max = Math.max(myAvgViews.value, stats.value?.global_avg_views || 0, 1)
  return Math.round(((stats.value?.global_avg_views || 0) / max) * 100)
})
const myLikePct = computed(() => {
  const max = Math.max(myAvgLikes.value, stats.value?.global_avg_likes || 0, 1)
  return Math.round((myAvgLikes.value / max) * 100)
})
const globalLikePct = computed(() => {
  const max = Math.max(myAvgLikes.value, stats.value?.global_avg_likes || 0, 1)
  return Math.round(((stats.value?.global_avg_likes || 0) / max) * 100)
})

function renderCharts() {
  const typeMap = { review: '落地评价', correction: '解析纠错', message: '办事留言' }
  const dist = stats.value?.opinion_type_dist || {}

  if (opTypePieRef.value) {
    const chart = echarts.init(opTypePieRef.value)
    chart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      color: ['#c0392b', '#2980b9', '#27ae60'],
      series: [{
        type: 'pie', radius: ['40%', '70%'],
        data: Object.entries(dist).map(([k, v]) => ({ name: typeMap[k] || k, value: v })),
        label: { fontSize: 12 },
        emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.2)' } },
      }],
    })
  }

  if (ratingBarRef.value) {
    const chart = echarts.init(ratingBarRef.value)
    const ratingDist = [1,2,3,4,5].map(n => ({
      name: `${n}星`,
      value: (stats.value?.doc_feedback || []).filter(d => Math.round(d.avg_rating) === n).length
    }))
    chart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { top: 10, bottom: 30, left: 40, right: 10 },
      xAxis: { type: 'category', data: ratingDist.map(r => r.name) },
      yAxis: { type: 'value', minInterval: 1 },
      series: [{
        type: 'bar', barWidth: '50%',
        data: ratingDist.map(r => r.value),
        itemStyle: {
          color: (p) => ['#e74c3c','#e67e22','#f1c40f','#2ecc71','#27ae60'][p.dataIndex],
          borderRadius: [4, 4, 0, 0],
        },
      }],
    })
  }
}

onMounted(async () => {
  if (!userStore.isCertified && !userStore.isAdmin) return
  try {
    const res = await apiClient.get(API_ROUTES.POLICY_DOCS_MY_STATS)
    stats.value = res.data
    await nextTick()
    renderCharts()
  } catch (e) { console.error(e) }
})
</script>

<style scoped>
.ca-page { padding: 30px; max-width: 1100px; margin: 0 auto; }
.ca-header { margin-bottom: 24px; }
.ca-desc { color: var(--text-secondary, #666); font-size: 14px; margin: 6px 0 0; }

.no-perm {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; padding: 80px; color: #999; gap: 16px;
}

/* 概览卡片 */
.overview-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px; margin-bottom: 24px;
}
.ov-card {
  position: relative; overflow: hidden;
  background: var(--card-bg, #fff);
  border: 1px solid var(--border-color, #e8e8e8);
  border-left: 3px solid var(--accent);
  padding: 18px 20px;
  display: flex; align-items: center; gap: 16px;
  transition: transform 0.25s, box-shadow 0.25s;
}
.ov-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.08); }
.ov-icon {
  width: 44px; height: 44px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.ov-text { display: flex; flex-direction: column; gap: 4px; }
.ov-value { font-size: 26px; font-weight: 900; color: var(--text-primary, #111); line-height: 1; }
.ov-label { font-size: 12px; color: var(--text-secondary, #666); }
.ov-bar {
  position: absolute; bottom: 0; left: 0; right: 0; height: 3px;
}

/* 对比区 */
.compare-section {
  background: var(--card-bg, #fff);
  border: 1px solid var(--border-color, #e8e8e8);
  padding: 20px; margin-bottom: 24px;
}
.compare-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 16px; }
.compare-item { display: flex; flex-direction: column; gap: 8px; }
.ci-label { font-size: 13px; font-weight: 600; color: var(--text-primary, #111); }
.ci-bar-wrap { display: flex; flex-direction: column; gap: 4px; }
.ci-bar {
  height: 8px; border-radius: 4px; transition: width 0.8s cubic-bezier(0.4,0,0.2,1);
  min-width: 4px;
}
.ci-bar.mine { background: var(--color-primary, #c0392b); }
.ci-bar.global { background: #bdc3c7; }
.ci-nums { display: flex; justify-content: space-between; font-size: 12px; }
.mine-num { color: var(--color-primary, #c0392b); font-weight: 600; }
.global-num { color: #999; }

/* 图表区 */
.charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
.chart-card {
  background: var(--card-bg, #fff);
  border: 1px solid var(--border-color, #e8e8e8);
  padding: 20px;
}
.chart-box { height: 220px; margin-top: 12px; }

/* 表格 */
.feedback-section {
  background: var(--card-bg, #fff);
  border: 1px solid var(--border-color, #e8e8e8);
  padding: 20px;
}
.feedback-table { margin-top: 16px; }
.ft-head, .ft-row {
  display: grid;
  grid-template-columns: 3fr 80px 60px 60px 60px 90px;
  gap: 8px; align-items: center;
  padding: 10px 12px;
  font-size: 13px;
}
.ft-head {
  background: var(--content-bg, #f4f5f7);
  font-weight: 700; font-size: 12px; color: var(--text-secondary, #666);
  border-radius: 4px;
}
.ft-row {
  border-bottom: 1px solid var(--border-color, #f0f0f0);
  transition: background 0.2s;
}
.ft-row:hover { background: var(--content-bg, #f9f9f9); }
.ft-title { font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ft-status { font-size: 11px; padding: 2px 8px; border-radius: 10px; font-weight: bold; text-align: center; }
.ft-status.approved { background: #e8f5e9; color: #2e7d32; }
.ft-status.pending { background: #fff8e1; color: #f57f17; }
.ft-status.rejected { background: #fce4e4; color: #c0392b; }
.ft-num { display: flex; align-items: center; gap: 4px; color: var(--text-secondary, #666); }
.ft-rating { display: flex; gap: 1px; }
.star { color: #ddd; font-size: 13px; }
.star.filled { color: #f39c12; }

.section-title {
  display: flex; align-items: center; gap: 8px;
  font-weight: 700; font-size: 14px; color: var(--text-primary, #111);
}
.dot { width: 8px; height: 8px; border-radius: 50%; background: var(--color-primary, #c0392b); flex-shrink: 0; }
.empty-tip { text-align: center; color: #999; padding: 30px; font-size: 13px; }

.row-fade-enter-active { transition: all 0.4s ease; }
.row-fade-enter-from { opacity: 0; transform: translateX(-10px); }
</style>
