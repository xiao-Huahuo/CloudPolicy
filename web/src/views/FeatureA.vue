<template>
  <div class="feature-container">
    <!-- 顶部轮播图 (占位) -->
    <div class="carousel-placeholder">
      <!-- 左右切换箭头 -->
      <button class="nav-arrow left-arrow">
        <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="15 18 9 12 15 6"></polyline>
        </svg>
      </button>
      <button class="nav-arrow right-arrow">
        <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="9 18 15 12 9 6"></polyline>
        </svg>
      </button>

      <div class="carousel-content">
        <h2>{{ carouselItems[currentSlide].title }}</h2>
        <p>{{ carouselItems[currentSlide].desc }}</p>
      </div>
      <!-- 轮播图指示器 -->
      <div class="carousel-indicators">
        <span
          v-for="(item, index) in carouselItems"
          :key="index"
          class="indicator"
          :class="{ active: currentSlide === index }"
          @click="currentSlide = index"
        ></span>
      </div>
    </div>

    <!-- 附属功能横条 -->
    <div class="action-bar">
      <div class="action-item" @click="goToRewrite">
        <div class="action-icon">
          <!-- 极简非 emoji 图标: 笔和纸 -->
          <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 20h9"></path>
            <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
          </svg>
        </div>
        <span class="action-name">多版本改写</span>
      </div>

      <div class="action-item" @click="goToHistory">
        <div class="action-icon">
          <!-- 极简非 emoji 图标: 历史/时钟 -->
          <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
        </div>
        <span class="action-name">历史记录</span>
      </div>

      <!-- 可以继续添加其他功能占位 -->
      <div class="action-item disabled">
        <div class="action-icon">
          <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="4 7 4 4 20 4 20 7"></polyline><line x1="9" y1="20" x2="15" y2="20"></line><line x1="12" y1="4" x2="12" y2="20"></line>
          </svg>
        </div>
        <span class="action-name">全文翻译 (敬请期待)</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// 轮播图逻辑
const currentSlide = ref(0);
const carouselItems = [
  { title: '文档智能处理中心', desc: '让繁杂的文档化繁为简' },
  { title: '多版本改写', desc: '一键转换文档风格，适配不同人群' },
  { title: '历史记录查询', desc: '随时找回您的解析结果' }
];
let slideInterval = null;

const nextSlide = () => {
  currentSlide.value = (currentSlide.value + 1) % carouselItems.length;
};

onMounted(() => {
  // 每 3 秒切换一次
  slideInterval = setInterval(nextSlide, 3000);
});

onUnmounted(() => {
  if (slideInterval) clearInterval(slideInterval);
});

const goToHistory = () => {
  router.push('/feature-c'); // 跳转到会话历史
};

const goToRewrite = () => {
  window.location.href = '/rewrite';
};
</script>

<style scoped>
.feature-container {
  padding: 30px;
  max-width: 1200px;
  margin: 0 auto;
}

/* 轮播图占位 */
.carousel-placeholder {
  width: 100%;
  height: 300px;
  background: #f5f7fa;
  border-radius: var(--border-radius-main);
  margin-bottom: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.nav-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid var(--border-color);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #333;
  transition: all 0.2s;
  z-index: 2;
}

.nav-arrow:hover {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.left-arrow {
  left: 20px;
}

.right-arrow {
  right: 20px;
}

.carousel-content {
  text-align: center;
  color: #000;
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.carousel-content h2 {
  font-size: 32px;
  margin: 0 0 10px 0;
  font-weight: bold;
}

.carousel-content p {
  color: #666;
  font-size: 16px;
  margin: 0;
}

.carousel-indicators {
  position: absolute;
  bottom: 20px;
  display: flex;
  gap: 8px;
}

.indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #ccc;
  cursor: pointer;
  transition: all 0.3s;
}

.indicator.active {
  background-color: #000;
  width: 24px; /* 激活时变成小胶囊 */
  border-radius: 4px;
}

/* 附属功能横条 */
.action-bar {
  display: flex;
  gap: 30px;
  justify-content: center;
  margin-top: 20px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 20px;
  border-radius: var(--border-radius-main);
  transition: all 0.2s;
  min-width: 120px;
}

.action-item:hover:not(.disabled) {
  background-color: #fff;
  transform: translateY(-5px);
  /* 去掉阴影 */
  border: 1px solid var(--border-color);
}

.action-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 按钮变成黑底白图标 */
.action-icon {
  width: 60px;
  height: 60px;
  background-color: #000; /* 黑底 */
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff; /* 白图标 */
  transition: all 0.3s;
}

.action-item:hover:not(.disabled) .action-icon {
  background-color: #333; /* hover 时变浅一点的黑 */
}

/* 文字变成黑色或灰色，不使用深蓝色 */
.action-name {
  font-size: 15px;
  font-weight: bold;
  color: #000; /* 纯黑 */
}
.action-item.disabled .action-name {
  color: #666; /* 灰色 */
}
</style>
