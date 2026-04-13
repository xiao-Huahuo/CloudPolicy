<template>
  <div class="form-container">
    <div class="logo-area">
      <img src="@/assets/photos/main-icon.png" alt="icon" class="main-icon" v-if="hasIcon" @error="hasIcon = false" />
      <h1 class="logo-text">
        <span v-for="(ch, i) in '云枢观策'" :key="i" class="letter" :style="{ animationDelay: `${i * 0.06}s` }">{{ ch }}</span>
      </h1>
    </div>

    <form class="form" @submit.prevent="handleLogin">
      <div class="flex-column">
        <label>用户名 / Username</label>
      </div>
      <div class="inputForm">
        <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" class="input-icon"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
        <input v-model="username" type="text" class="input" placeholder="Enter your username" required />
      </div>

      <div class="flex-column">
        <label>密码 / Password</label>
      </div>
      <div class="inputForm">
        <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" class="input-icon"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
        <input v-model="password" type="password" class="input" placeholder="Enter your password" required />
      </div>

      <div class="flex-row">
        <span class="span" @click="$emit('switch-to-register')">没有账号？去注册</span>
      </div>

      <button class="button-submit" type="submit" :disabled="loading">
        {{ loading ? '登录中...' : '登 录' }}
      </button>

      <p class="error-msg" v-if="errorMessage">{{ errorMessage }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useUserStore } from '@/stores/auth.js';

const emit = defineEmits(['success', 'switch-to-register']);
const hasIcon = ref(true);

const username = ref('');
const password = ref('');
const errorMessage = ref('');
const loading = ref(false);
const userStore = useUserStore();

const handleLogin = async () => {
  loading.value = true;
  errorMessage.value = '';
  try {
    await userStore.login(username.value, password.value);
    emit('success');
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '登录失败';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.form-container {
  --auth-wine-deep: #140c12;
  --auth-wine-mid: #512334;
  --auth-sky-deep: #15233f;
  --auth-night: #09131f;
  --auth-coral: #ff8f7a;
  --auth-coral-soft: #ffd7cf;
  --auth-gold: #ffdb64;
  --auth-sky: #58cbff;
  --auth-sky-soft: #5fd1ff;
  --auth-mint: #80fab0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  width: min(100%, 470px);
}

.logo-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.main-icon {
  width: 64px;
  height: 64px;
  object-fit: contain;
  filter: none;
}

.logo-text {
  font-size: 36px;
  font-weight: 800;
  margin: 0;
  letter-spacing: 2px;
  display: flex;
  text-shadow:
    0 8px 24px rgba(255, 143, 122, 0.18),
    0 0 20px rgba(88, 203, 255, 0.12);
}

.letter {
  display: inline-block;
  color: #fff7f1;
  animation: letterFloat 0.6s cubic-bezier(0.22, 1, 0.36, 1) both;
  opacity: 0;
}

@keyframes letterFloat {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: translateY(0); }
}

.form {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 15px;
  background: linear-gradient(
    160deg,
    rgba(20, 12, 18, 0.96) 0%,
    rgba(81, 35, 52, 0.92) 34%,
    rgba(21, 35, 63, 0.92) 72%,
    rgba(9, 19, 31, 0.97) 100%
  );
  padding: 38px 34px;
  width: 100%;
  border-radius: 28px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  backdrop-filter: blur(22px);
  box-shadow:
    0 28px 80px rgba(9, 19, 31, 0.46),
    0 0 0 1px rgba(255, 255, 255, 0.04) inset,
    0 0 42px rgba(255, 143, 122, 0.12);
}

.form::before,
.form::after {
  content: "";
  position: absolute;
  inset: auto;
  border-radius: 999px;
  pointer-events: none;
  z-index: -1;
  filter: blur(14px);
}

.form::before {
  top: -48px;
  right: -10px;
  width: 180px;
  height: 180px;
  background: radial-gradient(circle, rgba(255, 143, 122, 0.3) 0%, rgba(255, 143, 122, 0) 72%);
}

.form::after {
  left: -38px;
  bottom: -66px;
  width: 220px;
  height: 220px;
  background: radial-gradient(circle, rgba(88, 203, 255, 0.18) 0%, rgba(88, 203, 255, 0) 72%);
}

::placeholder {
  font-family: inherit;
  color: rgba(245, 247, 255, 0.44);
}

.flex-column > label {
  color: rgba(255, 247, 245, 0.86);
  font-weight: 600;
  font-size: 14px;
  letter-spacing: 0.02em;
}

.inputForm {
  border: 1.5px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  min-height: 54px;
  display: flex;
  align-items: center;
  padding-left: 16px;
  transition: border-color 0.2s ease, background-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.09), rgba(255, 255, 255, 0.05)),
    rgba(255, 255, 255, 0.04);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
  margin-bottom: 10px;
}

.inputForm:hover {
  border-color: rgba(255, 183, 111, 0.24);
}

.input-icon {
  color: rgba(255, 183, 111, 0.72);
}

.input {
  margin-left: 10px;
  border-radius: 6px;
  border: none;
  width: 100%;
  height: 100%;
  font-size: 15px;
  background: transparent !important;
  color: #fff7f1;
  -webkit-text-fill-color: #fff7f1;
  caret-color: #fff7f1;
  box-shadow: none;
  appearance: none;
}

.input:focus { outline: none; }

.input:-webkit-autofill,
.input:-webkit-autofill:hover,
.input:-webkit-autofill:focus,
.input:-webkit-autofill:active {
  -webkit-text-fill-color: #fff7f1;
  caret-color: #fff7f1;
  -webkit-box-shadow: 0 0 0 1000px transparent inset !important;
  box-shadow: 0 0 0 1000px transparent inset !important;
  -webkit-background-clip: padding-box;
  transition: background-color 9999s ease-out 0s;
}

.inputForm:focus-within {
  border: 1.5px solid rgba(255, 143, 122, 0.85);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.12), rgba(255, 255, 255, 0.06)),
    rgba(255, 255, 255, 0.05);
  box-shadow:
    0 0 0 4px rgba(255, 143, 122, 0.12),
    0 16px 28px rgba(9, 19, 31, 0.18);
  transform: translateY(-1px);
}

.flex-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
  justify-content: flex-end;
}

.span {
  font-size: 14px;
  color: rgba(255, 215, 207, 0.78);
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s ease, text-shadow 0.2s ease;
  text-decoration: underline;
}

.span:hover {
  color: var(--auth-coral);
  text-shadow: 0 0 14px rgba(255, 143, 122, 0.24);
}

.button-submit {
  position: relative;
  display: inline-block;
  padding: 15px 30px;
  text-align: center;
  letter-spacing: 1.5px;
  background: linear-gradient(135deg, #ff8f7a 0%, #ffdb64 38%, #58cbff 100%);
  transition: transform 0.2s ease, box-shadow 0.3s ease, filter 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 16px;
  box-shadow:
    0 18px 34px rgba(255, 143, 122, 0.2),
    0 8px 22px rgba(88, 203, 255, 0.14),
    inset 0 1px 0 rgba(255, 255, 255, 0.34);
  margin: 10px 0;
  color: #1f1720;
  font-size: 16px;
  font-weight: 800;
  height: 55px;
  width: 100%;
  cursor: pointer;
}

.button-submit:hover {
  transform: translateY(-1px);
  box-shadow:
    0 24px 38px rgba(255, 143, 122, 0.24),
    0 12px 28px rgba(88, 203, 255, 0.18),
    inset 0 1px 0 rgba(255, 255, 255, 0.42);
  filter: saturate(1.04);
}

.button-submit:active { transform: scale(0.98); }

.button-submit:disabled {
  opacity: 0.72;
  cursor: not-allowed;
  filter: saturate(0.86);
}

.error-msg {
  color: var(--auth-coral-soft);
  text-align: center;
  font-size: 14px;
  margin: 0;
  font-weight: 500;
  padding: 10px 14px;
  border-radius: 14px;
  background: rgba(255, 143, 122, 0.12);
  border: 1px solid rgba(255, 183, 111, 0.18);
}

@media (max-width: 560px) {
  .logo-text {
    font-size: 31px;
    letter-spacing: 1px;
  }

  .form {
    padding: 30px 22px;
    border-radius: 24px;
  }

  .button-submit {
    height: 52px;
  }
}
</style>
