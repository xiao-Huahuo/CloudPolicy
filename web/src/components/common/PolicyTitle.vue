<template>
  <div class="policy-title-wrap" :class="{ center }">
    <h1 class="policy-title">{{ title }}</h1>
    <p v-if="subtitle" class="policy-subtitle">{{ subtitle }}</p>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    default: '',
  },
  center: {
    type: Boolean,
    default: true,
  },
});
</script>

<style scoped>
.policy-title-wrap {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.policy-title-wrap.center {
  align-items: center;
  text-align: center;
}

.policy-title {
  margin: 0;
  font-size: var(--policy-title-size, 36px);
  font-weight: 900;
  color: var(--policy-title-color, #c0392b);
  letter-spacing: var(--policy-title-letter-spacing, 4px);
  line-height: 1.1;
  font-family: var(--policy-title-font, 'Noto Serif SC', 'SimSun', Georgia, serif);
  text-shadow: var(--policy-title-shadow, 0 3px 14px rgba(192, 57, 43, 0.16));
}

.policy-subtitle {
  margin: 0;
  font-size: var(--policy-subtitle-size, 14px);
  color: var(--policy-subtitle-color, #999);
  letter-spacing: 1px;
}
</style>
