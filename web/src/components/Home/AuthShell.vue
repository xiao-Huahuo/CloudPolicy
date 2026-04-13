<template>
  <div class="auth-shell">
    <transition name="auth-shell-fade" mode="out-in">
      <LoginForm
        v-if="currentForm === 'login'"
        key="login"
        @success="$emit('success')"
        @switch-to-register="currentForm = 'register'"
        @switch-to-recover="currentForm = 'recover'"
      />
      <RegisterForm
        v-else-if="currentForm === 'register'"
        key="register"
        @success="$emit('success')"
        @switch-to-login="currentForm = 'login'"
      />
      <ForgotPasswordForm
        v-else
        key="recover"
        @switch-to-login="currentForm = 'login'"
      />
    </transition>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import LoginForm from '@/components/Home/LoginForm.vue';
import RegisterForm from '@/components/Home/RegisterForm.vue';
import ForgotPasswordForm from '@/components/Home/ForgotPasswordForm.vue';

const props = defineProps({
  initialForm: {
    type: String,
    default: 'login',
  },
});

defineEmits(['success']);

const currentForm = ref(props.initialForm);

watch(
  () => props.initialForm,
  (value) => {
    currentForm.value = value || 'login';
  }
);
</script>

<style scoped>
.auth-shell {
  display: flex;
  justify-content: center;
  width: 100%;
}

.auth-shell-fade-enter-active,
.auth-shell-fade-leave-active {
  transition: opacity 0.24s ease;
}

.auth-shell-fade-enter-from,
.auth-shell-fade-leave-to {
  opacity: 0;
}
</style>
