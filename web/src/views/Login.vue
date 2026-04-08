<template>
  <div class="auth-page">
    <LoginForm @success="handleSuccess" @switch-to-register="goRegister" />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import LoginForm from '@/components/Home/LoginForm.vue';

const router = useRouter();

const handleSuccess = () => {
  router.push('/');
};

const goRegister = () => {
  router.push('/register');
};
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #111;
  padding: 24px 12px;
}
</style>
