<template>
  <div class="form-container">
    <div class="logo-area">
      <h1 class="logo-text">找回密码</h1>
      <p class="logo-subtitle">优先使用已绑定的手机号或邮箱恢复密码</p>
    </div>

    <form class="form" @submit.prevent="handlePrimaryAction">
      <div class="flex-column">
        <label>账号标识</label>
      </div>
      <div class="inputForm">
        <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" class="input-icon">
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
        </svg>
        <input
          v-model="identifier"
          type="text"
          class="input"
          placeholder="手机号 / 邮箱 / 用户名"
          required
        />
      </div>

      <template v-if="step !== 'lookup'">
        <div class="method-grid">
          <button
            v-for="item in methods"
            :key="item.channel"
            type="button"
            class="method-chip"
            :class="{ active: channel === item.channel }"
            @click="channel = item.channel"
          >
            <span>{{ item.label }}</span>
            <small>{{ item.masked_target }}</small>
          </button>
        </div>

        <div class="flex-column">
          <label>图形验证码</label>
        </div>
        <div class="captcha-row">
          <div class="inputForm inputForm--captcha">
            <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" class="input-icon">
              <rect x="3" y="4" width="18" height="16" rx="2"></rect>
              <path d="M7 8h10M7 12h4M7 16h8"></path>
            </svg>
            <input
              v-model="captchaAnswer"
              type="text"
              class="input"
              maxlength="4"
              placeholder="输入右侧验证码"
              required
            />
          </div>
          <button
            type="button"
            class="captcha-visual"
            :disabled="captchaLoading"
            @click="refreshCaptcha"
            v-html="captchaSvg"
          ></button>
        </div>
      </template>

      <template v-if="step === 'reset'">
        <div class="flex-column">
          <label>验证码</label>
        </div>
        <div class="inputForm">
          <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" class="input-icon">
            <path d="M9 12l2 2 4-4"></path>
            <path d="M21 12c.552 0 1-.449.973-1A10 10 0 1 0 12 22c.551.027 1-.421 1-.973V18"></path>
          </svg>
          <input v-model="code" type="text" class="input" maxlength="6" placeholder="输入收到的验证码" required />
        </div>

        <div class="flex-column">
          <label>新密码</label>
        </div>
        <div class="inputForm">
          <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" class="input-icon">
            <rect x="3" y="11" width="18" height="11" rx="2"></rect>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
          </svg>
          <input v-model="newPassword" type="password" class="input" placeholder="至少 6 位密码" required />
        </div>

        <div class="flex-column">
          <label>确认新密码</label>
        </div>
        <div class="inputForm">
          <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" class="input-icon">
            <rect x="3" y="11" width="18" height="11" rx="2"></rect>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
          </svg>
          <input v-model="confirmPassword" type="password" class="input" placeholder="再次输入新密码" required />
        </div>
      </template>

      <p v-if="previewCode" class="preview-box">沙箱验证码：<strong>{{ previewCode }}</strong></p>
      <p v-if="successMessage" class="success-msg">{{ successMessage }}</p>
      <p v-if="errorMessage" class="error-msg">{{ errorMessage }}</p>

      <div class="flex-row">
        <span class="span" @click="$emit('switch-to-login')">返回登录</span>
        <span v-if="step !== 'lookup'" class="span span-muted" @click="resetLookup">重新选择方式</span>
      </div>

      <button class="button-submit" type="submit" :disabled="loading || captchaLoading">
        {{ primaryButtonText }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { getCaptcha, getRecoveryOptions, resetPassword, sendRecoveryCode } from '@/api/user';

defineEmits(['switch-to-login']);

const identifier = ref('');
const methods = ref([]);
const channel = ref('phone');
const step = ref('lookup');

const captchaId = ref('');
const captchaSvg = ref('');
const captchaAnswer = ref('');

const code = ref('');
const newPassword = ref('');
const confirmPassword = ref('');

const previewCode = ref('');
const successMessage = ref('');
const errorMessage = ref('');

const loading = ref(false);
const captchaLoading = ref(false);

const primaryButtonText = computed(() => {
  if (step.value === 'lookup') return '查找可用方式';
  if (step.value === 'choose') return loading.value ? '发送中...' : '发送恢复验证码';
  return loading.value ? '提交中...' : '重置密码';
});

const refreshCaptcha = async () => {
  captchaLoading.value = true;
  try {
    const { data } = await getCaptcha();
    captchaId.value = data.captcha_id;
    captchaSvg.value = data.svg;
    captchaAnswer.value = '';
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '图形验证码加载失败';
  } finally {
    captchaLoading.value = false;
  }
};

const resetLookup = async () => {
  step.value = 'lookup';
  previewCode.value = '';
  successMessage.value = '';
  errorMessage.value = '';
  code.value = '';
  await refreshCaptcha();
};

const handleLookup = async () => {
  const { data } = await getRecoveryOptions(identifier.value);
  methods.value = data.methods || [];
  if (!methods.value.length) {
    throw new Error('当前账号没有可用的找回方式');
  }
  channel.value = methods.value[0].channel;
  step.value = 'choose';
  await refreshCaptcha();
};

const handleSend = async () => {
  const { data } = await sendRecoveryCode({
    identifier: identifier.value,
    channel: channel.value,
    captcha_id: captchaId.value,
    captcha_answer: captchaAnswer.value,
  });
  previewCode.value = data.preview_code || '';
  successMessage.value = '恢复验证码已发送，请完成密码重置。';
  step.value = 'reset';
};

const handleReset = async () => {
  const { data } = await resetPassword({
    identifier: identifier.value,
    channel: channel.value,
    code: code.value,
    new_password: newPassword.value,
    confirm_password: confirmPassword.value,
  });
  successMessage.value = data.message || '密码重置成功';
  errorMessage.value = '';
};

const handlePrimaryAction = async () => {
  loading.value = true;
  errorMessage.value = '';
  successMessage.value = '';
  try {
    if (step.value === 'lookup') {
      await handleLookup();
    } else if (step.value === 'choose') {
      await handleSend();
    } else {
      await handleReset();
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || error.message || '操作失败';
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  refreshCaptcha();
});
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
  gap: 8px;
}

.logo-text {
  margin: 0;
  font-size: 34px;
  font-weight: 800;
  color: #fff7f1;
}

.logo-subtitle {
  margin: 0;
  color: rgba(255, 247, 245, 0.74);
  font-size: 13px;
  text-align: center;
}

.form {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: linear-gradient(
    160deg,
    rgba(20, 12, 18, 0.96) 0%,
    rgba(81, 35, 52, 0.92) 34%,
    rgba(21, 35, 63, 0.92) 72%,
    rgba(9, 19, 31, 0.97) 100%
  );
  padding: 30px 34px;
  width: 100%;
  border-radius: 28px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(22px);
  box-shadow:
    0 28px 80px rgba(9, 19, 31, 0.46),
    0 0 0 1px rgba(255, 255, 255, 0.04) inset,
    0 0 42px rgba(255, 143, 122, 0.12);
}

.flex-column > label {
  color: rgba(255, 247, 245, 0.86);
  font-weight: 600;
  font-size: 13px;
}

.inputForm {
  border: 1.5px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  min-height: 48px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 14px;
  background: rgba(255, 255, 255, 0.04);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.inputForm--captcha {
  flex: 1;
}

.inputForm:focus-within {
  border-color: rgba(95, 209, 255, 0.56);
  box-shadow: 0 0 0 4px rgba(95, 209, 255, 0.12);
}

.input-icon {
  color: rgba(255, 255, 255, 0.72);
  flex-shrink: 0;
}

.input {
  border: none;
  outline: none;
  background: transparent;
  width: 100%;
  color: #fff;
  font-size: 14px;
}

.input::placeholder {
  color: rgba(245, 247, 255, 0.44);
}

.method-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.method-chip {
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 247, 245, 0.9);
  border-radius: 16px;
  min-height: 62px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 4px;
  cursor: pointer;
}

.method-chip small {
  color: rgba(255, 247, 245, 0.58);
}

.method-chip.active {
  border-color: rgba(95, 209, 255, 0.5);
  background: rgba(95, 209, 255, 0.12);
}

.captcha-row {
  display: flex;
  gap: 10px;
}

.captcha-visual {
  width: 138px;
  min-height: 48px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.04);
  cursor: pointer;
  overflow: hidden;
}

.captcha-visual :deep(svg) {
  display: block;
  width: 100%;
  height: 100%;
}

.preview-box,
.success-msg,
.error-msg {
  border-radius: 14px;
  padding: 10px 12px;
  font-size: 13px;
  line-height: 1.5;
  margin: 0;
}

.preview-box {
  background: rgba(255, 219, 100, 0.12);
  border: 1px solid rgba(255, 219, 100, 0.28);
  color: #ffe7a0;
}

.success-msg {
  background: rgba(128, 250, 176, 0.12);
  border: 1px solid rgba(128, 250, 176, 0.22);
  color: #c7fdd8;
}

.error-msg {
  background: rgba(255, 143, 122, 0.12);
  border: 1px solid rgba(255, 143, 122, 0.24);
  color: #ffd7cf;
}

.flex-row {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.span {
  color: var(--auth-coral);
  font-size: 13px;
  cursor: pointer;
}

.span-muted {
  color: rgba(255, 247, 245, 0.68);
}

.button-submit {
  margin-top: 4px;
  border: none;
  border-radius: 18px;
  min-height: 48px;
  background: linear-gradient(135deg, var(--auth-coral) 0%, #ffb76f 100%);
  color: #26111a;
  font-weight: 800;
  font-size: 15px;
  cursor: pointer;
}

.button-submit:disabled,
.captcha-visual:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 560px) {
  .form {
    padding: 26px 20px;
  }

  .method-grid {
    grid-template-columns: 1fr;
  }

  .captcha-row,
  .flex-row {
    flex-direction: column;
  }

  .captcha-visual {
    width: 100%;
  }
}
</style>
