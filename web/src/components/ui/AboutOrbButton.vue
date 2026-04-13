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
  width: 40px;
  height: 40px;
  border: 1px solid color-mix(in srgb, var(--shell-glass-border, rgba(255, 255, 255, 0.16)) 88%, transparent);
  border-radius: 999px;
  background: transparent;
  color: var(--shell-text-muted, var(--text-secondary));
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: none;
  transition: transform 0.2s ease, background 0.2s ease, color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.about-orb-btn:hover {
  transform: translateY(-1px);
  background: color-mix(in srgb, var(--color-primary) 14%, transparent);
  color: var(--shell-text, var(--text-primary));
  border-color: color-mix(in srgb, var(--color-primary) 26%, var(--shell-glass-border, rgba(255, 255, 255, 0.16)));
  box-shadow: 0 10px 18px color-mix(in srgb, var(--color-primary) 12%, transparent);
}

.about-orb-btn__tooltip {
  position: absolute;
  top: -42px;
  left: 50%;
  transform: translateX(-50%);
  min-width: 48px;
  padding: 6px 10px;
  border-radius: 10px;
  background: var(--card-bg);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  font-size: 11px;
  font-weight: 700;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.22s ease, transform 0.22s ease;
  box-shadow: 0 12px 22px rgba(10, 17, 28, 0.18);
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
</style>
