<template>
  <header class="app-header">
    <div class="search-bar">
      <input type="text" placeholder="Search..." v-model="searchQuery" @keyup.enter="handleSearch" />
      <button @click="handleSearch" class="search-btn">
        Search
      </button>
    </div>
    <div class="header-right">
      <div class="user-profile">
        <!-- 未登录状态：触发全局事件以打开模态框，而不是路由跳转 -->
        <button v-if="!userStore.token" @click="emitLoginEvent" class="login-capsule">
          登录
        </button>

        <!-- 已登录状态：显示用户名和注销按钮 -->
        <template v-else>
          <span class="welcome-text">Welcome, {{ userStore.user?.uname }}</span>
          <button @click="handleLogout" class="logout-btn" title="退出登录">
            <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16 17 21 12 16 7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
          </button>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';

const searchQuery = ref('');
const router = useRouter();
const userStore = useUserStore();

// 创建一个自定义事件派发器，用于通知父组件或全局总线打开登录弹窗
const emitLoginEvent = () => {
  // 最佳实践：使用原生的 Event 派发机制
  window.dispatchEvent(new CustomEvent('open-login-modal'));
};

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ path: '/search', query: { q: searchQuery.value } });
  }
};

const handleLogout = () => {
  userStore.logout();
  // 不强制跳走，或者看需求。为了稳妥回到主页
  router.push('/');
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
  border-radius: var(--border-radius-pill);
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
  padding-left: 10px;
}

.search-btn {
  background: #000;
  color: #fff;
  border: none;
  border-radius: var(--border-radius-pill);
  padding: 8px 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  font-weight: bold;
  font-size: 14px;
  transition: transform 0.2s, background-color 0.2s;
}

.search-btn:hover {
  background-color: #333;
  transform: scale(1.05);
}

.header-right {
  display: flex;
  align-items: center;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 15px;
}

.welcome-text {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.login-capsule {
  background-color: #000;
  color: #fff;
  border: none;
  padding: 8px 20px;
  border-radius: var(--border-radius-pill);
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: opacity 0.2s;
}

.login-capsule:hover {
  opacity: 0.8;
}

.logout-btn {
  background-color: #e53935;
  color: #fff;
  border: none;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: var(--border-radius-pill);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.logout-btn:hover {
  background-color: #c62828;
}
</style>
