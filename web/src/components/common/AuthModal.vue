<template>
  <Modal :isOpen="isOpen" @close="$emit('close')">
    <div class="auth-modal-content">
      <transition name="form-fade" mode="out-in">
        <div v-if="currentForm === 'login'" class="form-wrapper" key="login">
          <LoginForm @success="handleLoginSuccess" @switch-to-register="currentForm = 'register'" />
        </div>
        <div v-else class="form-wrapper" key="register">
          <RegisterForm @switch-to-login="currentForm = 'login'" />
        </div>
      </transition>
    </div>
  </Modal>
</template>

<script setup>
import { ref, watch } from 'vue';
import Modal from '@/components/common/Modal.vue';
import LoginForm from '@/components/Home/LoginForm.vue';
import RegisterForm from '@/components/Home/RegisterForm.vue';

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['close']);
const currentForm = ref('login');

watch(
  () => props.isOpen,
  (value) => {
    if (value) currentForm.value = 'login';
  }
);

const handleLoginSuccess = () => {
  emit('close');
};
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

.form-wrapper {
  width: auto;
  display: flex;
  justify-content: center;
}

.form-fade-enter-active,
.form-fade-leave-active {
  transition: opacity 0.25s ease;
}

.form-fade-enter-from,
.form-fade-leave-to {
  opacity: 0;
}
</style>
