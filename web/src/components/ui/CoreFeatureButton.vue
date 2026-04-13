<script setup>
defineProps({
  label: {
    type: String,
    required: true,
  },
  hint: {
    type: String,
    default: '',
  },
  title: {
    type: String,
    default: '',
  },
});
</script>

<template>
  <button class="core-feature-btn" type="button" :title="title || label">
    <span class="core-feature-btn__glow"></span>
    <span class="core-feature-btn__icon">
      <slot />
    </span>
    <span class="core-feature-btn__copy">
      <span class="core-feature-btn__label">{{ label }}</span>
      <span v-if="hint" class="core-feature-btn__hint">{{ hint }}</span>
    </span>
  </button>
</template>

<style scoped>
.core-feature-btn {
  position: relative;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 142px;
  height: 142px;
  padding: 16px 14px;
  border: 1px solid color-mix(in srgb, var(--color-primary) 24%, var(--border-color));
  border-radius: 24px;
  background:
    linear-gradient(155deg, color-mix(in srgb, var(--card-bg) 82%, transparent), color-mix(in srgb, var(--color-primary) 8%, var(--card-bg))),
    linear-gradient(135deg, color-mix(in srgb, var(--color-primary) 12%, transparent), color-mix(in srgb, var(--color-secondary) 10%, transparent));
  color: var(--text-primary);
  cursor: pointer;
  overflow: hidden;
  box-shadow:
    0 6px 14px color-mix(in srgb, var(--color-primary) 10%, transparent),
    inset 0 1px 0 rgba(255, 255, 255, 0.14);
  transition: transform 0.28s ease, border-color 0.28s ease, box-shadow 0.28s ease, background 0.28s ease;
}

.core-feature-btn__glow {
  position: absolute;
  inset: auto -20% -42%;
  height: 78%;
  background: radial-gradient(circle, color-mix(in srgb, var(--color-secondary) 22%, transparent), transparent 66%);
  pointer-events: none;
  opacity: 0.6;
  transition: opacity 0.28s ease, transform 0.28s ease;
}

.core-feature-btn__icon {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 66px;
  height: 66px;
  border-radius: 20px;
  background:
    linear-gradient(145deg, color-mix(in srgb, var(--color-primary) 18%, transparent), color-mix(in srgb, var(--color-secondary) 18%, transparent));
  color: var(--color-primary-dark);
  box-shadow:
    0 4px 12px color-mix(in srgb, var(--color-primary) 10%, transparent),
    inset 0 1px 0 rgba(255, 255, 255, 0.24);
  transition: transform 0.32s ease, color 0.28s ease, box-shadow 0.28s ease;
}

.core-feature-btn__copy {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
  text-align: center;
}

.core-feature-btn__label {
  font-size: 15px;
  font-weight: 800;
  line-height: 1.25;
}

.core-feature-btn__hint {
  font-size: 11px;
  line-height: 1.4;
  color: var(--text-secondary);
}

.core-feature-btn:hover {
  transform: translate(-4px, -4px) rotate(0.8deg);
  border-color: color-mix(in srgb, var(--color-secondary) 36%, var(--border-color));
  box-shadow: 0 8px 18px color-mix(in srgb, var(--color-primary) 12%, transparent);
}

.core-feature-btn:hover .core-feature-btn__icon {
  transform: translateY(-8px) rotate(-4deg);
  color: #fff;
  box-shadow: 0 8px 16px color-mix(in srgb, var(--color-primary) 12%, transparent);
}

.core-feature-btn:hover .core-feature-btn__glow {
  opacity: 0.92;
  transform: scale(1.08);
}

[data-theme='dark'] .core-feature-btn {
  border-color: color-mix(in srgb, var(--color-primary) 30%, var(--border-color));
  box-shadow:
    0 8px 18px rgba(4, 10, 18, 0.26),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

[data-theme='dark'] .core-feature-btn:hover {
  box-shadow: 0 10px 22px rgba(4, 10, 18, 0.32);
}

@media (max-width: 720px) {
  .core-feature-btn {
    width: min(100%, 148px);
    height: 128px;
    border-radius: 22px;
  }

  .core-feature-btn__icon {
    width: 58px;
    height: 58px;
  }
}
</style>
