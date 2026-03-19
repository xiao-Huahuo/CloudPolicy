<template>
  <header class="app-header">
    <div class="search-bar" v-if="showSearch">
      <input type="text" v-model="searchQuery" @keyup.enter="handleSearch" placeholder="搜索文档..." />
      <button class="search-btn" @click="handleSearch">
        <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
      </button>
    </div>
    <div class="spacer" v-else></div>

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
        <button v-if="!userStore.token" @click.stop="emitLoginEvent" class="login-capsule">登录</button>
        <template v-else>
            <img v-if="displayAvatar" :src="displayAvatar" alt="avatar" class="header-avatar" />
            <div v-else class="header-avatar-placeholder">
              <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
            </div>
        </template>
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

// 某些页面可能不需要搜索栏
const showSearch = computed(() => {
  return route.name !== 'login' && route.name !== 'register';
});

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

const emitLoginEvent = () => {
  window.dispatchEvent(new CustomEvent('open-login-modal'));
};

const handleUserClick = () => {
  if (userStore.token) {
    router.push('/profile');
  }
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
  height: 56px;
  background: linear-gradient(90deg, #c0392b 0%, #7f8c8d 100%);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  flex-shrink: 0;
}

.search-bar {
  display: flex;
  align-items: center;
  background-color: rgba(255,255,255,0.18);
  border: 1px solid rgba(255,255,255,0.25);
  border-radius: var(--border-radius-pill);
  padding: 5px 10px;
  width: 300px;
  transition: background 0.3s;
}
.search-bar:focus-within {
  background-color: rgba(255,255,255,0.28);
}

.search-bar input {
  border: none;
  background: transparent;
  outline: none;
  flex: 1;
  padding: 5px;
  font-size: 14px;
  color: #fff;
}
.search-bar input::placeholder { color: rgba(255,255,255,0.65); }

.search-btn {
  background: none;
  color: rgba(255,255,255,0.8);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}
.search-btn:hover { color: #fff; }

.spacer { flex: 1; }

.user-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: rgba(255,255,255,0.85);
  transition: color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.icon-btn:hover { color: #fff; }
.logout-btn:hover { color: rgba(255,255,255,0.7); }

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
  border: 2px solid rgba(255,255,255,0.5);
}

.header-avatar-placeholder {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: rgba(255,255,255,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255,255,255,0.8);
}

.login-capsule {
  background-color: rgba(255,255,255,0.2);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.4);
  padding: 8px 20px;
  border-radius: var(--border-radius-pill);
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}

.login-capsule:hover { background-color: rgba(255,255,255,0.35); }
</style>
