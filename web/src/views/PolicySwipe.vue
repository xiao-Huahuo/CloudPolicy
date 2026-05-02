<template>
  <div class="swipe-page">
    <div class="swipe-header">
      <PolicyTitle title="政策推荐阅读" />
      <p class="swipe-desc">根据您的职业和浏览偏好，为您推荐相关政策</p>
    </div>

    <div class="swipe-search">
      <UnifiedSearchBox
        v-model="searchQuery"
        v-model:types="searchTypes"
        source="policy_swipe_search_dropdown"
        placeholder="搜索政策、文章、历史、智能体..."
        @submit="handleSearchSubmit"
      />
    </div>

    <div class="swipe-layout">
      <div class="left-section">
        <div class="overview-panel">
          <!-- 轮播图 -->
          <div class="carousel-section">
            <transition name="slide-fade" mode="out-in">
              <div class="carousel-slide" :key="slideIdx" :style="getCarouselStyle(carouselDocs[slideIdx])">
                <div class="slide-overlay"></div>
                <div class="slide-content">
                  <span class="slide-tag">{{ carouselDocs[slideIdx]?.category || '政策文件' }}</span>
                  <h3 class="slide-title">{{ carouselDocs[slideIdx]?.title || '加载中...' }}</h3>
                  <p class="slide-meta">浏览 {{ carouselDocs[slideIdx]?.view_count || 0 }} · 点赞 {{ carouselDocs[slideIdx]?.like_count || 0 }}</p>
                </div>
              </div>
            </transition>
            <div class="carousel-dots">
              <span v-for="(_, i) in carouselDocs" :key="i" class="dot" :class="{ active: i === slideIdx }" @click="slideIdx = i"></span>
            </div>
          </div>

          <!-- 概览列表 -->
          <div class="overview-list" ref="overviewRef" @scroll="onScroll">
            <div class="overview-header">
              <span class="overview-dot"></span>
              <span class="overview-title">政策概览</span>
            </div>
            <div v-for="doc in docs" :key="doc.id" class="overview-item"
              :class="{ active: activeId === doc.id }" @click="openDoc(doc)">
              <div class="ov-top">
                <span class="ov-cat" v-if="doc.category">{{ doc.category }}</span>
                <span class="ov-date">{{ formatDate(doc.created_time) }}</span>
              </div>
              <h3 class="ov-title">{{ doc.title }}</h3>
              <div class="ov-meta">
                <span class="ov-author">{{ doc.uploader_name || '认证主体' }}</span>
                <div class="ov-stats">
                  <span class="ov-stat">
                    <svg viewBox="0 0 24 24" width="11" height="11" stroke="currentColor" stroke-width="2" fill="none"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                    {{ doc.view_count }}
                  </span>
                  <span class="ov-stat">
                    <svg viewBox="0 0 24 24" width="11" height="11" stroke="currentColor" stroke-width="2" fill="none"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3H14z"/></svg>
                    {{ doc.like_count }}
                  </span>
                </div>
              </div>
            </div>
            <div v-if="loading" class="loading-more">
              <AgentLoader :size="18" compact :center="false" />
              <span>加载中...</span>
            </div>
            <div v-if="!loading && !hasMore" class="no-more">已加载全部内容</div>
          </div>
        </div>

      </div>

      <div class="middle-section">
        <div v-if="activeDoc" class="reader-panel">
          <div class="rp-header">
            <button class="rp-close" @click="closeDoc()">×</button>
            <div class="rp-tags">
              <span v-if="activeDoc.category" class="rp-cat">{{ activeDoc.category }}</span>
              <span v-for="tag in parsedTags" :key="tag" class="rp-tag">{{ tag }}</span>
            </div>
          </div>
          <h1 class="rp-title">{{ activeDoc.title }}</h1>
          <div class="rp-meta">
            <span>{{ activeDoc.uploader_name || '认证主体' }}</span>
            <span>{{ formatDate(activeDoc.created_time) }}</span>
            <span>{{ activeDoc.view_count }} 次浏览</span>
          </div>
          <div class="rp-body">{{ activeDoc.content }}</div>
          <div class="rp-actions">
            <button class="rp-like" @click="likeDoc(activeDoc)">
              <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3H14z"/></svg>
              {{ activeDoc.like_count }} 点赞
            </button>
            <button class="rp-favorite" :class="{ active: isDocFavorited(activeDoc.id) }" @click="toggleFavoriteDoc(activeDoc)">
              <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" :fill="isDocFavorited(activeDoc.id) ? 'currentColor' : 'none'"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
              {{ isDocFavorited(activeDoc.id) ? '已收藏' : '收藏' }}
            </button>
          </div>

          <section class="policy-feedback-source">
            <div class="feedback-source-header">
              <div>
                <span class="feedback-source-kicker">民生反馈来源</span>
                <h2>评论区与发表意见</h2>
              </div>
              <span class="policy-audit-note">意见提交后进入审核机制，通过后同步进入民生大厅展示</span>
            </div>

            <div class="policy-comments">
              <div class="policy-comments-title">评论区</div>
              <div v-for="comment in activePolicyFeedbacks" :key="comment.id" class="policy-comment">
                <div class="policy-comment-meta">
                  <span class="policy-comment-user">{{ comment.user }}</span>
                  <span class="policy-comment-status" :class="{ pending: comment.status === '待审核' }">{{ comment.status }}</span>
                </div>
                <p>{{ comment.content }}</p>
              </div>
            </div>

            <form class="policy-opinion-form" @submit.prevent="submitPolicyOpinion">
              <label for="policyOpinionInput">发表意见</label>
              <textarea
                id="policyOpinionInput"
                v-model="policyOpinionDraft"
                rows="3"
                placeholder="写下你对政策落地、办理体验或解析内容的意见"
              ></textarea>
              <div class="opinion-form-footer">
                <span>提交后先进入审核队列，演示版会在当前政策下方标记为待审核。</span>
                <button type="submit" :disabled="!policyOpinionDraft.trim()">提交意见</button>
              </div>
            </form>
          </section>
        </div>
        <div v-else class="reader-placeholder">
          <span class="reader-placeholder-tag">阅读区</span>
          <h3>从左侧选择一条政策，直接在这里展开阅读</h3>
          <p>政策概览会继续保留，方便连续切换不同条目，不再因为打开正文而挤掉左侧浏览区。</p>
        </div>
      </div>

      <div class="right-section">
        <div class="panel-header">
          <span class="panel-dot" :class="rightPanelMode === 'docs' ? 'dot-red' : 'dot-blue'"></span>
          <h3 class="panel-title">{{ rightPanelMode === 'docs' ? '中央文件' : '时事热点' }}</h3>
          <div class="right-panel-switch">
            <button class="switch-btn" :class="{ active: rightPanelMode === 'docs' }" @click="rightPanelMode = 'docs'">中央文件</button>
            <button class="switch-btn" :class="{ active: rightPanelMode === 'news' }" @click="rightPanelMode = 'news'">时事热点</button>
          </div>
        </div>

        <!-- 中央文件内容 -->
        <div class="docs-content" v-show="rightPanelMode === 'docs'">
          <div class="doc-titles-scroll">
            <div
              v-for="(doc, idx) in centralDocs"
              :key="idx"
              class="doc-title-item"
              :class="{ active: selectedDocIdx === idx }"
              @click="selectedDocIdx = idx"
            >
              <span class="doc-index">{{ String(idx + 1).padStart(2, '0') }}</span>
              <span class="doc-title-text">{{ doc.title }}</span>
            </div>
            <div v-if="docsLoading" class="loading-placeholder">
              <div v-for="i in 3" :key="i" class="skeleton-line"></div>
            </div>
          </div>

          <div class="doc-content-section" v-if="centralDocs[selectedDocIdx]">
            <div class="doc-content-header">
              <div class="red-header-bar">
                <span class="red-star">★</span>
                <span>中华人民共和国国务院</span>
                <span class="red-star">★</span>
              </div>
              <h4 class="doc-content-title">{{ centralDocs[selectedDocIdx].title }}</h4>
              <span class="doc-date" v-if="centralDocs[selectedDocIdx].pubDate">{{ centralDocs[selectedDocIdx].pubDate }}</span>
            </div>
            <div class="doc-content-body">
              <span v-html="stripHtml(centralDocs[selectedDocIdx].description) || '暂无摘要内容'"></span>
              <button v-if="centralDocs[selectedDocIdx].link" type="button" class="doc-read-more" @click="openCentralDoc(centralDocs[selectedDocIdx])">阅读全文 →</button>
            </div>
          </div>
        </div>

        <!-- 时事热点内容 -->
        <div class="news-content" v-show="rightPanelMode === 'news'">
          <div class="news-list">
            <div
              v-for="(item, idx) in hotNews"
              :key="idx"
              class="news-item"
              @click="openHotNewsItem(item)"
            >
              <span class="news-rank" :class="idx < 3 ? 'rank-top' : ''">{{ idx + 1 }}</span>
              <span class="news-title">{{ item.title }}</span>
              <svg class="news-arrow" viewBox="0 0 24 24" width="12" height="12" stroke="currentColor" stroke-width="2" fill="none"><polyline points="9 18 15 12 9 6"></polyline></svg>
            </div>
            <div v-if="newsLoading" class="loading-placeholder">
              <div v-for="i in 5" :key="i" class="skeleton-line"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PolicyTitle from '@/components/common/PolicyTitle.vue'
import UnifiedSearchBox from '@/components/common/UnifiedSearchBox.vue'
import AgentLoader from '@/components/ui/AgentLoader.vue'
import { trackHistoryEvent } from '@/api/history'
import { useUserStore } from '@/stores/auth.js'
import { apiClient, API_ROUTES } from '@/router/api_routes'
import { getHotNews, getCentralDocs } from '@/api/news'
import { buildSearchRouteQuery } from '@/utils/unifiedSearch'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const docs = ref([])
const loading = ref(false)
const hasMore = ref(true)
const skip = ref(0)
const LIMIT = 10
const activeDoc = ref(null)
const activeId = ref(null)
const overviewRef = ref(null)
const slideIdx = ref(0)
const carouselDocs = ref([])
let carouselTimer = null
const carouselImageModules = import.meta.glob('/src/assets/photos/opinion-carousel/*.{jpg,jpeg,png,webp}', { eager: true })
const carouselImages = Object.entries(carouselImageModules)
  .sort(([a], [b]) => a.localeCompare(b, 'zh-CN'))
  .map(([, mod]) => mod.default)

const centralDocs = ref([])
const hotNews = ref([])
const docsLoading = ref(true)
const newsLoading = ref(true)
const selectedDocIdx = ref(0)
const rightPanelMode = ref('docs')
const searchQuery = ref('')
const searchTypes = ref([])
const POLICY_DOC_FAVORITES_KEY = 'cloudpolicy.policyDocFavorites'
const favoriteDocIds = ref([])
const policyOpinionDraft = ref('')
const submittedPolicyOpinions = ref([])
const policyDocOpinions = ref({})

const parsedTags = computed(() => {
  if (!activeDoc.value?.tags) return []
  return activeDoc.value.tags.split(',').map(t => t.trim()).filter(Boolean)
})

const activePolicyFeedbacks = computed(() => {
  if (!activeDoc.value) return []
  const loadedOpinions = policyDocOpinions.value[activeDoc.value.id] || []
  const base = loadedOpinions.length ? loadedOpinions : [
    {
      id: `sample-${activeDoc.value.id}-1`,
      user: '群众代表',
      status: '已审核',
      content: `希望继续跟进“${activeDoc.value.title}”在基层办理中的材料简化和窗口协同情况。`,
    },
    {
      id: `sample-${activeDoc.value.id}-2`,
      user: '企业用户',
      status: '已审核',
      content: '政策条款已经比较清楚，建议后续补充适用对象和申报时间节点的提醒。',
    },
  ]
  const local = submittedPolicyOpinions.value.filter((item) => item.docId === activeDoc.value.id)
  return [...local, ...base]
})

const formatDate = (t) => t ? new Date(t).toLocaleDateString('zh-CN') : ''

const stripHtml = (html) => {
  if (!html) return ''
  return String(html).replace(/<[^>]*>/g, '')
}

const getCarouselStyle = (doc) => {
  const style = { background: '#c0392b' }
  if (!doc) return style
  if (doc.bgImage) {
    style.backgroundImage = `url(${doc.bgImage})`
    style.backgroundSize = 'cover'
    style.backgroundPosition = 'center'
  }
  return style
}

const normalizeDocId = (value) => {
  const parsed = Number.parseInt(String(value ?? ''), 10)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null
}

const readFavoriteDocIds = () => {
  if (typeof window === 'undefined') return []
  try {
    const parsed = JSON.parse(window.localStorage.getItem(POLICY_DOC_FAVORITES_KEY) || '[]')
    if (!Array.isArray(parsed)) return []
    return parsed.map((item) => normalizeDocId(item)).filter(Boolean)
  } catch {
    return []
  }
}

const persistFavoriteDocIds = (docIds) => {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(POLICY_DOC_FAVORITES_KEY, JSON.stringify(docIds))
}

const isDocFavorited = (docId) => favoriteDocIds.value.includes(normalizeDocId(docId))

const syncDocPatch = (docId, patch) => {
  docs.value = docs.value.map((item) => (item.id === docId ? { ...item, ...patch } : item))
  carouselDocs.value = carouselDocs.value.map((item) => (item.id === docId ? { ...item, ...patch } : item))
  if (activeDoc.value?.id === docId) {
    activeDoc.value = { ...activeDoc.value, ...patch }
  }
}

const mapOpinionFeedback = (opinion) => ({
  id: opinion.id,
  user: opinion.user_name || '匿名用户',
  status: '已审核',
  content: opinion.content,
})

const loadDocOpinions = async (docId) => {
  const normalizedId = normalizeDocId(docId)
  if (!normalizedId || policyDocOpinions.value[normalizedId]) return

  try {
    const res = await apiClient.get(API_ROUTES.OPINIONS_BY_DOC(normalizedId), { params: { limit: 6 } })
    policyDocOpinions.value = {
      ...policyDocOpinions.value,
      [normalizedId]: (res.data || []).map(mapOpinionFeedback),
    }
  } catch (error) {
    console.warn('政策评议加载失败', error)
    policyDocOpinions.value = { ...policyDocOpinions.value, [normalizedId]: [] }
  }
}

const syncDocRoute = async (docId) => {
  const nextId = normalizeDocId(docId)
  const currentId = normalizeDocId(route.query.doc_id)
  if (nextId === currentId) return

  const nextQuery = { ...route.query }
  if (nextId) nextQuery.doc_id = String(nextId)
  else delete nextQuery.doc_id

  await router.replace({ path: '/policy-swipe', query: nextQuery })
}

const handleSearchSubmit = ({ query, types }) => {
  if (!query) return
  router.push({
    path: '/search',
    query: buildSearchRouteQuery(query, types),
  })
}

const loadMore = async () => {
  if (loading.value || !hasMore.value) return
  loading.value = true
  try {
    const route = userStore.token ? API_ROUTES.POLICY_DOC_RECOMMEND_ME : API_ROUTES.POLICY_DOC_RECOMMEND
    const res = await apiClient.get(route, { params: { skip: skip.value, limit: LIMIT } })
    const items = res.data || []
    const merged = [...docs.value]
    items.forEach((item) => {
      if (!merged.some((doc) => doc.id === item.id)) merged.push(item)
    })
    docs.value = merged
    skip.value += items.length
    if (items.length < LIMIT) hasMore.value = false

    // 鍒濆鍖栬疆鎾浘鏁版嵁
    if (carouselDocs.value.length === 0 && items.length > 0) {
      carouselDocs.value = items.slice(0, 5).map((doc, i) => ({
        ...doc,
        bgImage: carouselImages.length ? carouselImages[i % carouselImages.length] : ''
      }))
    }
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const loadCentralDocs = async () => {
  try {
    const res = await getCentralDocs(5)
    centralDocs.value = res.data.items || []
  } catch (e) {
    console.warn('中央文件加载失败', e)
  } finally {
    docsLoading.value = false
  }
}

const loadHotNews = async () => {
  try {
    const res = await getHotNews(10)
    hotNews.value = res.data.items || []
  } catch (e) {
    console.warn('热点新闻加载失败', e)
  } finally {
    newsLoading.value = false
  }
}

const onScroll = () => {
  const el = overviewRef.value
  if (!el) return
  if (el.scrollTop + el.clientHeight >= el.scrollHeight - 100) loadMore()
}

const openDoc = async (doc, options = {}) => {
  const { syncRoute = true, incrementView = true } = options
  activeDoc.value = doc
  activeId.value = doc.id
  if (syncRoute) await syncDocRoute(doc.id)
  await loadDocOpinions(doc.id)
  if (incrementView) {
    apiClient.post(API_ROUTES.POLICY_DOC_VIEW(doc.id)).then((res) => {
      const viewCount = res.data?.view_count
      if (typeof viewCount === 'number') {
        doc.view_count = viewCount
        if (activeDoc.value?.id === doc.id) activeDoc.value.view_count = viewCount
      }
    }).catch(() => {})
  }
}

const closeDoc = async (options = {}) => {
  const { syncRoute = true } = options
  activeDoc.value = null
  activeId.value = null
  if (syncRoute) await syncDocRoute(null)
}

const likeDoc = async (doc) => {
  try {
    const res = await apiClient.post(API_ROUTES.POLICY_DOC_LIKE(doc.id))
    if (typeof res.data?.like_count === 'number') {
      syncDocPatch(doc.id, { like_count: res.data.like_count })
    }
  } catch (e) { console.error(e) }
}

const toggleFavoriteDoc = (doc) => {
  const normalizedId = normalizeDocId(doc?.id)
  if (!normalizedId) return

  const nextIds = isDocFavorited(normalizedId)
    ? favoriteDocIds.value.filter((item) => item !== normalizedId)
    : [...favoriteDocIds.value, normalizedId]

  favoriteDocIds.value = nextIds
  persistFavoriteDocIds(nextIds)
}

const submitPolicyOpinion = () => {
  const content = policyOpinionDraft.value.trim()
  if (!content || !activeDoc.value) return

  submittedPolicyOpinions.value.unshift({
    id: `local-${activeDoc.value.id}-${Date.now()}`,
    docId: activeDoc.value.id,
    user: '当前用户',
    status: '待审核',
    content,
  })
  policyOpinionDraft.value = ''
}

const trackExternalBrowse = (payload) => {
  if (!userStore.token) return
  trackHistoryEvent(payload).catch(() => {})
}

const openCentralDoc = (doc) => {
  if (!doc?.link) return
  trackExternalBrowse({
    domain: 'policy_browse',
    event_type: 'opened_external',
    subject_type: 'external_policy_article',
    title: doc.title || '中央文件',
    summary: stripHtml(doc.description),
    route_path: window.location.pathname + window.location.search,
    external_url: doc.link,
    icon: 'policy',
    search_text: [doc.title, stripHtml(doc.description)].filter(Boolean).join('\n'),
    extra: {
      source: 'policy_swipe_central_docs',
      pub_date: doc.pubDate || null,
    },
  })
  window.open(doc.link, '_blank')
}

const openHotNewsItem = (item) => {
  if (!item?.link) return
  trackExternalBrowse({
    domain: 'article_browse',
    event_type: 'opened_external',
    subject_type: 'news_article',
    title: item.title || '热点资讯',
    summary: stripHtml(item.description),
    route_path: window.location.pathname + window.location.search,
    external_url: item.link,
    icon: 'news',
    search_text: [item.title, stripHtml(item.description)].filter(Boolean).join('\n'),
    extra: {
      source: 'policy_swipe_hot_news',
      pub_date: item.pubDate || null,
    },
  })
  window.open(item.link, '_blank')
}

const ensureDocLoaded = async (docId) => {
  const normalizedId = normalizeDocId(docId)
  if (!normalizedId) return null

  const existing = docs.value.find((item) => item.id === normalizedId)
  if (existing) return existing

  const res = await apiClient.get(API_ROUTES.POLICY_DOC_DETAIL(normalizedId))
  const fetched = res.data
  if (!fetched) return null

  docs.value = [fetched, ...docs.value.filter((item) => item.id !== fetched.id)]
  if (!carouselDocs.value.length) {
    carouselDocs.value = [{
      ...fetched,
      bgImage: carouselImages.length ? carouselImages[0] : '',
    }]
  }
  return fetched
}

const syncDocFromRoute = async () => {
  const docId = normalizeDocId(route.query.doc_id)
  if (!docId) {
    if (activeDoc.value) await closeDoc({ syncRoute: false })
    return
  }

  if (activeDoc.value?.id === docId) return

  try {
    const doc = await ensureDocLoaded(docId)
    if (doc) await openDoc(doc, { syncRoute: false })
  } catch (error) {
    console.warn('政策深链加载失败', error)
  }
}

const startCarousel = () => {
  carouselTimer = setInterval(() => {
    if (!carouselDocs.value.length) return
    slideIdx.value = (slideIdx.value + 1) % carouselDocs.value.length
  }, 4000)
}

watch(
  () => route.query.doc_id,
  async () => {
    await syncDocFromRoute()
  }
)

onMounted(async () => {
  favoriteDocIds.value = readFavoriteDocIds()
  await Promise.all([loadMore(), loadCentralDocs(), loadHotNews()])
  await syncDocFromRoute()
  startCarousel()
})

onBeforeUnmount(() => {
  if (carouselTimer) clearInterval(carouselTimer)
})
</script>

<style scoped>
.swipe-page { padding: 24px; max-width: 1600px; margin: 0 auto; height: calc(100vh - 80px); display: flex; flex-direction: column; }
.swipe-header { margin-bottom: 20px; }
.swipe-desc { color: var(--text-secondary, #666); font-size: 14px; margin: 4px 0 0; }
.swipe-search {
  margin: 16px 0 22px;
  max-width: 680px;
}

.swipe-layout {
  display: grid;
  grid-template-columns: minmax(300px, 360px) minmax(0, 1fr) minmax(320px, 420px);
  gap: 20px;
  flex: 1;
  min-height: 0;
}

/* 宸︿晶鍖哄煙 */
.left-section {
  min-height: 0;
}

.overview-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
}

.middle-section {
  min-height: 0;
  display: flex;
}

.reader-panel {
  width: 100%;
  background: var(--card-bg, #fff);
  border: 1px solid var(--border-color, #e8e8e8);
  border-radius: 10px;
  overflow-y: auto;
  padding: 24px;
}

.reader-placeholder {
  width: 100%;
  border: 1px dashed color-mix(in srgb, var(--color-primary, #c0392b) 24%, var(--border-color, #e8e8e8));
  border-radius: 10px;
  background: linear-gradient(180deg, color-mix(in srgb, var(--color-primary, #c0392b) 3%, var(--card-bg, #fff)), var(--card-bg, #fff));
  padding: 28px 26px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 12px;
  color: var(--text-secondary, #666);
}

.reader-placeholder-tag {
  display: inline-flex;
  align-self: flex-start;
  padding: 4px 10px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--color-primary, #c0392b) 10%, var(--card-bg, #fff));
  color: var(--color-primary, #c0392b);
  font-size: 11px;
  font-weight: 700;
}

.reader-placeholder h3 {
  margin: 0;
  font-size: 22px;
  line-height: 1.4;
  color: var(--text-primary, #111);
}

.reader-placeholder p {
  margin: 0;
  font-size: 14px;
  line-height: 1.8;
}

/* 鍙充晶鍖哄煙 */
.right-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: var(--card-bg, #fff);
  border: 1px solid var(--border-color, #e8e8e8);
  padding: 20px;
  overflow-y: auto;
  transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary, #111);
  margin: 0 0 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--color-primary, #c0392b);
}

/* 闈㈡澘澶撮儴 */
.panel-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color, #e8e8e8);
  margin-bottom: 16px;
}

.panel-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.dot-red { background: #c0392b; }
.dot-blue { background: #3498db; }

.panel-title {
  font-size: 16px;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary, #111);
}

.right-panel-switch {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.switch-btn {
  background: transparent;
  border: 1px solid var(--border-color, #ddd);
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-secondary, #666);
}

.switch-btn.active {
  background: var(--color-primary, #c0392b);
  border-color: var(--color-primary, #c0392b);
  color: #fff;
}

/* 杞挱鍥?*/
.carousel-section {
  position: relative;
  height: 200px;
  border-radius: 0;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.carousel-slide {
  position: relative;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  cursor: pointer;
  transition: transform 0.3s;
}
.slide-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, rgba(0,0,0,0.2), rgba(0,0,0,0.6));
}
.slide-content {
  position: relative;
  z-index: 1;
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  color: #fff;
}
.slide-tag {
  font-size: 11px;
  background: rgba(255,255,255,0.25);
  padding: 3px 10px;
  border-radius: 10px;
  width: fit-content;
  margin-bottom: 8px;
}
.slide-title {
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 6px;
  line-height: 1.4;
}
.slide-meta {
  font-size: 12px;
  opacity: 0.9;
  margin: 0;
}
.carousel-dots {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 6px;
  z-index: 2;
}
.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255,255,255,0.5);
  cursor: pointer;
  transition: all 0.3s;
}
.dot.active {
  width: 20px;
  border-radius: 3px;
  background: #fff;
}

/* 概览列表 */
.overview-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-right: 4px;
}
.overview-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  padding: 0 4px;
}
.overview-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-primary, #c0392b);
}
.overview-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary, #111);
}
.overview-item {
  background: color-mix(in srgb, var(--card-bg, #fff) 96%, #ffffff);
  border: 1px solid color-mix(in srgb, var(--color-primary, #c0392b) 6%, var(--border-color, #e8e8e8));
  padding: 12px 14px;
  cursor: pointer;
  transition: all 0.2s;
  border-radius: 6px;
}
.overview-item:hover {
  background: color-mix(in srgb, var(--color-primary, #c0392b) 3%, var(--card-bg, #fff));
  border-color: color-mix(in srgb, var(--color-primary, #c0392b) 18%, var(--border-color, #e8e8e8));
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.overview-item.active {
  border-color: color-mix(in srgb, var(--color-primary, #c0392b) 22%, var(--border-color, #e8e8e8));
  background: color-mix(in srgb, var(--color-primary, #c0392b) 6%, var(--card-bg, #fff));
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--color-primary, #c0392b) 10%, transparent);
}
.ov-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.ov-cat {
  font-size: 10px;
  background: rgba(192,57,43,0.1);
  color: #c0392b;
  padding: 2px 7px;
  border-radius: 8px;
}
.ov-date {
  font-size: 10px;
  color: #999;
}
.ov-title {
  font-size: 13px;
  font-weight: 600;
  margin: 0 0 8px;
  line-height: 1.4;
  color: var(--text-primary, #111);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.ov-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.ov-author {
  font-size: 11px;
  color: #999;
}
.ov-stats {
  display: flex;
  gap: 8px;
}
.ov-stat {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 11px;
  color: #bbb;
}

/* 阅读面板样式 */
.rp-header { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 16px; }
.rp-close { background: none; border: 1px solid var(--border-color, #eee); width: 28px; height: 28px; border-radius: 50%; cursor: pointer; font-size: 12px; color: #999; flex-shrink: 0; transition: all 0.2s; }
.rp-close:hover { background: #f0f0f0; color: #333; }
.rp-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.rp-cat { font-size: 11px; background: rgba(192,57,43,0.1); color: #c0392b; padding: 2px 10px; border-radius: 10px; }
.rp-tag { font-size: 11px; background: var(--content-bg, #f4f5f7); color: #666; padding: 2px 10px; border-radius: 10px; }
.rp-title { font-size: 20px; font-weight: 800; margin: 0 0 12px; line-height: 1.4; color: var(--text-primary, #111); }
.rp-meta { display: flex; gap: 16px; font-size: 12px; color: #999; margin-bottom: 20px; flex-wrap: wrap; }
.rp-body { font-size: 15px; line-height: 1.9; color: var(--text-primary, #333); white-space: pre-wrap; }
.rp-actions { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--border-color, #eee); }
.rp-like,
.rp-favorite {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: 1px solid var(--border-color, #eee);
  padding: 8px 20px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
  color: #666;
  transition: all 0.2s;
}
.rp-like:hover { border-color: #c0392b; color: #c0392b; }
.rp-favorite:hover,
.rp-favorite.active {
  border-color: #c0392b;
  color: #c0392b;
}

.policy-feedback-source {
  margin-top: 22px;
  padding: 18px;
  border: 1px solid color-mix(in srgb, var(--color-primary, #c0392b) 14%, var(--border-color, #eee));
  border-radius: 14px;
  background:
    radial-gradient(circle at 0% 0%, color-mix(in srgb, var(--color-primary, #c0392b) 8%, transparent), transparent 32%),
    color-mix(in srgb, var(--color-primary, #c0392b) 3%, var(--card-bg, #fff));
}

.feedback-source-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 14px;
}

.feedback-source-kicker {
  display: inline-flex;
  color: var(--color-primary, #c0392b);
  font-size: 12px;
  font-weight: 800;
  margin-bottom: 4px;
}

.feedback-source-header h2 {
  margin: 0;
  color: var(--text-primary, #111);
  font-size: 18px;
}

.policy-audit-note {
  max-width: 260px;
  color: var(--text-secondary, #666);
  font-size: 12px;
  line-height: 1.6;
  text-align: right;
}

.policy-comments {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
}

.policy-comments-title {
  color: var(--text-primary, #111);
  font-size: 13px;
  font-weight: 800;
}

.policy-comment {
  padding: 12px;
  border-radius: 12px;
  border: 1px solid color-mix(in srgb, var(--color-primary, #c0392b) 10%, var(--border-color, #eee));
  background: var(--card-bg, #fff);
}

.policy-comment-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.policy-comment-user {
  color: var(--text-primary, #111);
  font-size: 12px;
  font-weight: 800;
}

.policy-comment-status {
  padding: 2px 8px;
  border-radius: 999px;
  color: var(--color-primary, #c0392b);
  background: color-mix(in srgb, var(--color-primary, #c0392b) 10%, var(--card-bg, #fff));
  font-size: 11px;
  font-weight: 700;
}

.policy-comment-status.pending {
  color: color-mix(in srgb, var(--color-secondary, #e67e22) 82%, #7a3f00);
  background: color-mix(in srgb, var(--color-secondary, #e67e22) 12%, var(--card-bg, #fff));
}

.policy-comment p {
  margin: 0;
  color: var(--text-primary, #333);
  font-size: 13px;
  line-height: 1.7;
}

.policy-opinion-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.policy-opinion-form label {
  color: var(--text-primary, #111);
  font-size: 13px;
  font-weight: 800;
}

.policy-opinion-form textarea {
  resize: vertical;
  min-height: 84px;
  border: 1px solid color-mix(in srgb, var(--color-primary, #c0392b) 12%, var(--border-color, #eee));
  border-radius: 12px;
  padding: 10px 12px;
  background: var(--card-bg, #fff);
  color: var(--text-primary, #333);
  font-size: 13px;
  line-height: 1.6;
  outline: none;
}

.policy-opinion-form textarea:focus {
  border-color: color-mix(in srgb, var(--color-primary, #c0392b) 42%, var(--border-color, #eee));
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--color-primary, #c0392b) 10%, transparent);
}

.opinion-form-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.opinion-form-footer span {
  color: var(--text-secondary, #666);
  font-size: 12px;
  line-height: 1.5;
}

.opinion-form-footer button {
  flex-shrink: 0;
  border: 1px solid var(--color-primary, #c0392b);
  border-radius: 999px;
  background: var(--color-primary, #c0392b);
  color: #fff;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 800;
  cursor: pointer;
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.opinion-form-footer button:hover:not(:disabled) {
  transform: translateY(-1px);
}

.opinion-form-footer button:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

/* 中央文件样式 */
.doc-titles-scroll {
  max-height: 200px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.doc-title-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: color-mix(in srgb, var(--card-bg, #fff) 94%, #ffffff);
  border: 1px solid color-mix(in srgb, var(--color-primary, #c0392b) 8%, var(--border-color, #e8e8e8));
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.doc-title-item:hover {
  border-color: color-mix(in srgb, var(--color-primary, #c0392b) 18%, var(--border-color, #e8e8e8));
  background: color-mix(in srgb, var(--color-primary, #c0392b) 4%, var(--card-bg, #fff));
}

.doc-title-item.active {
  background: color-mix(in srgb, var(--color-primary, #c0392b) 8%, var(--card-bg, #fff));
  border-color: color-mix(in srgb, var(--color-primary, #c0392b) 24%, var(--border-color, #e8e8e8));
  box-shadow: inset 0 0 0 1px rgba(192,57,43,0.08);
}

.doc-index {
  font-size: 14px;
  font-weight: 700;
  color: #c0392b;
  flex-shrink: 0;
}

.doc-title-text {
  font-size: 13px;
  color: var(--text-primary, #333);
  line-height: 1.4;
  flex: 1;
}

.doc-content-section {
  background: var(--content-bg, #fafafa);
  padding: 16px;
  border-radius: 8px;
}

.doc-content-header {
  text-align: center;
  margin-bottom: 16px;
}

.red-header-bar {
  background: color-mix(in srgb, var(--color-primary, #c0392b) 90%, var(--color-primary-dark, #8e231b) 10%);
  color: #fff;
  border: 1px solid color-mix(in srgb, var(--color-primary, #c0392b) 34%, rgba(255, 255, 255, 0.24));
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 12px;
}

.red-star {
  font-size: 16px;
}

.doc-content-title {
  font-size: 15px;
  font-weight: 700;
  margin: 0 0 8px;
  color: var(--text-primary, #111);
}

.doc-date {
  font-size: 11px;
  color: #999;
}

.doc-content-body {
  font-size: 13px;
  line-height: 1.8;
  color: var(--text-secondary, #666);
}

.doc-read-more {
  display: inline-block;
  margin-top: 12px;
  padding: 0;
  border: none;
  background: transparent;
  color: #c0392b;
  text-decoration: none;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.doc-read-more:hover {
  text-decoration: underline;
}

/* 时事热点样式 */
.news-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.news-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: color-mix(in srgb, var(--card-bg, #fff) 95%, #ffffff);
  border: 1px solid color-mix(in srgb, var(--color-primary, #c0392b) 6%, var(--border-color, #e8e8e8));
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.news-item:hover {
  background: color-mix(in srgb, var(--color-primary, #c0392b) 4%, var(--card-bg, #fff));
  border-color: color-mix(in srgb, var(--color-primary, #c0392b) 16%, var(--border-color, #e8e8e8));
}

.news-rank {
  font-size: 14px;
  font-weight: 700;
  color: #999;
  flex-shrink: 0;
  width: 24px;
  text-align: center;
}

.news-rank.rank-top {
  color: #c0392b;
}

.news-title {
  flex: 1;
  font-size: 13px;
  color: var(--text-primary, #333);
  line-height: 1.4;
}

.news-arrow {
  flex-shrink: 0;
  color: #ccc;
}

.loading-more { display: flex; align-items: center; justify-content: center; gap: 10px; padding: 16px; color: #999; font-size: 13px; }
.no-more { text-align: center; padding: 16px; color: #ccc; font-size: 12px; }

.loading-placeholder {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-line {
  height: 12px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.slide-fade-enter-active, .slide-fade-leave-active { transition: opacity 0.4s; }
.slide-fade-enter-from, .slide-fade-leave-to { opacity: 0; }

@media (max-width: 1180px) {
  .swipe-layout {
    grid-template-columns: minmax(260px, 320px) minmax(0, 1fr);
  }

  .right-section {
    grid-column: 1 / -1;
  }
}

@media (max-width: 768px) {
  .swipe-page {
    padding: 16px;
    height: auto;
    min-height: calc(100vh - 80px);
  }

  .swipe-layout {
    grid-template-columns: 1fr;
  }
}
</style>
