<template>
  <Modal :isOpen="isOpen" @close="emit('cancel')">
    <div class="logout-dialog">
      <h3 class="logout-dialog__title">退出登录</h3>
      <p class="logout-dialog__text">当前会结束本次登录状态，确定现在退出吗？</p>
      <div class="logout-dialog__actions">
        <button type="button" class="logout-dialog__btn logout-dialog__btn--ghost" @click="emit('cancel')">取消</button>
        <button type="button" class="logout-dialog__btn logout-dialog__btn--primary" @click="emit('confirm')">退出登录</button>
      </div>
    </div>
  </Modal>
</template>

<script setup>
import Modal from '@/components/common/Modal.vue'

defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['cancel', 'confirm'])
</script>

<style scoped>
.logout-dialog {
  width: min(420px, calc(100vw - 40px));
  padding: 28px 26px 24px;
  border-radius: 18px;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  box-shadow: 0 20px 48px rgba(9, 19, 31, 0.18);
}

.logout-dialog__title {
  margin: 0;
  font-size: 20px;
  color: var(--text-primary);
}

.logout-dialog__text {
  margin: 12px 0 0;
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.logout-dialog__actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 22px;
}

.logout-dialog__btn {
  min-width: 96px;
  padding: 10px 16px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.logout-dialog__btn--ghost {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.logout-dialog__btn--ghost:hover {
  color: var(--text-primary);
  border-color: color-mix(in srgb, var(--color-primary) 20%, var(--border-color));
}

.logout-dialog__btn--primary {
  background: var(--color-primary);
  color: #fff;
  border: 1px solid var(--color-primary);
}

.logout-dialog__btn--primary:hover {
  filter: brightness(1.04);
}
</style>
