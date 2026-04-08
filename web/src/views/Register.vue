<template>
  <div class="auth-page">
    <RegisterForm @switch-to-login="goLogin" />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import RegisterForm from '@/components/Home/RegisterForm.vue';

const router = useRouter();

const goLogin = () => {
  router.push('/login');
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
