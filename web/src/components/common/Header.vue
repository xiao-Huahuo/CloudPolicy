<template>
  <header class="app-header">
    <div class="search-bar">
      <input type="text" v-model="searchQuery" @keyup.enter="handleSearch" placeholder="搜索此功能 (开发中...)" />
      <button class="search-btn" @click="handleSearch">
        <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
      </button>
    </div>

    <div class="user-actions">
      <!-- 通知图标 (对接 settingsStore) -->
      <button class="icon-btn" @click="toggleNotification" :title="settingsStore.settings.system_notifications ? '关闭系统通知' : '开启系统通知'">
        <!-- 开启通知：普通铃铛 -->
        <svg v-if="settingsStore.settings.system_notifications" viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
          <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
        </svg>
        <!-- 关闭通知：带斜杠的铃铛 -->
        <svg v-else viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
          <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
          <path d="M18.63 13A17.89 17.89 0 0 1 18 8"></path>
          <path d="M6.26 6.26A5.86 5.86 0 0 0 6 8c0 7-3 9-3 9h14"></path>
          <path d="M18 8a6 6 0 0 0-9.33-5"></path>
          <line x1="1" y1="1" x2="23" y2="23"></line>
        </svg>
      </button>

      <!-- 用户头像区 -->
      <div class="user-profile" @click="handleUserClick" title="个人中心">
        <img v-if="displayAvatar" :src="displayAvatar" alt="avatar" class="header-avatar" />
        <div v-else class="header-avatar-placeholder">
          <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
        </div>
      </div>

      <!-- 退出登录按钮 (恢复) -->
      <button v-if="userStore.token" class="icon-btn logout-btn" @click="handleLogout" title="退出登录">
        <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
          <polyline points="16 17 21 12 16 7"></polyline>
          <line x1="21" y1="12" x2="9" y2="12"></line>
        </svg>
      </button>
    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import { useSettingsStore } from '@/stores/settings';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const settingsStore = useSettingsStore();

const searchQuery = ref('');

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ path: '/search', query: { q: searchQuery.value } });
  }
};

const displayAvatar = computed(() => {
    if (!userStore.user?.avatar_url) return null;
    const url = userStore.user.avatar_url;
    if (url.startsWith('default:')) {
        const defaultName = url.substring(8);
        return `/src/assets/photos/default-avatars/${defaultName}`;
    }
    return url;
});

const handleUserClick = () => {
  router.push('/profile');
};

const handleLogout = () => {
  if (confirm('确定要退出登录吗？')) {
    userStore.logout();
    router.push('/');
  }
};

const toggleNotification = async () => {
  if (!userStore.token) return;
  // 直接更新 pinia store 并向后端发请求
  settingsStore.settings.system_notifications = !settingsStore.settings.system_notifications;
  await settingsStore.updateSettings({
      system_notifications: settingsStore.settings.system_notifications
  });
};
</script>

<style scoped>
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background-color: var(--header-bg);
  /* 移除边框线，与左侧融为一体 */
}

.search-bar {
  display: flex;
  align-items: center;
  background-color: #f5f7fa;
  border: none; /* 移除搜索框边缘线 */
  border-radius: var(--border-radius-pill); /* 两边圆的圆角矩形 */
  padding: 5px 10px;
  flex: 1;
  max-width: 500px;
  transition: box-shadow 0.3s;
}

.search-bar:focus-within {
  box-shadow: 0 0 0 2px rgba(0,0,0,0.1); /* 用浅阴影代替粗边框 */
}

.search-bar input {
  border: none;
  background: transparent;
  outline: none;
  flex: 1;
  padding: 5px;
  font-size: 14px;
}

.search-btn {
  background: #000; /* 黑色底色 */
  color: #fff; /* 白色文字 */
  border: none;
  border-radius: var(--border-radius-pill); /* 两边圆的圆角矩形 */
  padding: 8px 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.search-btn:hover {
  background: #333;
}

.spacer {
  flex: 1;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #666;
  transition: color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.icon-btn:hover {
  color: #000;
}

.logout-btn:hover {
  color: #f44336; /* 退出按钮悬浮变红 */
}

.user-profile {
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #eee;
}

.header-avatar-placeholder {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
}
</style>
