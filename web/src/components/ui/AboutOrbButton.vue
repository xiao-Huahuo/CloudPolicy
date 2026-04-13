<script setup>
defineProps({
  label: {
    type: String,
    default: '更多',
  },
});
</script>

<template>
  <button class="about-orb-btn" type="button">
    <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round">
      <circle cx="5" cy="12" r="1.25"></circle>
      <circle cx="12" cy="12" r="1.25"></circle>
      <circle cx="19" cy="12" r="1.25"></circle>
    </svg>
    <span class="about-orb-btn__tooltip">{{ label }}</span>
  </button>
</template>

<style scoped>
.about-orb-btn {
  position: relative;
  width: 48px;
  height: 48px;
  border: 1px solid color-mix(in srgb, var(--color-primary) 16%, var(--border-color));
  border-radius: 999px;
  background:
    linear-gradient(147deg, color-mix(in srgb, var(--color-secondary) 72%, #ffffff 28%) 0%, color-mix(in srgb, var(--color-primary) 84%, #ffffff 16%) 74%);
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow:
    0 14px 24px color-mix(in srgb, var(--color-primary) 20%, transparent),
    0 0 16px color-mix(in srgb, var(--color-secondary) 20%, transparent);
  transition: transform 0.24s ease, box-shadow 0.24s ease, filter 0.24s ease;
}

.about-orb-btn:hover {
  transform: translateY(-1px) scale(1.02);
  filter: saturate(1.06);
  box-shadow:
    0 18px 28px color-mix(in srgb, var(--color-primary) 26%, transparent),
    0 0 22px color-mix(in srgb, var(--color-secondary) 24%, transparent);
}

.about-orb-btn:hover svg {
  animation: about-orb-jello 0.7s both;
}

.about-orb-btn__tooltip {
  position: absolute;
  top: -42px;
  left: 50%;
  transform: translateX(-50%);
  min-width: 48px;
  padding: 6px 10px;
  border-radius: 10px;
  background:
    linear-gradient(147deg, color-mix(in srgb, var(--color-secondary) 72%, #ffffff 28%) 0%, color-mix(in srgb, var(--color-primary) 84%, #ffffff 16%) 74%);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.22s ease, transform 0.22s ease;
  box-shadow: 0 12px 22px color-mix(in srgb, var(--color-primary) 18%, transparent);
}

.about-orb-btn__tooltip::before {
  content: '';
  position: absolute;
  left: 50%;
  bottom: -5px;
  width: 10px;
  height: 10px;
  background: inherit;
  transform: translateX(-50%) rotate(45deg);
}

.about-orb-btn:hover .about-orb-btn__tooltip {
  opacity: 1;
  transform: translateX(-50%) translateY(-2px);
}

@keyframes about-orb-jello {
  0% { transform: scale3d(1, 1, 1); }
  30% { transform: scale3d(0.75, 1.25, 1); }
  40% { transform: scale3d(1.25, 0.75, 1); }
  50% { transform: scale3d(0.85, 1.15, 1); }
  65% { transform: scale3d(1.05, 0.95, 1); }
  75% { transform: scale3d(0.95, 1.05, 1); }
  100% { transform: scale3d(1, 1, 1); }
}
</style>
