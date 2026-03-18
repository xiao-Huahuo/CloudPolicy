<template>
  <div class="home-container">
    <!-- 标题区域 (始终显示) -->
    <div class="hero-section" v-if="!showResult">
      <div class="title-with-icon">
        <h1 class="main-title">文档解析</h1>
      </div>
      <p class="sub-title">全格式兼容-精准提取-详细输出</p>
    </div>

    <!-- 初始视图：上传区 -->
    <div v-if="!showResult" class="initial-view">
      <!-- 上传区域 -->
      <div
        class="upload-area"
        @click="triggerFileUpload"
        @dragover.prevent
        @drop.prevent="handleDrop"
        :class="{ 'disabled': loading }"
      >
        <div class="upload-buttons">
          <button class="action-btn" @click.stop="triggerFileUpload" :disabled="loading">
            本地上传
          </button>
          <button class="action-btn" @click.stop="handleUrlUpload" :disabled="loading">
            URL上传
          </button>
          <button class="action-btn" @click.stop="handleScreenshot" :disabled="loading">
            截图
          </button>
        </div>
        <p class="upload-hint">点击或拖拽上传 (支持 TXT, PDF, Word, Excel)</p>

        <!-- 隐藏的文件输入框 -->
        <input
          type="file"
          ref="fileInput"
          style="display: none"
          @change="handleFileUpload"
          accept=".txt,.pdf,.doc,.docx,.xls,.xlsx"
        />
      </div>

      <!-- 加载中小横幅 -->
      <div v-if="loading" class="loading-banner">
        <span>正在智能解读中...</span>
      </div>

      <!-- 恢复示例区域 -->
      <div class="examples-section">
        <h2 class="section-title">示例</h2>
        <div class="examples-grid">
          <div v-for="ex in examples" :key="ex.id" class="example-card">
            <div class="card-image">
              <div class="placeholder-img">IMG</div>
            </div>
            <div class="card-content">
              <h3 class="card-title">{{ ex.title }}</h3>
              <div class="card-tags">
                <span v-for="tag in ex.tags" :key="tag" class="tag">{{ tag }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 结果视图 -->
    <div v-else class="result-view">
      <div class="result-header">
        <button @click="resetView" class="back-btn">
          <span class="icon">←</span> 返回
        </button>
        <h2>解读结果</h2>
      </div>

      <!-- 解析结果展示卡片 -->
      <div class="response-section" v-if="aiResponse">
        <!-- 固定的表头部分 -->
        <div class="fixed-result-header">
          <div class="header-top-row">
             <h3 class="result-title">{{ aiResponse.handling_matter || '未知事项' }}</h3>
             <div class="tags-container">
                <span class="highlight-tag" v-if="aiResponse.target_audience">{{ aiResponse.target_audience }}</span>
                <span class="info-tag" v-if="aiResponse.chat_analysis?.notice_type">{{ aiResponse.chat_analysis.notice_type }}</span>
             </div>
          </div>
        </div>

        <div class="scrollable-content">
          <!-- 左右分栏 -->
          <div class="result-grid">
            <!-- 左侧：具体信息提取 -->
            <div class="info-list">
               <div class="info-item" v-if="aiResponse.time_deadline">
                  <div class="info-text">
                    <strong>办理时间：</strong>
                    <p>{{ aiResponse.time_deadline }}</p>
                  </div>
               </div>

               <div class="info-item" v-if="aiResponse.location_entrance">
                  <div class="info-text">
                    <strong>办理地点/入口：</strong>
                    <p>{{ aiResponse.location_entrance }}</p>
                  </div>
               </div>

               <div class="info-item" v-if="aiResponse.required_materials">
                  <div class="info-text">
                    <strong>所需材料：</strong>
                    <p>{{ aiResponse.required_materials }}</p>
                  </div>
               </div>

               <div class="info-item" v-if="aiResponse.handling_process">
                  <div class="info-text">
                    <strong>办理流程：</strong>
                    <div class="process-text">{{ aiResponse.handling_process }}</div>
                  </div>
               </div>
            </div>

            <!-- 右侧：原文、注意事项、风险提醒、改写、难度分析 -->
            <div class="right-panel">

               <!-- 注意事项和风险提醒移到上方 -->
               <div class="warning-panel">
                 <div class="warning-box" v-if="aiResponse.precautions">
                    <h4>注意事项</h4>
                    <p>{{ aiResponse.precautions }}</p>
                 </div>
                 <div class="warning-box" v-if="aiResponse.risk_warnings">
                    <h4>风险提醒</h4>
                    <p>{{ aiResponse.risk_warnings }}</p>
                 </div>
               </div>

               <!-- 难度分析横条放在改写上面 -->
               <div class="analysis-dashboard" v-if="aiResponse.chat_analysis">
                  <div class="dashboard-item">
                     <span class="label">语言复杂度: </span>
                     <span class="value text-only" :class="getComplexityClass(aiResponse.chat_analysis.language_complexity)">
                       {{ aiResponse.chat_analysis.language_complexity || '未知' }}
                     </span>
                  </div>
                  <div class="dashboard-item">
                     <span class="label">办理复杂度: </span>
                     <span class="value text-only" :class="getComplexityClass(aiResponse.chat_analysis.handling_complexity)">
                       {{ aiResponse.chat_analysis.handling_complexity || '未知' }}
                     </span>
                  </div>
                  <div class="dashboard-item">
                     <span class="label">风险等级: </span>
                     <span class="value text-only" :class="getComplexityClass(aiResponse.chat_analysis.risk_level)">
                       {{ aiResponse.chat_analysis.risk_level || '未知' }}
                     </span>
                  </div>
               </div>

               <!-- 切换改写版本 -->
               <div class="rewrite-toolbar">
                  <span>切换改写版本：</span>
                  <div class="rewrite-buttons">
                    <button class="rewrite-btn" @click="rewriteTarget('老人版')" :disabled="isRewriting">老人版</button>
                    <button class="rewrite-btn" @click="rewriteTarget('学生版')" :disabled="isRewriting">学生版</button>
                    <button class="rewrite-btn" @click="rewriteTarget('家属转述版')" :disabled="isRewriting">家属转述版</button>
                    <button class="rewrite-btn" @click="rewriteTarget('极简版')" :disabled="isRewriting">极简版</button>
                    <button class="rewrite-btn" @click="rewriteTarget('客服答复版')" :disabled="isRewriting">客服答复版</button>
                  </div>
                  <span v-if="isRewriting" class="rewriting-status">正在生成...</span>
               </div>

               <!-- 原文独占右侧下部 -->
               <div class="original-text-section" v-if="aiResponse.original_text">
                 <h4>原文</h4>
                 <div class="original-content">
                   {{ aiResponse.original_text }}
                 </div>
               </div>

               <!-- 原文映射作为参考，如果有的话 -->
               <div class="mapping-section" v-if="aiResponse.file_url">
                  <h4>原文件参考</h4>
                  <a :href="aiResponse.file_url" target="_blank" class="file-link">点击查看上传的原文件</a>
               </div>
               <div class="mapping-section" v-else-if="aiResponse.original_text_mapping">
                  <h4>对应位置参考</h4>
                  <p>{{ aiResponse.original_text_mapping }}</p>
               </div>

            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 弹窗：通过 CSS 将整个屏幕蒙在一个灰色遮罩里，并将表单居中 -->
    <Modal :isOpen="showModal" @close="closeModal">
      <!-- 这个容器包裹了图标、标题和表单，在切换时由于 key 的存在，整个容器会平滑过渡 -->
      <div class="auth-modal-content">
        <div class="logo-area-transition">
          <h1 class="logo-text">ClearNotify</h1>
        </div>

        <!-- 使用动态高度包裹容器来实现上下平滑撑开 -->
        <!-- 修改这里：将 transition 放在相对定位包裹层的外层，或者是调整其绝对定位的 top/bottom 以实现上下移动，同时还要有高度变化 -->
        <div class="form-transition-container" :style="{ height: containerHeight + 'px' }">
          <transition
            name="form-slide"
            @before-enter="onBeforeEnter"
            @enter="onEnter"
            @after-enter="onAfterEnter"
            @leave="onLeave"
          >
            <!-- 使用绝对定位来实现平滑滑动切换，避免高度瞬间变化和挤压 -->
            <div v-if="currentForm === 'login'" class="form-wrapper login-wrapper-abs" key="login">
              <LoginForm
                @success="handleLoginSuccess"
                @switch-to-register="currentForm = 'register'"
              />
            </div>
            <div v-else-if="currentForm === 'register'" class="form-wrapper register-wrapper-abs" key="register">
              <RegisterForm
                @switch-to-login="currentForm = 'login'"
                @success="handleLoginSuccess"
              />
            </div>
          </transition>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { useUserStore } from '@/stores/user';
import { createChatMessage, createChatMessageWithFile, uploadAndExtractDocument, rewriteChatMessage } from '@/api/ai';
import { useRouter } from 'vue-router';
import Modal from '@/components/common/Modal.vue';
import LoginForm from '@/components/Home/LoginForm.vue';
import RegisterForm from '@/components/Home/RegisterForm.vue';

const userStore = useUserStore();
const router = useRouter();
const inputText = ref('');
const aiResponse = ref(null);
const loading = ref(false);
const isRewriting = ref(false);
const showResult = ref(false);
const fileInput = ref(null);

const showModal = ref(false);
const currentForm = ref('login');
const containerHeight = ref(350); // 默认登录框高度

// 用于动画平滑改变高度
const onBeforeEnter = (el) => {
  el.style.opacity = 0;
};

const onEnter = (el, done) => {
  // 在 DOM 更新后获取新表单的实际高度
  nextTick(() => {
    containerHeight.value = el.offsetHeight;
    el.style.opacity = 1;
    done();
  });
};

const onAfterEnter = (el) => {
  el.style.opacity = '';
};

const onLeave = (el, done) => {
  el.style.opacity = 0;
  setTimeout(done, 400); // 等待 CSS 动画结束
};

onMounted(() => {
  if (userStore.token) {
    userStore.fetchUser();
  }
  window.addEventListener('open-login-modal', openLoginModal);
});

const examples = ref([
  { id: 1, title: '社区通知', tags: ['通知', '民生', '公告'] },
  { id: 2, title: '政务文件', tags: ['政策', '解读', '官方'] },
  { id: 3, title: '学校通知', tags: ['教育', '学生', '家长'] },
]);

const openLoginModal = () => {
  currentForm.value = 'login';
  containerHeight.value = 350; // 重置高度
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

const handleLoginSuccess = () => {
  closeModal();
};

const triggerFileUpload = () => {
  if (loading.value) return;

  if (!userStore.token) {
    openLoginModal();
    return;
  }

  fileInput.value.click();
};

const handleFileUpload = (event) => {
  const file = event.target.files[0];
  processFile(file);
};

const handleDrop = (event) => {
  if (loading.value) return;

  if (!userStore.token) {
    openLoginModal();
    return;
  }

  const file = event.dataTransfer.files[0];
  processFile(file);
};

const processFile = async (file) => {
  if (!file) return;

  loading.value = true;
  aiResponse.value = null;

  try {
    // 1. 上传文件到后端提取文本并获取 URL
    const uploadRes = await uploadAndExtractDocument(file);
    const { extracted_text, file_url } = uploadRes.data;

    // 2. 将提取的文本连同 file_url 提交给大模型进行解析
    const chatRes = await createChatMessageWithFile(extracted_text, file_url);
    aiResponse.value = chatRes.data;
    showResult.value = true;
  } catch (error) {
    console.error(error);
    if (error.response?.status === 401) {
       userStore.logout();
       openLoginModal();
    } else {
       alert('文件处理失败: ' + (error.response?.data?.detail || error.message));
    }
  } finally {
    loading.value = false;
    if (fileInput.value) {
       fileInput.value.value = ''; // 清空 input 允许重复上传相同文件
    }
  }
};

const handleUrlUpload = () => {
  if (loading.value) return;

  if (!userStore.token) {
    openLoginModal();
    return;
  }

  const url = prompt("请输入 URL:");
  if (url) {
    inputText.value = `URL: ${url}`;
    submitToAI();
  }
};

const handleScreenshot = () => {
  if (!userStore.token) {
    openLoginModal();
    return;
  }
  alert("截图功能开发中...");
};

const submitToAI = async () => {
  if (!userStore.token) {
    openLoginModal();
    return;
  }

  if (!inputText.value.trim()) {
    return;
  }

  loading.value = true;
  aiResponse.value = null;

  try {
    const response = await createChatMessage(inputText.value);
    aiResponse.value = response.data;
    showResult.value = true;
  } catch (error) {
    console.error(error);
    if (error.response?.status === 401) {
       userStore.logout();
       openLoginModal();
    } else {
       alert('解析失败: ' + (error.response?.data?.detail || error.message));
    }
  } finally {
    loading.value = false;
  }
};

const rewriteTarget = async (target) => {
  if (!aiResponse.value || !aiResponse.value.id) return;

  isRewriting.value = true;
  try {
    const response = await rewriteChatMessage(aiResponse.value.id, target);
    aiResponse.value = response.data;
  } catch (error) {
    console.error(error);
    alert('改写失败: ' + (error.response?.data?.detail || error.message));
  } finally {
    isRewriting.value = false;
  }
}

const resetView = () => {
  inputText.value = '';
  aiResponse.value = null;
  showResult.value = false;
  if (fileInput.value) {
    fileInput.value.value = '';
  }
};

const getComplexityClass = (level) => {
  if (level === '高') return 'level-high';
  if (level === '中') return 'level-medium';
  if (level === '低') return 'level-low';
  return '';
}
</script>

<style scoped>
.home-container {
  padding: 40px;
  max-width: 1200px;
  margin: 0 auto;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 标题区域 */
.hero-section {
  margin-bottom: 30px;
  flex-shrink: 0;
}
.title-with-icon {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}
.main-title {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  font-size: 32px;
  font-weight: 800;
  color: #000;
  margin: 0;
  letter-spacing: 2px;
}
.sub-title {
  font-size: 16px;
  color: #999;
  margin: 0;
  padding-left: 2px; /* 对齐文字 */
}

/* 上传区域 */
.initial-view {
  flex: 1;
}

.upload-area {
  background-color: #fff;
  border: 2px dashed #e0e0e0;
  border-radius: 20px;
  padding: 120px 60px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 20px;
}
.upload-area:hover {
  border-color: var(--color-middle);
  background-color: #fafafa;
}
.upload-area.disabled {
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none;
}
.upload-buttons {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 20px;
}
.action-btn {
  background-color: #f5f5f5;
  border: none;
  border-radius: 12px;
  padding: 8px 20px;
  font-size: 14px;
  font-weight: bold;
  color: #000;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
  box-shadow: none;
}
.action-btn:hover {
  background-color: #eee;
}
.upload-hint {
  font-size: 14px;
  color: #999;
  margin: 0;
}

/* 加载横幅 */
.loading-banner {
  background-color: #e6f7ff;
  color: #00a8ff;
  padding: 15px;
  border-radius: var(--border-radius-pill); /* 胶囊型 */
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 40px;
  animation: fadeIn 0.5s;
  border: none; /* 去除边缘 */
  font-weight: bold;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 结果区域 */
.result-view {
  animation: fadeIn 0.5s;
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden; /* 让卡片内部可以滚动 */
}
.result-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  flex-shrink: 0;
}
.back-btn {
  background: none;
  border: 1px solid #ccc;
  padding: 8px 15px;
  border-radius: 20px;
  cursor: pointer;
  margin-right: 20px;
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  transition: all 0.2s;
  color: #000;
}
.back-btn:hover {
  background-color: #f0f0f0;
}
.result-header h2 {
  margin: 0;
  font-size: 20px;
}

/* 结果卡片详细设计 */
.response-section {
  background-color: #fff;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

.fixed-result-header {
  padding: 20px 30px;
  border-bottom: 1px solid #eee;
  flex-shrink: 0;
}
.header-top-row {
  display: flex;
  align-items: center;
  gap: 20px;
}
.result-title {
  margin: 0;
  font-size: 24px;
  color: #000;
  font-weight: bold;
}
.tags-container {
  display: flex;
  gap: 10px;
}
.highlight-tag {
  background-color: #000;
  color: #fff;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: bold;
}
.info-tag {
  background-color: var(--color-primary);
  color: #000;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: bold;
}

.scrollable-content {
  padding: 30px;
  overflow-y: auto;
  flex: 1;
}

.result-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 40px;
}

/* 左侧：具体信息提取 */
.info-list {
  display: flex;
  flex-direction: column;
  gap: 25px;
}
.info-item {
  display: flex;
  align-items: flex-start;
}
.info-text strong {
  display: block;
  margin-bottom: 8px;
  color: #000;
  font-size: 16px;
}
.info-text p {
  margin: 0;
  color: #333;
  line-height: 1.6;
  font-size: 15px;
}
.process-text {
  white-space: pre-wrap;
  color: #333;
  line-height: 1.6;
  background-color: var(--content-bg);
  padding: 15px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  font-size: 15px;
}

/* 右侧面板 */
.right-panel {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.warning-panel {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.warning-box {
  padding: 15px;
  border-radius: 8px;
  background-color: #fff;
  color: #666;
  border: 1px solid var(--border-color);
}
.warning-box h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: bold;
  color: #000;
}
.warning-box p {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
}

/* 难度分析仪表盘 */
.analysis-dashboard {
  display: flex;
  gap: 20px;
  padding: 15px 0;
  border-top: 1px dashed var(--border-color);
  border-bottom: 1px dashed var(--border-color);
}
.dashboard-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
.dashboard-item .label {
  color: #666;
  font-size: 14px;
}
.dashboard-item .value.text-only {
  font-weight: bold;
  font-size: 14px;
}
.level-high { color: #e53935 !important; }
.level-medium { color: #f57c00 !important; }
.level-low { color: #43a047 !important; }

/* 多版本改写工具栏 */
.rewrite-toolbar {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.rewrite-toolbar span {
  color: #000;
  font-weight: bold;
  font-size: 14px;
}
.rewrite-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.rewrite-btn {
  background-color: #fff;
  border: 1px solid #000;
  color: #000;
  padding: 6px 15px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 13px;
  font-weight: 500;
}
.rewrite-btn:hover:not(:disabled) {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
  color: #000;
}
.rewrite-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.rewriting-status {
  font-size: 13px;
  color: #999;
  font-style: italic;
  font-weight: normal !important;
}

/* 原文区域 */
.original-text-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 200px;
}
.original-text-section h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: bold;
  color: #000;
}
.original-content {
  flex: 1;
  background-color: #fafafa;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 15px;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  overflow-y: auto;
  max-height: 400px; /* 防止过长 */
}

.mapping-section {
  padding-top: 15px;
}
.mapping-section h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: bold;
  color: #000;
}
.mapping-section p {
  margin: 0;
  font-size: 13px;
  line-height: 1.5;
  color: #666;
}
.file-link {
  color: #00a8ff;
  text-decoration: underline;
}

/* Modal 中的表单切换过渡动画 */
.auth-modal-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 0 0 0;
  background: linear-gradient(45deg, skyblue, darkblue);
  border-radius: 20px;
  /* 去掉白色外框 */
  width: 480px; /* 固定宽度，防止切换时抖动 */
  min-height: 450px; /* 给一个最小高度 */
  overflow: hidden; /* 防止滑动溢出 */
  transition: height 0.4s cubic-bezier(0.4, 0, 0.2, 1); /* 外框高度平滑过渡 */
}

.logo-area-transition {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.auth-modal-content .logo-text {
  color: #fff;
  font-size: 28px;
  font-weight: 800;
  margin: 0;
  letter-spacing: 1px;
}

.form-transition-container {
  width: 100%;
  position: relative;
  transition: height 0.4s cubic-bezier(0.4, 0, 0.2, 1); /* 内部容器高度平滑过渡 */
}

.form-wrapper {
  width: 100%;
  display: flex;
  justify-content: center;
}

/* 使用绝对定位来实现表单区域的相对平滑滑动切换，不会互相挤压 */
.login-wrapper-abs, .register-wrapper-abs {
  position: absolute;
  top: 0;
  left: 0;
}

/* 增加了 translateY 实现平滑上下移动 */
.form-slide-enter-active,
.form-slide-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 离开的向下稍微滑动并变透明，新来的从下方滑入 */
.form-slide-enter-from {
  opacity: 0;
  transform: translateY(30px);
}
.form-slide-leave-to {
  opacity: 0;
  transform: translateY(-30px);
}

/* 恢复示例区域 */
.examples-section {
  margin-top: 20px;
}
.section-title {
  font-size: 16px;
  color: #000;
  margin-bottom: 20px;
  font-weight: bold;
}
.examples-grid {
  display: flex;
  gap: 30px;
  flex-wrap: wrap;
}
.example-card {
  flex: 1;
  min-width: 250px;
  max-width: 350px;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #eee;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s;
  cursor: pointer;
}
.example-card:hover {
  transform: translateY(-5px);
}
.card-image {
  height: 140px;
  background: linear-gradient(135deg, #f5f7fa, #e4e8f0);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ccc;
}
.card-content {
  padding: 15px;
  background-color: #fff;
  flex: 1;
}
.card-title {
  font-size: 16px;
  margin: 0 0 10px 0;
  color: #000;
}
.card-tags {
  display: flex;
  gap: 8px;
}
.tag {
  background-color: #f5f5f5;
  padding: 4px 10px;
  border-radius: var(--border-radius-pill);
  font-size: 12px;
  color: #000;
}
</style>
