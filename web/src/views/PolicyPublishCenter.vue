<template>
  <div class="ppc-page">
    <div class="ppc-header">
      <PolicyTitle title="政策发布中心" />
      <p class="ppc-desc">上传标准化政务文件，经管理员审核通过后展示于全景政策广场</p>
    </div>

    <div v-if="!userStore.isCertified && !userStore.isAdmin" class="no-perm">
      <svg viewBox="0 0 24 24" width="48" height="48" stroke="#ccc" stroke-width="1.5" fill="none"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      <p>需要认证主体权限才能访问此页面</p>
    </div>

    <template v-else>
      <div class="ppc-layout">
        <!-- 左：上传表单 -->
        <div class="form-panel">
          <div class="panel-title"><span class="dot"></span>发布新政务文件</div>

          <div class="form-group">
            <label>文件标题 <span class="required">*</span></label>
            <input v-model="form.title" placeholder="请输入政务文件标题" class="form-input" maxlength="100" />
            <span class="char-count">{{ form.title.length }}/100</span>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>分类</label>
              <select v-model="form.category" class="form-input">
                <option value="">请选择分类</option>
                <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>标签 <span class="hint">（逗号分隔）</span></label>
              <input v-model="form.tags" placeholder="如：政策,补贴,企业" class="form-input" />
            </div>
          </div>

          <div class="form-group">
            <label>文件正文 <span class="required">*</span></label>
            <textarea v-model="form.content" placeholder="请输入政务文件正文内容..." class="form-textarea" rows="10" maxlength="5000"></textarea>
            <span class="char-count">{{ form.content.length }}/5000</span>
          </div>

          <div class="form-actions">
            <button class="reset-btn" @click="resetForm">重置</button>
            <button class="submit-btn" @click="submitDoc" :disabled="submitting || !form.title || !form.content">
              <AgentLoader v-if="submitting" :size="18" compact />
              {{ submitting ? '提交中...' : '提交审核' }}
            </button>
          </div>

          <transition name="toast-fade">
            <div v-if="toast.show" class="toast" :class="toast.type">{{ toast.msg }}</div>
          </transition>
        </div>

        <!-- 右：我的文件列表 -->
        <div class="list-panel">
          <div class="panel-title-row">
            <div class="panel-title"><span class="dot"></span>我的文件</div>
            <button class="refresh-btn" @click="loadMyDocs">
              <svg viewBox="0 0 24 24" width="13" height="13" stroke="currentColor" stroke-width="2" fill="none"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
              刷新
            </button>
          </div>

          <div class="status-tabs">
            <button v-for="tab in statusTabs" :key="tab.value"
              class="stab" :class="{ active: activeTab === tab.value }"
              @click="activeTab = tab.value">
              {{ tab.label }}
              <span class="stab-count">{{ tabCount(tab.value) }}</span>
            </button>
          </div>

          <div v-if="listLoading" class="list-loading">
            <div v-for="i in 3" :key="i" class="skeleton-row"></div>
          </div>
          <transition-group v-else name="list-fade" tag="div" class="doc-list">
            <div v-for="doc in filteredDocs" :key="doc.id" class="doc-item">
              <div class="di-top">
                <span class="di-status" :class="doc.status">{{ statusLabel(doc.status) }}</span>
                <span class="di-date">{{ formatDate(doc.created_time) }}</span>
              </div>
              <p class="di-title">{{ doc.title }}</p>
              <div class="di-meta">
                <span v-if="doc.category" class="di-cat">{{ doc.category }}</span>
                <span v-for="tag in docTags(doc.tags)" :key="`${doc.id}-${tag}`" class="di-tag-text">{{ tag }}</span>
                <span class="di-stat">
                  <svg viewBox="0 0 24 24" width="11" height="11" stroke="currentColor" stroke-width="2" fill="none"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  {{ doc.view_count }}
                </span>
                <span class="di-stat">
                  <svg viewBox="0 0 24 24" width="11" height="11" stroke="currentColor" stroke-width="2" fill="none"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3H14z"/></svg>
                  {{ doc.like_count }}
                </span>
              </div>
              <p v-if="doc.reject_reason" class="di-reject">拒绝原因：{{ doc.reject_reason }}</p>
            </div>
          </transition-group>
          <div v-if="!listLoading && !filteredDocs.length" class="empty-tip">暂无文件</div>
        </div>
      </div>

      <!-- 审核流程说明 -->
      <div class="flow-section">
        <div class="panel-title"><span class="dot"></span>审核流程</div>
        <div class="flow-steps">
          <div v-for="(step, i) in flowSteps" :key="i" class="flow-step">
            <div class="fs-num">{{ i + 1 }}</div>
            <div class="fs-icon">
              <svg viewBox="0 0 24 24" width="20" height="20" :stroke="step.color" stroke-width="2" fill="none" v-html="step.icon"></svg>
            </div>
            <div class="fs-text">
              <span class="fs-title">{{ step.title }}</span>
              <span class="fs-desc">{{ step.desc }}</span>
            </div>
            <div v-if="i < flowSteps.length - 1" class="fs-arrow">→</div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import PolicyTitle from '@/components/common/PolicyTitle.vue'
import AgentLoader from '@/components/ui/AgentLoader.vue'
import { useUserStore } from '@/stores/auth.js'
import { apiClient, API_ROUTES } from '@/router/api_routes'

const userStore = useUserStore()

const form = ref({ title: '', category: '', tags: '', content: '' })
const submitting = ref(false)
const myDocs = ref([])
const listLoading = ref(false)
const activeTab = ref('all')
const toast = ref({ show: false, msg: '', type: 'success' })

const categories = ['数字化', '惠企政策', '医疗卫生', '乡村振兴', '市场监管', '教育', '社会保障', '环境保护', '交通建设', '其他']

const statusTabs = [
  { label: '全部', value: 'all' },
  { label: '待审核', value: 'pending' },
  { label: '已通过', value: 'approved' },
  { label: '已拒绝', value: 'rejected' },
]

const flowSteps = [
  { title: '填写并提交', desc: '填写文件标题、分类、正文', color: '#2980b9', icon: '<path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>' },
  { title: '等待审核', desc: '管理员在1-3个工作日内审核', color: '#e67e22', icon: '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>' },
  { title: '审核通过', desc: '文件出现在全景政策广场', color: '#27ae60', icon: '<polyline points="20 6 9 17 4 12"/>' },
  { title: '智能解析', desc: '系统自动解析并纳入数据统计', color: '#8e44ad', icon: '<rect x="3" y="3" width="18" height="14" rx="2"/><path d="M7 21h10"/>' },
]

const filteredDocs = computed(() => {
  if (activeTab.value === 'all') return myDocs.value
  return myDocs.value.filter(d => d.status === activeTab.value)
})

const tabCount = (tab) => tab === 'all' ? myDocs.value.length : myDocs.value.filter(d => d.status === tab).length

const statusLabel = (s) => ({ approved: '已通过', pending: '待审核', rejected: '已拒绝' }[s] || s)

const docTags = (tags) => {
  if (!tags) return []
  return String(tags).split(',').map((tag) => tag.trim()).filter(Boolean)
}

const formatDate = (t) => {
  if (!t) return ''
  return new Date(t).toLocaleDateString('zh-CN')
}

const showToast = (msg, type = 'success') => {
  toast.value = { show: true, msg, type }
  setTimeout(() => { toast.value.show = false }, 3000)
}

const resetForm = () => { form.value = { title: '', category: '', tags: '', content: '' } }

const submitDoc = async () => {
  if (!form.value.title.trim() || !form.value.content.trim()) return
  submitting.value = true
  try {
    await apiClient.post(API_ROUTES.POLICY_DOC_CREATE, form.value)
    showToast('提交成功，等待管理员审核')
    resetForm()
    await loadMyDocs()
  } catch (e) {
    showToast(e.response?.data?.detail || '提交失败', 'error')
  } finally {
    submitting.value = false
  }
}

const loadMyDocs = async () => {
  listLoading.value = true
  try {
    const res = await apiClient.get(API_ROUTES.POLICY_DOCS_MINE)
    myDocs.value = res.data
  } catch (e) { console.error(e) }
  finally { listLoading.value = false }
}

onMounted(() => {
  if (userStore.isCertified || userStore.isAdmin) loadMyDocs()
})
</script>

<style scoped>
.ppc-page { padding: 30px; max-width: 1200px; margin: 0 auto; }
.ppc-header { margin-bottom: 24px; }
.ppc-desc { color: var(--text-secondary, #666); font-size: 14px; margin: 6px 0 0; }

.no-perm { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 80px; color: #999; gap: 16px; }

.ppc-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }

/* 面板通用 */
.form-panel, .list-panel {
  background: var(--card-bg, #fff);
  border: 1px solid var(--border-color, #e8e8e8);
  padding: 24px;
}
.panel-title { display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 15px; margin-bottom: 20px; }
.panel-title-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.panel-title-row .panel-title { margin-bottom: 0; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: var(--color-primary, #c0392b); flex-shrink: 0; }

/* 表单 */
.form-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; position: relative; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
label { font-size: 13px; font-weight: 600; color: var(--text-primary, #111); }
.required { color: #c0392b; }
.hint { font-weight: normal; color: #999; font-size: 11px; }
.form-input, .form-textarea {
  border: 1px solid var(--border-color, #e0e0e0);
  border-radius: 6px; padding: 10px 12px;
  font-size: 14px; color: var(--text-primary, #111);
  background: var(--card-bg, #fff);
  transition: border-color 0.2s, box-shadow 0.2s;
  outline: none; width: 100%; box-sizing: border-box;
}
.form-input:focus, .form-textarea:focus {
  border-color: var(--color-primary, #c0392b);
  box-shadow: 0 0 0 3px rgba(192,57,43,0.1);
}
.form-textarea { resize: vertical; min-height: 200px; font-family: inherit; line-height: 1.6; }
.char-count { font-size: 11px; color: #999; text-align: right; }

.form-actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 8px; }
.reset-btn {
  padding: 10px 24px; border: 1px solid var(--border-color, #e0e0e0);
  border-radius: 6px; background: none; cursor: pointer;
  font-size: 14px; color: var(--text-secondary, #666); transition: all 0.2s;
}
.reset-btn:hover { border-color: #999; color: var(--text-primary, #111); }
.submit-btn {
  padding: 10px 28px; background: var(--color-primary, #c0392b);
  color: #fff; border: none; border-radius: 6px; cursor: pointer;
  font-size: 14px; font-weight: 600; transition: all 0.2s;
  display: flex; align-items: center; gap: 8px;
}
.submit-btn:hover:not(:disabled) { background: var(--color-primary-light, #e74c3c); transform: translateY(-1px); box-shadow: 0 4px 12px rgba(192,57,43,0.3); }
.submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.spinner {
  width: 14px; height: 14px; border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff; border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.toast {
  margin-top: 12px; padding: 10px 16px; border-radius: 6px;
  font-size: 13px; font-weight: 500;
}
.toast.success { background: #e8f5e9; color: #2e7d32; }
.toast.error { background: #fce4e4; color: #c0392b; }
.toast-fade-enter-active, .toast-fade-leave-active { transition: all 0.3s; }
.toast-fade-enter-from, .toast-fade-leave-to { opacity: 0; transform: translateY(-8px); }

/* 文件列表 */
.refresh-btn {
  display: flex; align-items: center; gap: 4px;
  background: none; border: 1px solid var(--border-color, #e0e0e0);
  padding: 5px 10px; border-radius: 4px; font-size: 12px; cursor: pointer; color: #666;
  transition: all 0.2s;
}
.refresh-btn:hover { border-color: var(--color-primary, #c0392b); color: var(--color-primary, #c0392b); }

.status-tabs { display: flex; gap: 4px; margin-bottom: 16px; flex-wrap: wrap; }
.stab {
  padding: 5px 12px; border: 1px solid var(--border-color, #e0e0e0);
  border-radius: 20px; background: none; cursor: pointer;
  font-size: 12px; color: #666; transition: all 0.2s;
  display: flex; align-items: center; gap: 4px;
}
.stab.active { background: var(--color-primary, #c0392b); color: #fff; border-color: var(--color-primary, #c0392b); }
.stab-count {
  background: rgba(0,0,0,0.1); border-radius: 10px;
  padding: 0 6px; font-size: 11px;
}
.stab.active .stab-count { background: rgba(255,255,255,0.25); }

.doc-list { display: flex; flex-direction: column; gap: 10px; max-height: 480px; overflow-y: auto; }
.doc-item {
  border: 1px solid var(--border-color, #e8e8e8);
  padding: 12px 14px; transition: box-shadow 0.2s, border-color 0.2s;
}
.doc-item:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.06);
  border-color: color-mix(in srgb, var(--color-primary, #c0392b) 24%, var(--border-color, #e8e8e8));
}
.di-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.di-status { font-size: 11px; font-weight: 700; letter-spacing: 0.02em; }
.di-status.approved { color: #2e7d32; }
.di-status.pending { color: #f57f17; }
.di-status.rejected { color: #c0392b; }
.di-date { font-size: 11px; color: #999; }
.di-title { font-size: 14px; font-weight: 600; margin: 0 0 8px; line-height: 1.4; }
.di-meta { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.di-cat,
.di-tag-text {
  font-size: 11px;
  color: var(--text-secondary, #666);
}
.di-stat { display: flex; align-items: center; gap: 3px; font-size: 12px; color: #999; }
.di-reject { font-size: 12px; color: #c0392b; margin: 6px 0 0; padding: 6px 10px; background: #fce4e4; border-radius: 4px; }

.skeleton-row {
  height: 80px; background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%; animation: shimmer 1.5s infinite;
  border-radius: 4px; margin-bottom: 10px;
}
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

/* 审核流程 */
.flow-section {
  background: var(--card-bg, #fff);
  border: 1px solid var(--border-color, #e8e8e8);
  padding: 24px;
}
.flow-steps { display: flex; align-items: center; gap: 0; margin-top: 16px; flex-wrap: wrap; }
.flow-step {
  display: flex; align-items: center; gap: 12px;
  flex: 1; min-width: 180px;
}
.fs-num {
  width: 28px; height: 28px; border-radius: 50%;
  background: var(--color-primary, #c0392b); color: #fff;
  font-size: 13px; font-weight: 700;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.fs-icon {
  width: 40px; height: 40px; border-radius: 10px;
  background: var(--content-bg, #f4f5f7);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.fs-text { display: flex; flex-direction: column; gap: 3px; }
.fs-title { font-size: 13px; font-weight: 700; }
.fs-desc { font-size: 11px; color: #999; }
.fs-arrow { font-size: 20px; color: #ccc; padding: 0 8px; flex-shrink: 0; }

.empty-tip { text-align: center; color: #999; padding: 30px; font-size: 13px; }
.list-fade-enter-active { transition: all 0.3s ease; }
.list-fade-enter-from { opacity: 0; transform: translateY(8px); }
</style>
