import { onBeforeUnmount, onMounted, ref, watch } from 'vue';

const APPEARANCE_ATTRIBUTES = ['data-theme', 'data-color-scheme'];

export function useAppearanceTransition(sources = [], duration = 820) {
  const isAppearanceTransitioning = ref(false);
  let observer = null;
  let timer = null;
  let appearanceSignature = '';
  const normalizedSources = Array.isArray(sources) ? sources : [sources];

  const readAppearanceSignature = () => (
    APPEARANCE_ATTRIBUTES
      .map((attribute) => document.documentElement.getAttribute(attribute) || '')
      .join('|')
  );

  const clearTransitionTimer = () => {
    if (!timer) return;
    clearTimeout(timer);
    timer = null;
  };

  const triggerTransition = () => {
    clearTransitionTimer();
    isAppearanceTransitioning.value = false;
    requestAnimationFrame(() => {
      isAppearanceTransitioning.value = true;
      timer = setTimeout(() => {
        isAppearanceTransitioning.value = false;
        timer = null;
      }, duration);
    });
  };

  const handleAppearanceMutation = () => {
    const nextSignature = readAppearanceSignature();
    if (nextSignature === appearanceSignature) return;
    appearanceSignature = nextSignature;
    triggerTransition();
  };

  onMounted(() => {
    appearanceSignature = readAppearanceSignature();
    observer = new MutationObserver(handleAppearanceMutation);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: APPEARANCE_ATTRIBUTES,
    });
  });

  onBeforeUnmount(() => {
    observer?.disconnect();
    clearTransitionTimer();
  });

  if (normalizedSources.length) {
    watch(
      normalizedSources,
      (newValues, oldValues) => {
        if (!oldValues) return;
        if (newValues.every((value, index) => value === oldValues[index])) return;
        triggerTransition();
      },
      { flush: 'post' }
    );
  }

  return {
    isAppearanceTransitioning,
  };
}
