<script setup>
import { computed } from 'vue';
import ThinkingLoaderBase from '../../../super-comonents/loader.vue';

const props = defineProps({
  size: {
    type: [Number, String],
    default: 44,
  },
  label: {
    type: String,
    default: '',
  },
  color: {
    type: String,
    default: '',
  },
  center: {
    type: Boolean,
    default: true,
  },
  compact: {
    type: Boolean,
    default: false,
  },
});

const pixelSize = computed(() => {
  const parsed = Number.parseFloat(String(props.size));
  return Number.isFinite(parsed) ? `${parsed}px` : String(props.size);
});

const loaderStyle = computed(() => ({
  width: pixelSize.value,
  height: pixelSize.value,
  '--loader-color': props.color || 'var(--ui-loader-color)',
}));
</script>

<template>
  <div class="agent-loader" :class="{ 'is-centered': center, 'is-compact': compact }">
    <div class="agent-loader__visual" :style="loaderStyle">
      <ThinkingLoaderBase />
    </div>
    <span v-if="label" class="agent-loader__label">{{ label }}</span>
  </div>
</template>

<style scoped>
.agent-loader {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  color: var(--text-secondary);
}

.agent-loader.is-centered {
  justify-content: center;
}

.agent-loader.is-compact {
  gap: 8px;
}

.agent-loader__visual {
  position: relative;
  flex: 0 0 auto;
}

.agent-loader__label {
  font-size: 13px;
  font-weight: 600;
  line-height: 1.4;
}
</style>
