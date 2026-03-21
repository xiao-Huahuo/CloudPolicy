<template>
  <div class="favorites-container">
    <div class="header-section">
      <h1 class="page-title">我的收藏</h1>
    </div>

    <div v-if="loading" class="empty-state">加载中...</div>
    <div v-else-if="items.length === 0" class="empty-state">暂无收藏</div>

    <div v-else class="favorites-grid">
      <div v-for="item in items" :key="item.fav.id" class="favorite-card">
        <div class="card-header">
          <h3 class="card-title">{{ item.message?.handling_matter || formatName(item.message?.original_text) }}</h3>
          <span class="card-time">{{ formatDate(item.fav.created_time) }}</span>
        </div>
        <div class="card-body">
          <p class="card-text">{{ formatPreview(item.message?.original_text) }}</p>
          <div class="card-tags">
            <span class="tag">{{ item.message?.chat_analysis?.notice_type || '文档' }}</span>
            <span class="tag subtle">{{ item.message?.target_audience || '未知对象' }}</span>
          </div>
        </div>
        <div class="card-actions">
          <button class="action-btn" @click="openDetail(item.message)">查看详情</button>
          <button class="action-btn danger" @click="removeFavorite(item.fav.id)">取消收藏</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { apiClient, API_ROUTES } from '@/router/api_routes.js';
import { useUserStore } from '@/stores/auth.js';

const userStore = useUserStore();
const router = useRouter();
const loading = ref(true);
const items = ref([]);

const formatDate = (dateString) => {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return `${date.getMonth() + 1}-${date.getDate()} ${date.getHours()}:${date.getMinutes()}`;
};

const formatName = (text) => {
  if (!text) return '未命名';
  const cleanText = text.replace(/\s+/g, ' ');
  return cleanText.length > 16 ? cleanText.substring(0, 16) + '...' : cleanText;
};

const formatPreview = (text) => {
  if (!text) return '暂无内容';
  const cleanText = text.replace(/\s+/g, ' ');
  return cleanText.length > 120 ? cleanText.substring(0, 120) + '...' : cleanText;
};

const fetchFavorites = async () => {
  if (!userStore.token) {
    alert('请先登录查看收藏');
    loading.value = false;
    return;
  }
  try {
    const favRes = await apiClient.get(API_ROUTES.FAVORITE);
    const favList = favRes.data || [];
    const messageTasks = favList.map((fav) =>
      apiClient.get(`${API_ROUTES.CHAT_MESSAGE}${fav.chat_message_id}`)
        .then(res => ({ fav, message: res.data }))
        .catch(() => ({ fav, message: null }))
    );
    items.value = await Promise.all(messageTasks);
  } catch (e) {
    console.error('获取收藏失败', e);
  } finally {
    loading.value = false;
  }
};

const removeFavorite = async (favId) => {
  try {
    await apiClient.delete(`${API_ROUTES.FAVORITE}${favId}`);
    items.value = items.value.filter(item => item.fav.id !== favId);
  } catch (e) {
    alert('取消收藏失败');
  }
};

const openDetail = async (message) => {
  if (!message?.id) return;
  try {
    const res = await apiClient.get(`${API_ROUTES.CHAT_MESSAGE}${message.id}`);
    sessionStorage.setItem('restoredChatMessage', JSON.stringify(res.data));
    router.push('/');
  } catch (e) {
    alert('打开详情失败');
  }
};

onMounted(fetchFavorites);
</script>

<style scoped>
.favorites-container {
  padding: 20px 30px;
  height: 100%;
  box-sizing: border-box;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  margin: 0 0 20px 0;
  color: #111;
}

.empty-state {
  color: #999;
  padding: 40px 0;
  text-align: center;
}

.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.favorite-card {
  background: #fff;
  border: 1px solid #eee;
  border-top: 3px solid #c0392b;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.card-title {
  font-size: 14px;
  margin: 0;
  font-weight: 700;
  color: #111;
}

.card-time {
  font-size: 11px;
  color: #999;
}

.card-text {
  margin: 0;
  font-size: 12px;
  color: #444;
  line-height: 1.5;
}

.card-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tag {
  background: #111;
  color: #fff;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 12px;
}

.tag.subtle {
  background: #f0f0f0;
  color: #555;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  border: 1px solid #ddd;
  background: #fff;
  color: #333;
  padding: 6px 10px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  border-color: #c0392b;
  color: #c0392b;
}

.action-btn.danger {
  border-color: #f1c1c1;
  color: #c0392b;
}

.action-btn.danger:hover {
  background: #fff0f0;
}
</style>
