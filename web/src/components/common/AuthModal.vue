<template>
  <Modal :isOpen="isOpen" @close="$emit('close')">
    <div class="auth-modal-content">
      <AuthShell :initial-form="initialForm" @success="emit('close')" />
    </div>
  </Modal>
</template>

<script setup>
import Modal from '@/components/common/Modal.vue';
import AuthShell from '@/components/Home/AuthShell.vue';

defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
  initialForm: {
    type: String,
    default: 'login',
  },
});

const emit = defineEmits(['close']);
</script>

<style scoped>
.auth-modal-content {
  display: flex;
  justify-content: center;
  align-items: center;
  background: transparent;
  padding: 0;
  width: auto;
  min-height: 0;
}
</style>
