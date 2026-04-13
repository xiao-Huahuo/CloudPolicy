<script setup>
defineProps({
  label: {
    type: String,
    default: '查看全部',
  },
  compact: {
    type: Boolean,
    default: false,
  },
});
</script>

<template>
  <button class="learn-more-link" :class="{ compact }" type="button">
    <span class="learn-more-link__circle" aria-hidden="true">
      <span class="learn-more-link__icon"></span>
    </span>
    <span class="learn-more-link__text">{{ label }}</span>
  </button>
</template>

<style scoped>
.learn-more-link {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: flex-start;
  min-width: 10.5rem;
  min-height: 3rem;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--text-primary);
  font: inherit;
}

.learn-more-link.compact {
  min-width: 9rem;
  min-height: 2.75rem;
}

.learn-more-link__circle {
  position: relative;
  display: block;
  width: 3rem;
  height: 3rem;
  border-radius: 999px;
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--color-primary) 88%, #ffffff 12%), color-mix(in srgb, var(--color-secondary) 72%, #ffffff 28%));
  box-shadow:
    0 10px 22px color-mix(in srgb, var(--color-primary) 24%, transparent),
    inset 0 1px 0 rgba(255, 255, 255, 0.28);
  transition: width 0.45s cubic-bezier(0.65, 0, 0.076, 1), box-shadow 0.3s ease, filter 0.3s ease;
}

.learn-more-link__icon {
  position: absolute;
  left: 0.72rem;
  top: 50%;
  width: 1.15rem;
  height: 0.14rem;
  background: rgba(16, 24, 39, 0.9);
  border-radius: 999px;
  transform: translateY(-50%);
  transition: transform 0.45s cubic-bezier(0.65, 0, 0.076, 1), background 0.3s ease;
}

.learn-more-link__icon::before {
  content: '';
  position: absolute;
  right: 0.02rem;
  top: 50%;
  width: 0.58rem;
  height: 0.58rem;
  border-top: 0.14rem solid rgba(16, 24, 39, 0.9);
  border-right: 0.14rem solid rgba(16, 24, 39, 0.9);
  transform: translateY(-50%) rotate(45deg);
}

.learn-more-link__text {
  position: absolute;
  inset: 0;
  margin-left: 1.85rem;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 1.4rem 0 2.1rem;
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.04em;
  white-space: nowrap;
  transition: color 0.3s ease;
}

.learn-more-link:hover .learn-more-link__circle {
  width: 100%;
  filter: saturate(1.04);
  box-shadow:
    0 14px 26px color-mix(in srgb, var(--color-primary) 28%, transparent),
    0 0 24px color-mix(in srgb, var(--color-secondary) 18%, transparent);
}

.learn-more-link:hover .learn-more-link__icon {
  transform: translate(0.92rem, -50%);
  background: rgba(255, 255, 255, 0.96);
}

.learn-more-link:hover .learn-more-link__icon::before {
  border-color: rgba(255, 255, 255, 0.96);
}

.learn-more-link:hover .learn-more-link__text {
  color: #fff;
}

[data-theme='dark'] .learn-more-link__text {
  color: rgba(235, 243, 255, 0.94);
}
</style>
