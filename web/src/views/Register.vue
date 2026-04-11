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
  position: relative;
  isolation: isolate;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(circle at 14% 18%, rgba(255, 143, 122, 0.18), transparent 24%),
    radial-gradient(circle at 86% 16%, rgba(95, 209, 255, 0.18), transparent 22%),
    radial-gradient(circle at 52% 82%, rgba(255, 219, 100, 0.1), transparent 24%),
    linear-gradient(135deg, #140c12 0%, #512334 36%, #15233f 72%, #09131f 100%);
  padding: 32px 14px;
}

.auth-page::before,
.auth-page::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.auth-page::before {
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.035) 1px, transparent 1px);
  background-size: 40px 40px;
  mask-image: radial-gradient(circle at center, rgba(0, 0, 0, 0.82), transparent 84%);
}

.auth-page::after {
  background:
    linear-gradient(90deg, transparent 0, rgba(255, 255, 255, 0.05) 50%, transparent 100%);
  transform: translateX(-100%);
  animation: authShimmer 10s linear infinite;
}

@keyframes authShimmer {
  to {
    transform: translateX(100%);
  }
}
</style>
