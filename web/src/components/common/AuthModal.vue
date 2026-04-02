<template>
  <Modal :isOpen="isOpen" @close="$emit('close')">
    <div class="auth-modal-content">
      <div class="logo-area-transition">
        <h1 class="logo-text">ClearNotify</h1>
      </div>
      <div class="form-transition-container" :style="{ height: containerHeight + 'px' }">
        <transition
          name="form-slide"
          @before-enter="onBeforeEnter"
          @enter="onEnter"
          @after-enter="onAfterEnter"
          @leave="onLeave"
        >
          <div v-if="currentForm === 'login'" class="form-wrapper login-wrapper-abs" key="login">
            <LoginForm @success="handleLoginSuccess" @switch-to-register="currentForm = 'register'" />
          </div>
          <div v-else class="form-wrapper register-wrapper-abs" key="register">
            <RegisterForm @switch-to-login="currentForm = 'login'" @success="handleLoginSuccess" />
          </div>
        </transition>
      </div>
    </div>
  </Modal>
</template>

<script setup>
import { nextTick, ref, watch } from 'vue';
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
const containerHeight = ref(350);

watch(
  () => props.isOpen,
  (value) => {
    if (value) {
      currentForm.value = 'login';
      containerHeight.value = 350;
    }
  }
);

const onBeforeEnter = (el) => {
  el.style.opacity = 0;
};

const onEnter = (el, done) => {
  nextTick(() => {
    containerHeight.value = el.offsetHeight;
    el.style.opacity = 1;
    done();
  });
};

const onAfterEnter = (el) => {
  el.style.opacity = '';
};

const onLeave = (el, done) => {
  el.style.opacity = 0;
  setTimeout(done, 400);
};

const handleLoginSuccess = () => {
  emit('close');
};
</script>

<style scoped>
.auth-modal-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 0 0;
  background: linear-gradient(140deg, #5a1e1e 0%, #7f8c8d 55%, #2c2c2c 100%);
  border-radius: 20px;
  width: 480px;
  min-height: 450px;
  overflow: hidden;
  transition: height 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.logo-area-transition {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.logo-text {
  color: #fff;
  font-size: 28px;
  font-weight: 800;
  margin: 0;
  letter-spacing: 1px;
}

.form-transition-container {
  width: 100%;
  position: relative;
  transition: height 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.form-wrapper {
  width: 100%;
  display: flex;
  justify-content: center;
}

.login-wrapper-abs,
.register-wrapper-abs {
  position: absolute;
  top: 0;
  left: 0;
}

.form-slide-enter-active,
.form-slide-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.form-slide-enter-from {
  opacity: 0;
  transform: translateY(30px);
}

.form-slide-leave-to {
  opacity: 0;
  transform: translateY(-30px);
}
</style>
