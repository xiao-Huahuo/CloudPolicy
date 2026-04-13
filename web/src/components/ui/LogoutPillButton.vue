<script setup>
defineProps({
  label: {
    type: String,
    default: '退出登录',
  },
  compact: {
    type: Boolean,
    default: false,
  },
});
</script>

<template>
  <button class="logout-pill-btn" :class="{ compact }" type="button">
    <span class="logout-pill-btn__sign" aria-hidden="true">
      <svg viewBox="0 0 512 512">
        <path
          d="M377.9 105.9 500.7 228.7c7.2 7.2 11.3 17.1 11.3 27.3s-4.1 20.1-11.3 27.3L377.9 406.1c-6.4 6.4-15 9.9-24 9.9-18.7 0-33.9-15.2-33.9-33.9v-62.1H192c-17.7 0-32-14.3-32-32v-64c0-17.7 14.3-32 32-32h128v-62.1c0-18.7 15.2-33.9 33.9-33.9 9 0 17.6 3.6 24 9.9ZM160 96H96c-17.7 0-32 14.3-32 32v256c0 17.7 14.3 32 32 32h64c17.7 0 32 14.3 32 32s-14.3 32-32 32H96c-53 0-96-43-96-96V128C0 75 43 32 96 32h64c17.7 0 32 14.3 32 32s-14.3 32-32 32Z"
        />
      </svg>
    </span>
    <span class="logout-pill-btn__text">{{ label }}</span>
  </button>
</template>

<style scoped>
.logout-pill-btn {
  display: inline-flex;
  align-items: center;
  justify-content: flex-start;
  width: 48px;
  height: 48px;
  padding: 0;
  border: none;
  border-radius: 999px;
  overflow: hidden;
  cursor: pointer;
  background:
    linear-gradient(135deg, #ff6c6c, #ff4141);
  box-shadow:
    0 12px 24px rgba(255, 65, 65, 0.24),
    inset 0 1px 0 rgba(255, 255, 255, 0.24);
  transition: width 0.3s ease, transform 0.24s ease, box-shadow 0.24s ease;
}

.logout-pill-btn.compact {
  width: 42px;
  height: 42px;
}

.logout-pill-btn__sign {
  width: 48px;
  min-width: 48px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.logout-pill-btn.compact .logout-pill-btn__sign {
  width: 42px;
  min-width: 42px;
}

.logout-pill-btn__sign svg {
  width: 16px;
  fill: #fff;
}

.logout-pill-btn__text {
  width: 0;
  opacity: 0;
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
  transition: width 0.3s ease, opacity 0.24s ease;
}

.logout-pill-btn:hover {
  width: 128px;
  transform: translateY(-1px);
  box-shadow:
    0 16px 26px rgba(255, 65, 65, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.28);
}

.logout-pill-btn.compact:hover {
  width: 116px;
}

.logout-pill-btn:hover .logout-pill-btn__text {
  width: 72px;
  opacity: 1;
}

.logout-pill-btn.compact:hover .logout-pill-btn__text {
  width: 64px;
}
</style>
