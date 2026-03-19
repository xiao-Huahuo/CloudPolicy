<template>
  <div class="sidebar">
    <div class="logo">
      <img src="@/assets/photos/main-icon.png" alt="icon" class="logo-icon" v-if="hasIcon" @error="hasIcon = false" />
      ClearNotify
    </div>
    <nav>
      <router-link to="/" class="nav-item" active-class="active">
        <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" class="nav-icon"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
        主页
      </router-link>
      <router-link to="/feature-a" class="nav-item" active-class="active">
        <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" class="nav-icon"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        发现
      </router-link>
      <router-link to="/feature-b" class="nav-item" active-class="active">
        <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" class="nav-icon"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>
        数据分析
      </router-link>
      <router-link to="/feature-c" class="nav-item" active-class="active">
        <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" class="nav-icon"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
        会话历史
      </router-link>
      <router-link to="/todo" class="nav-item" active-class="active">
        <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" class="nav-icon"><polyline points="9 11 12 14 22 4"></polyline><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path></svg>
        办事进度
      </router-link>
      <router-link v-if="userStore.user?.is_admin" to="/admin" class="nav-item" active-class="active">
        <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" class="nav-icon"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
        管理员
      </router-link>
      <router-link to="/profile" class="nav-item" active-class="active">
        <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" class="nav-icon"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
        我的
      </router-link>
    </nav>
    <div class="sidebar-footer">
      <router-link to="/settings" class="settings-btn" active-class="active" title="设置">
        <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useUserStore } from '@/stores/user';
const hasIcon = ref(true);
const userStore = useUserStore();
</script>

<style scoped>
.sidebar {
  width: 200px;
  background: linear-gradient(180deg, #c0392b 0%, #922b21 60%, #7f8c8d 100%);
  color: #fff;
  height: 100vh;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}

/* 波浪装饰 */
.sidebar::before {
  content: '';
  position: absolute;
  bottom: -30px;
  left: -40px;
  width: 260px;
  height: 260px;
  border-radius: 50%;
  background: rgba(255,255,255,0.05);
  pointer-events: none;
}
.sidebar::after {
  content: '';
  position: absolute;
  top: -60px;
  right: -60px;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: rgba(255,255,255,0.04);
  pointer-events: none;
}

.logo {
  padding: 20px;
  font-size: 18px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #fff;
  letter-spacing: 1px;
  position: relative;
  z-index: 1;
}
.logo-icon { width: 24px; height: 24px; filter: brightness(0) invert(1); }

nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 10px 0;
  position: relative;
  z-index: 1;
}

.nav-item {
  padding: 10px 20px;
  color: rgba(255,255,255,0.75);
  text-decoration: none;
  transition: all 0.2s;
  border-radius: 10px;
  margin: 3px 10px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
}
.nav-item:hover {
  background-color: rgba(255,255,255,0.12);
  color: #fff;
}
.nav-item.active {
  background-color: rgba(255,255,255,0.2);
  color: #fff;
  font-weight: bold;
  box-shadow: inset 3px 0 0 #fff;
}
.nav-item.active .nav-icon { color: #fff; }

.sidebar-footer {
  padding: 20px;
  display: flex;
  align-items: center;
  position: relative;
  z-index: 1;
}
.settings-btn {
  color: rgba(255,255,255,0.6);
  cursor: pointer;
  transition: color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.settings-btn:hover, .settings-btn.active { color: #fff; }
</style>
