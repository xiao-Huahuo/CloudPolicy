<template>
  <div class="search-page">
    <PolicyTitle class="policy-page-header" title="搜索中心" />

    <!-- 搜索栏 -->
    <div class="search-bar-wrap">
      <div class="search-bar">
        <svg class="search-icon" viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        <input
          ref="inputRef"
          v-model="inputVal"
          class="search-input"
          placeholder="搜索政策文件、时事热点..."
          @keydown.enter="doSearch"
          @input="onInput"
        />
        <button v-if="inputVal" class="clear-btn" @click="clearSearch">
          <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2.5" fill="none"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </button>
        <button class="search-btn" @click="doSearch" :disabled="searching">
          {{ searching ? '搜索中...' : '搜索' }}
        </button>
      </div>

      <!-- 热门搜索词 -->
      <div class="hot-tags" v-if="!hasSearched">
        <span class="hot-label">热门：</span>
        <span
          v-for="tag in hotTags"
          :key="tag"
          class="hot-tag"
          @click="quickSearch(tag)"
        >{{ tag }}</span>
      </div>
    </div>

    <!-- 搜索结果 -->
    <div class="results-area" v-if="hasSearched">
      <div class="results-meta">
        <span class="results-count" v-if="!searching">
          找到 <strong>{{ results.length }}</strong> 条结果
          <span v-if="currentQuery"> · "{{ currentQuery }}"</span>
        </span>
        <div class="filter-tabs">
          <button
            v-for="tab in filterTabs"
            :key="tab.key"
            :class="{ active: activeFilter === tab.key }"
            @click="activeFilter = tab.key"
          >{{ tab.label }}</button>
        </div>
      </div>

      <!-- 骨架屏 -->
      <div v-if="searching" class="skeleton-list">
        <div v-for="i in 5" :key="i" class="skeleton-result">
          <div class="sk-type"></div>
          <div class="sk-body">
            <div class="sk-title"></div>
            <div class="sk-desc"></div>
          </div>
        </div>
      </div>

      <!-- 无结果 -->
      <div v-else-if="filteredResults.length === 0" class="empty-state">
        <svg viewBox="0 0 24 24" width="48" height="48" stroke="#ccc" stroke-width="1.5" fill="none"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        <p>未找到相关内容</p>
        <span>试试其他关键词，或浏览热门搜索</span>
      </div>

      <!-- 结果列表 -->
      <div v-else class="result-list">
        <div
          v-for="(item, idx) in filteredResults"
          :key="idx"
          class="result-item"
          @click="openLink(item.link)"
        >
          <div class="ri-left">
            <span class="ri-type" :class="item.source_type === 'policy' ? 'type-policy' : 'type-news'">
              {{ item.source_type === 'policy' ? '政策' : '时事' }}
            </span>
          </div>
          <div class="ri-body">
            <p class="ri-title" v-html="highlight(item.title)"></p>
            <p class="ri-desc" v-if="item.description" v-html="highlight(item.description)"></p>
            <div class="ri-meta">
              <span class="ri-date" v-if="item.pubDate">{{ formatDate(item.pubDate) }}</span>
              <span class="ri-source" v-if="item.link">{{ getDomain(item.link) }}</span>
            </div>
          </div>
          <div class="ri-right">
            <svg viewBox="0 0 24 24" width="14" height="14" stroke="#ccc" stroke-width="2" fill="none"><polyline points="9 18 15 12 9 6"></polyline></svg>
          </div>
        </div>
      </div>
    </div>

    <!-- 未搜索时的推荐 -->
    <div class="recommend-area" v-else>
      <div class="rec-section">
        <h3 class="rec-title">最新政策</h3>
        <div class="rec-list">
          <div
            v-for="(doc, idx) in recentDocs"
            :key="idx"
            class="rec-item"
            @click="openLink(doc.link)"
          >
            <span class="rec-rank" :class="idx < 3 ? 'rank-top' : ''">{{ idx + 1 }}</span>
            <div class="rec-content">
              <p class="rec-text">{{ doc.title }}</p>
              <span class="rec-date">{{ formatDate(doc.pubDate) }}</span>
            </div>
          </div>
          <div v-if="docsLoading" class="loading-placeholder">
            <div v-for="i in 3" :key="i" class="skeleton-line"></div>
          </div>
        </div>
      </div>

      <div class="rec-section">
        <h3 class="rec-title">时事热点</h3>
        <div class="rec-list">
          <div
            v-for="(news, idx) in recentNews"
            :key="idx"
            class="rec-item"
            @click="openLink(news.link)"
          >
            <span class="rec-rank" :class="idx < 3 ? 'rank-top' : ''">{{ idx + 1 }}</span>
            <div class="rec-content">
              <p class="rec-text">{{ news.title }}</p>
              <span class="rec-date">{{ formatDate(news.pubDate) }}</span>
            </div>
          </div>
          <div v-if="newsLoading" class="loading-placeholder">
            <div v-for="i in 3" :key="i" class="skeleton-line"></div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { searchNews, getHotNews, getCentralDocs } from '@/api/news';
import PolicyTitle from '@/components/common/PolicyTitle.vue';

const route = useRoute();
const router = useRouter();

const inputVal = ref('');
const currentQuery = ref('');
const results = ref([]);
const searching = ref(false);
const hasSearched = ref(false);
const inputRef = ref(null);
const activeFilter = ref('all');

const recentDocs = ref([]);
const recentNews = ref([]);
const docsLoading = ref(true);
const newsLoading = ref(true);

const hotTags = ['改革', '政策', '乡村振兴', '营商环境', '医疗', '教育', '就业', '数字经济'];

const filterTabs = [
  { key: 'all', label: '全部' },
  { key: 'news', label: '时事' },
  { key: 'policy', label: '政策' },
];

const filteredResults = computed(() => {
  if (activeFilter.value === 'all') return results.value;
  return results.value.filter(r => r.source_type === activeFilter.value);
});

onMounted(async () => {
  const q = route.query.q;
  if (q) { inputVal.value = q; await doSearch(); }
  loadRecommend();
});

watch(() => route.query.q, (q) => {
  if (q && q !== currentQuery.value) { inputVal.value = q; doSearch(); }
});

async function loadRecommend() {
  try {
    const res = await getCentralDocs(5);
    recentDocs.value = res.data.items || [];
  } catch (e) { console.warn(e); } finally { docsLoading.value = false; }
  try {
    const res = await getHotNews(5);
    recentNews.value = res.data.items || [];
  } catch (e) { console.warn(e); } finally { newsLoading.value = false; }
}

async function doSearch() {
  const q = inputVal.value.trim();
  if (!q) return;
  searching.value = true;
  hasSearched.value = true;
  currentQuery.value = q;
  activeFilter.value = 'all';
  router.replace({ query: { q } });
  try {
    const res = await searchNews(q, 30);
    results.value = res.data.items || [];
  } catch (e) {
    console.warn('搜索失败', e);
    results.value = [];
  } finally {
    searching.value = false;
  }
}

function quickSearch(tag) { inputVal.value = tag; doSearch(); }

function clearSearch() {
  inputVal.value = '';
  hasSearched.value = false;
  results.value = [];
  currentQuery.value = '';
  router.replace({ query: {} });
  inputRef.value?.focus();
}

let _debounceTimer = null;
function onInput() {
  clearTimeout(_debounceTimer);
  _debounceTimer = setTimeout(() => {
    if (inputVal.value.trim().length >= 2) doSearch();
  }, 500);
}

const openLink = (url) => { if (url) window.open(url, '_blank'); };
const formatDate = (d) => { if (!d) return ''; const s = String(d); return s.length > 10 ? s.slice(0, 10) : s; };
const getDomain = (url) => { try { return new URL(url).hostname.replace('www.', ''); } catch { return ''; } };
const highlight = (text) => {
  if (!currentQuery.value || !text) return text;
  const q = currentQuery.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return text.replace(new RegExp(q, 'gi'), m => `<mark>${m}</mark>`);
};
</script>

<style scoped>
.search-page {
  height: 100%;
  overflow-y: auto;
  padding: 24px 32px;
  background: var(--content-bg, #f5f7fa);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ── 搜索栏 ─────────────────────────────────────────────────────────────── */
.search-bar-wrap {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 700px;
  margin: 0 auto;
  width: 100%;
}
.search-bar {
  display: flex;
  align-items: center;
  background: #fff;
  border: 2px solid #e0e0e0;
  border-radius: 14px;
  padding: 0 6px 0 14px;
  gap: 8px;
  transition: border-color 0.2s;
}
.search-bar:focus-within { border-color: #00a8ff; }
.search-icon { color: #aaa; flex-shrink: 0; }
.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 15px;
  padding: 12px 0;
  background: transparent;
  color: #111;
}
.search-input::placeholder { color: #bbb; }
.clear-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #bbb;
  display: flex;
  align-items: center;
  padding: 4px;
  border-radius: 50%;
  transition: color 0.2s;
}
.clear-btn:hover { color: #666; }
.search-btn {
  background: #111;
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 8px 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}
.search-btn:hover:not(:disabled) { background: #333; }
.search-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.hot-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.hot-label { font-size: 12px; color: #aaa; flex-shrink: 0; }
.hot-tag {
  font-size: 12px;
  background: #fff;
  border: 1px solid #e0e0e0;
  color: #555;
  padding: 4px 12px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
}
.hot-tag:hover { border-color: #00a8ff; color: #00a8ff; background: #e6f7ff; }

/* ── 结果区域 ─────────────────────────────────────────────────────────────── */
.results-area { display: flex; flex-direction: column; gap: 12px; }
.results-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.results-count { font-size: 13px; color: #666; }
.results-count strong { color: #111; }
.filter-tabs { display: flex; gap: 4px; }
.filter-tabs button {
  background: #fff;
  border: 1px solid #e0e0e0;
  color: #666;
  padding: 5px 14px;
  border-radius: 20px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}
.filter-tabs button.active { background: #111; color: #fff; border-color: #111; font-weight: 600; }

/* 骨架屏 */
.skeleton-list { display: flex; flex-direction: column; gap: 12px; }
.skeleton-result {
  display: flex;
  gap: 12px;
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid #eee;
}
.sk-type { width: 40px; height: 20px; border-radius: 10px; background: #f0f0f0; flex-shrink: 0; }
.sk-body { flex: 1; display: flex; flex-direction: column; gap: 8px; }
.sk-title { height: 16px; border-radius: 6px; background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%); background-size: 200% 100%; animation: shimmer 1.5s infinite; }
.sk-desc { height: 12px; width: 70%; border-radius: 6px; background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%); background-size: 200% 100%; animation: shimmer 1.5s infinite; }

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 60px 0;
  color: #aaa;
}
.empty-state p { margin: 0; font-size: 16px; font-weight: 600; color: #666; }
.empty-state span { font-size: 13px; }

/* 结果列表 */
.result-list { display: flex; flex-direction: column; gap: 8px; }
.result-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #eee;
  padding: 14px 16px;
  cursor: pointer;
  transition: box-shadow 0.2s, border-color 0.2s;
}
.result-item:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.08); border-color: #d0d0d0; }
.ri-left { flex-shrink: 0; padding-top: 2px; }
.ri-type {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 10px;
}
.type-news { background: #e6f7ff; color: #0077cc; }
.type-policy { background: #fff0f0; color: #c0392b; }
.ri-body { flex: 1; min-width: 0; }
.ri-title {
  margin: 0 0 5px;
  font-size: 14px;
  font-weight: 600;
  color: #111;
  line-height: 1.5;
}
.ri-title :deep(mark) { background: #fff3cd; color: #111; border-radius: 2px; padding: 0 1px; }
.ri-desc {
  margin: 0 0 6px;
  font-size: 12px;
  color: #666;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.ri-desc :deep(mark) { background: #fff3cd; color: #111; border-radius: 2px; padding: 0 1px; }
.ri-meta { display: flex; gap: 12px; align-items: center; }
.ri-date { font-size: 11px; color: #bbb; }
.ri-source { font-size: 11px; color: #00a8ff; }
.ri-right { flex-shrink: 0; padding-top: 4px; }

/* ── 推荐区域 ─────────────────────────────────────────────────────────────── */
.recommend-area {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.rec-section {
  background: #fff;
  border-radius: 16px;
  border: 1px solid #eee;
  padding: 16px;
}
.rec-title { font-size: 14px; font-weight: 700; color: #111; margin: 0 0 12px; }
.rec-list { display: flex; flex-direction: column; gap: 2px; }
.rec-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 9px 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
}
.rec-item:hover { background: #f5f7fa; }
.rec-rank { font-size: 13px; font-weight: 700; color: #ccc; width: 18px; flex-shrink: 0; text-align: center; }
.rec-rank.rank-top { color: #c0392b; }
.rec-content { flex: 1; min-width: 0; }
.rec-text { margin: 0 0 3px; font-size: 13px; color: #222; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.rec-date { font-size: 11px; color: #bbb; }

/* 通用骨架 */
.loading-placeholder { padding: 4px 0; }
.skeleton-line {
  height: 12px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 6px;
  margin-bottom: 10px;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
