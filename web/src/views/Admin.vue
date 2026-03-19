<template>
  <div class="admin-page">
    <div class="admin-header">
      <h1 class="page-title">管理员控制台</h1>
    </div>

    <div v-if="!isAdmin" class="no-permission">无权限访问</div>
    <template v-else>

      <!-- 统计概览 -->
      <div class="stats-row">
        <div class="stat-card">
          <span class="stat-num">{{ stats.total_users ?? '-' }}</span>
          <span class="stat-label">注册用户</span>
        </div>
        <div class="stat-card">
          <span class="stat-num">{{ stats.total_messages ?? '-' }}</span>
          <span class="stat-label">总解析次数</span>
        </div>
        <div class="stat-card">
          <span class="stat-num">{{ stats.active_users ?? '-' }}</span>
          <span class="stat-label">活跃用户</span>
        </div>
      </div>

      <!-- 用户列表 -->
      <div class="section">
        <div class="section-label-row">
          <span class="section-label">用户管理</span>
          <button class="refresh-btn" @click="loadAll">刷新</button>
        </div>
        <div v-if="usersLoading" class="loading-text">加载中...</div>
        <table v-else class="user-table">
          <thead>
            <tr>
              <th>UID</th><th>用户名</th><th>邮箱</th><th>注册时间</th><th>身份</th><th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.uid">
              <td>{{ u.uid }}</td>
              <td>{{ u.uname }}</td>
              <td>{{ u.email }}</td>
              <td>{{ u.created_time?.slice(0, 10) }}</td>
              <td>
                <span :class="u.is_admin ? 'badge-admin' : 'badge-user'">
                  {{ u.is_admin ? '管理员' : '普通用户' }}
                </span>
              </td>
              <td class="action-cell">
                <button class="tbl-btn" @click="toggleAdmin(u.uid)" :disabled="u.uid === selfUid">
                  {{ u.is_admin ? '撤销管理员' : '设为管理员' }}
                </button>
                <button class="tbl-btn danger" @click="deleteUser(u.uid)" :disabled="u.uid === selfUid">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 用户解析量图表 -->
      <div class="section">
        <span class="section-label">各用户解析量</span>
        <div class="bar-list">
          <div v-for="item in stats.user_message_counts || []" :key="item.user_id" class="bar-row">
            <span class="bar-uid">UID {{ item.user_id }}</span>
            <div class="bar-track">
              <div class="bar-fill" :style="{ width: barWidth(item.count) }"></div>
            </div>
            <span class="bar-count">{{ item.count }}</span>
          </div>
        </div>
      </div>

    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { apiClient, API_ROUTES } from '@/router/api_routes.js';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();
const isAdmin = computed(() => userStore.user?.is_admin);
const selfUid = computed(() => userStore.user?.uid);

const users = ref([]);
const stats = ref({});
const usersLoading = ref(true);

onMounted(() => { if (isAdmin.value) loadAll(); });

async function loadAll() {
  usersLoading.value = true;
  try {
    const [usersRes, statsRes] = await Promise.all([
      apiClient.get(API_ROUTES.ADMIN_USERS),
      apiClient.get(API_ROUTES.ADMIN_STATS),
    ]);
    users.value = usersRes.data;
    stats.value = statsRes.data;
  } catch (e) {
    console.warn('管理员数据加载失败', e);
  } finally {
    usersLoading.value = false;
  }
}

async function toggleAdmin(uid) {
  try {
    const res = await apiClient.patch(`/admin/users/${uid}/toggle-admin`);
    const u = users.value.find(u => u.uid === uid);
    if (u) u.is_admin = res.data.is_admin;
  } catch (e) { console.warn(e); }
}

async function deleteUser(uid) {
  if (!confirm('确认删除该用户？此操作不可撤销。')) return;
  try {
    await apiClient.delete(`/admin/users/${uid}`);
    users.value = users.value.filter(u => u.uid !== uid);
  } catch (e) { console.warn(e); }
}

const maxCount = computed(() => Math.max(...(stats.value.user_message_counts || []).map(i => i.count), 1));
const barWidth = (count) => Math.round((count / maxCount.value) * 100) + '%';
</script>

<style scoped>
.admin-page { display: flex; flex-direction: column; gap: 20px; }
.admin-header { display: flex; align-items: center; justify-content: space-between; }
.page-title { font-size: 20px; font-weight: 800; color: #111; margin: 0; }
.no-permission { text-align: center; color: #aaa; padding: 60px 0; font-size: 14px; }

.stats-row { display: flex; gap: 12px; }
.stat-card {
  flex: 1; background: #fff; border: 1px solid #eee; border-top: 3px solid #c0392b;
  padding: 16px; display: flex; flex-direction: column; gap: 4px;
}
.stat-num { font-size: 28px; font-weight: 800; color: #c0392b; line-height: 1; }
.stat-label { font-size: 12px; color: #888; }

.section { background: #fff; border: 1px solid #eee; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
.section-label-row { display: flex; align-items: center; justify-content: space-between; }
.section-label { font-size: 13px; font-weight: 700; color: #111; }
.refresh-btn { background: none; border: 1px solid #ddd; padding: 4px 12px; font-size: 12px; cursor: pointer; }
.refresh-btn:hover { border-color: #c0392b; color: #c0392b; }
.loading-text { color: #aaa; font-size: 13px; }

.user-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.user-table th { text-align: left; padding: 8px 10px; background: #f9f9f9; color: #666; font-weight: 600; border-bottom: 1px solid #eee; }
.user-table td { padding: 8px 10px; border-bottom: 1px solid #f5f5f5; color: #333; }
.badge-admin { background: #c0392b; color: #fff; padding: 2px 8px; font-size: 11px; font-weight: 700; }
.badge-user { background: #f0f0f0; color: #666; padding: 2px 8px; font-size: 11px; }
.action-cell { display: flex; gap: 6px; }
.tbl-btn { background: #f5f5f5; border: none; padding: 4px 10px; font-size: 11px; cursor: pointer; transition: background 0.2s; }
.tbl-btn:hover { background: #e0e0e0; }
.tbl-btn.danger:hover { background: #c0392b; color: #fff; }
.tbl-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.bar-list { display: flex; flex-direction: column; gap: 8px; }
.bar-row { display: flex; align-items: center; gap: 10px; }
.bar-uid { font-size: 12px; color: #888; width: 60px; flex-shrink: 0; }
.bar-track { flex: 1; background: #f5f5f5; height: 12px; }
.bar-fill { height: 100%; background: linear-gradient(to right, #c0392b, #e67e22); transition: width 0.4s; }
.bar-count { font-size: 12px; color: #333; width: 30px; text-align: right; flex-shrink: 0; }
</style>
