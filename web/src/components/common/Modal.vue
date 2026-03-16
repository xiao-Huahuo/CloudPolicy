<template>
  <div v-if="isOpen" class="modal-overlay" @click="close">
    <!-- 移除了 modal-content 的默认样式类，改为接收传入的自定义 class 或者去除默认背景 -->
    <div class="modal-container" @click.stop>
      <button class="close-btn" @click="close">
        <!-- 使用极简的白色叉号，因为登录框是深蓝色的，如果放外面就是灰色 -->
        <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
      </button>
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  isOpen: Boolean
});

const emit = defineEmits(['close']);

const close = () => {
  emit('close');
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5); /* 灰色遮罩 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

/* 移除了原本的白色背景和内边距，让内部组件自己决定外观 */
.modal-container {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}

.close-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  background: none;
  border: none;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.7); /* 半透明白色，因为底层是蓝色的登录框 */
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  color: #fff;
  transform: scale(1.1);
}
</style>
