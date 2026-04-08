<template>
  <div class="swipe-page">
    <div class="swipe-header">
      <PolicyTitle title="政策推荐阅读" />
      <p class="swipe-desc">根据您的职业和浏览偏好，为您推荐相关政策</p>
    </div>

    <div class="swipe-layout">
      <!-- 左侧文章流 -->
      <div class="article-feed" ref="feedRef" @scroll="onScroll">
        <transition-group name="article" tag="div">
          <div v-for="doc in docs" :key="doc.id" class="article-card"
            :class="{ active: activeId === doc.id }" @click="openDoc(doc)">
            <div class="ac-top">
              <span class="ac-cat" v-if="doc.category">{{ doc.category }}</span>
              <span class="ac-date">{{ formatDate(doc.created_time) }}</span>
            </div>
            <h2 class="ac-title">{{ doc.title }}</h2>
            <p class="ac-excerpt">{{ excerpt(doc.content) }}</p>
            <div class="ac-meta">
              <span class="ac-author">{{ doc.uploader_name || '认证主体' }}</span>
              <div class="ac-stats">
                <span class="ac-stat">
                  <svg viewBox="0 0 24 24" width="12" height="12" stroke="currentColor" stroke-width="2" fill="none"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  {{ doc.view_count }}
                </span>
                <span class="ac-stat">
                  <svg viewBox="0 0 24 24" width="12" height="12" stroke="currentColor" stroke-width="2" fill="none"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3H14z"/></svg>
                  {{ doc.like_count }}
                </span>
              </div>
            </div>
          </div>
        </transition-group>
        <div v-if="loading" class="loading-more">
          <div class="spinner-sm"></div> 加载中...
        </div>
        <div v-if="!loading && !hasMore" class="no-more">已加载全部内容</div>
      </div>

      <!-- 右侧阅读面板 -->
      <div class="reader-panel" :class="{ open: activeDoc }">
        <template v-if="activeDoc">
          <div class="rp-header">
            <button class="rp-close" @click="activeDoc = null">✕</button>
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
          </div>
        </template>
        <div v-else class="rp-empty">
          <svg viewBox="0 0 24 24" width="40" height="40" stroke="#ccc" stroke-width="1.5" fill="none"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
          <p>点击左侧文章开始阅读</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import PolicyTitle from '@/components/common/PolicyTitle.vue'
import { useUserStore } from '@/stores/auth.js'
import { apiClient, API_ROUTES } from '@/router/api_routes'

const userStore = useUserStore()
const docs = ref([])
const loading = ref(false)
const hasMore = ref(true)
const skip = ref(0)
const LIMIT = 10
const activeDoc = ref(null)
const activeId = ref(null)
const feedRef = ref(null)

const parsedTags = computed(() => {
  if (!activeDoc.value?.tags) return []
  return activeDoc.value.tags.split(',').map(t => t.trim()).filter(Boolean)
})

const excerpt = (content) => content?.slice(0, 120) + (content?.length > 120 ? '...' : '')
const formatDate = (t) => t ? new Date(t).toLocaleDateString('zh-CN') : ''

const loadMore = async () => {
  if (loading.value || !hasMore.value) return
  loading.value = true
  try {
    const route = userStore.token ? API_ROUTES.POLICY_DOC_RECOMMEND_ME : API_ROUTES.POLICY_DOC_RECOMMEND
    const res = await apiClient.get(route, { params: { skip: skip.value, limit: LIMIT } })
    const items = res.data
    docs.value.push(...items)
    skip.value += items.length
    if (items.length < LIMIT) hasMore.value = false
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const onScroll = () => {
  const el = feedRef.value
  if (!el) return
  if (el.scrollTop + el.clientHeight >= el.scrollHeight - 100) loadMore()
}

const openDoc = async (doc) => {
  activeDoc.value = doc
  activeId.value = doc.id
  apiClient.post(API_ROUTES.POLICY_DOC_VIEW(doc.id)).catch(() => {})
}

const likeDoc = async (doc) => {
  try {
    const res = await apiClient.post(API_ROUTES.POLICY_DOC_LIKE(doc.id))
    doc.like_count = res.data.like_count
  } catch (e) { console.error(e) }
}

onMounted(loadMore)
</script>

<style scoped>
.swipe-page { padding: 24px; max-width: 1200px; margin: 0 auto; height: calc(100vh - 80px); display: flex; flex-direction: column; }
.swipe-header { margin-bottom: 20px; }
.swipe-desc { color: var(--text-secondary, #666); font-size: 14px; margin: 4px 0 0; }

.swipe-layout { display: grid; grid-template-columns: 1fr 1.2fr; gap: 20px; flex: 1; min-height: 0; }

.article-feed { overflow-y: auto; display: flex; flex-direction: column; gap: 12px; padding-right: 4px; }
.article-card {
  background: var(--card-bg, #fff);
  border: 1px solid var(--border-color, #e8e8e8);
  border-left: 3px solid transparent;
  padding: 16px 18px; cursor: pointer;
  transition: all 0.2s;
}
.article-card:hover { border-left-color: var(--color-primary, #c0392b); box-shadow: 0 4px 16px rgba(0,0,0,0.06); transform: translateX(2px); }
.article-card.active { border-left-color: var(--color-primary, #c0392b); background: rgba(192,57,43,0.03); }
.ac-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.ac-cat { font-size: 11px; background: rgba(192,57,43,0.1); color: #c0392b; padding: 2px 8px; border-radius: 10px; }
.ac-date { font-size: 11px; color: #999; }
.ac-title { font-size: 15px; font-weight: 700; margin: 0 0 8px; line-height: 1.4; color: var(--text-primary, #111); }
.ac-excerpt { font-size: 13px; color: var(--text-secondary, #666); line-height: 1.6; margin: 0 0 10px; }
.ac-meta { display: flex; justify-content: space-between; align-items: center; }
.ac-author { font-size: 12px; color: #999; }
.ac-stats { display: flex; gap: 10px; }
.ac-stat { display: flex; align-items: center; gap: 3px; font-size: 12px; color: #bbb; }

.reader-panel {
  background: var(--card-bg, #fff);
  border: 1px solid var(--border-color, #e8e8e8);
  overflow-y: auto; padding: 24px;
  transition: opacity 0.3s;
}
.rp-header { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 16px; }
.rp-close { background: none; border: 1px solid var(--border-color, #eee); width: 28px; height: 28px; border-radius: 50%; cursor: pointer; font-size: 12px; color: #999; flex-shrink: 0; transition: all 0.2s; }
.rp-close:hover { background: #f0f0f0; color: #333; }
.rp-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.rp-cat { font-size: 11px; background: rgba(192,57,43,0.1); color: #c0392b; padding: 2px 10px; border-radius: 10px; }
.rp-tag { font-size: 11px; background: var(--content-bg, #f4f5f7); color: #666; padding: 2px 10px; border-radius: 10px; }
.rp-title { font-size: 20px; font-weight: 800; margin: 0 0 12px; line-height: 1.4; color: var(--text-primary, #111); }
.rp-meta { display: flex; gap: 16px; font-size: 12px; color: #999; margin-bottom: 20px; flex-wrap: wrap; }
.rp-body { font-size: 15px; line-height: 1.9; color: var(--text-primary, #333); white-space: pre-wrap; }
.rp-actions { margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--border-color, #eee); }
.rp-like { display: flex; align-items: center; gap: 6px; background: none; border: 1px solid var(--border-color, #eee); padding: 8px 20px; border-radius: 20px; cursor: pointer; font-size: 13px; color: #666; transition: all 0.2s; }
.rp-like:hover { border-color: #c0392b; color: #c0392b; }
.rp-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; gap: 12px; color: #ccc; font-size: 13px; }

.loading-more { display: flex; align-items: center; justify-content: center; gap: 8px; padding: 16px; color: #999; font-size: 13px; }
.spinner-sm { width: 14px; height: 14px; border: 2px solid #eee; border-top-color: #c0392b; border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.no-more { text-align: center; padding: 16px; color: #ccc; font-size: 12px; }

.article-enter-active { transition: all 0.4s ease; }
.article-enter-from { opacity: 0; transform: translateY(16px); }
</style>
