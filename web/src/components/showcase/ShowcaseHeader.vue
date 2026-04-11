<template>
  <header
    class="sc-header"
    :class="{
      scrolled: isScrolled,
      'always-transparent': shouldStayTransparent,
      'transparent-top': props.transparentTop,
      'top-light': props.topText === 'light',
      'appearance-transitioning': isAppearanceTransitioning,
    }"
  >
    <div class="sc-header-inner">
      <div class="sc-logo" @click="router.push('/showcase')">
        <img v-if="!noImg" src="@/assets/photos/main-icon.png" alt="" class="sc-logo-img" @error="noImg = true" />
        <span>云枢观策</span>
      </div>

      <nav class="sc-nav">
        <router-link to="/showcase" class="sc-link">首页</router-link>
        <router-link to="/showcase/discovery" class="sc-link">政策广场</router-link>
        <router-link to="/showcase/screen" class="sc-link">数据大屏</router-link>
      </nav>

      <div class="sc-actions">
        <label class="theme-switch" title="切换明暗模式">
          <input class="theme-switch__checkbox" type="checkbox" :checked="isDark" @change="toggleTheme" />
          <div class="theme-switch__container">
            <div class="theme-switch__clouds"></div>
            <div class="theme-switch__stars-container">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 144 55" fill="none">
                <path
                  fill-rule="evenodd"
                  clip-rule="evenodd"
                  d="M135.831 3.00688C135.055 3.85027 134.111 4.29946 133 4.35447C134.111 4.40947 135.055 4.85867 135.831 5.71206C136.607 6.55545 136.996 7.56878 136.996 8.75C136.996 7.56878 137.385 6.55545 138.161 5.71206C138.937 4.85867 139.881 4.40947 141 4.35447C139.881 4.29946 138.937 3.85027 138.161 3.00688C137.385 2.16348 136.996 1.15016 136.996 0C136.996 1.15016 136.607 2.16348 135.831 3.00688ZM123.831 23.0069C123.055 23.8503 122.111 24.2995 121 24.3545C122.111 24.4095 123.055 24.8587 123.831 25.7121C124.607 26.5555 124.996 27.5688 124.996 28.75C124.996 27.5688 125.385 26.5555 126.161 25.7121C126.937 24.8587 127.881 24.4095 129 24.3545C127.881 24.2995 126.937 23.8503 126.161 23.0069C125.385 22.1635 124.996 21.1502 124.996 20C124.996 21.1502 124.607 22.1635 123.831 23.0069ZM97.831 43.0069C97.055 43.8503 96.1114 44.2995 95 44.3545C96.1114 44.4095 97.055 44.8587 97.831 45.7121C98.607 46.5555 98.9959 47.5688 98.9959 48.75C98.9959 47.5688 99.3849 46.5555 100.161 45.7121C100.937 44.8587 101.881 44.4095 103 44.3545C101.881 44.2995 100.937 43.8503 100.161 43.0069C99.3849 42.1635 98.9959 41.1502 98.9959 40C98.9959 41.1502 98.607 42.1635 97.831 43.0069Z"
                  fill="white"
                />
              </svg>
            </div>
            <div class="theme-switch__circle-container">
              <div class="theme-switch__sun-moon-container">
                <div class="theme-switch__moon">
                  <div class="theme-switch__spot"></div>
                  <div class="theme-switch__spot"></div>
                  <div class="theme-switch__spot"></div>
                </div>
              </div>
            </div>
          </div>
        </label>

        <button
          class="scheme-switch"
          :class="{ 'is-switching': isSchemeSwitching }"
          type="button"
          :disabled="isSchemeSwitching"
          :aria-label="`切换品牌色系，当前：${currentSchemeLabel}，点击切换到：${nextSchemeLabel}`"
          :title="`切换品牌色系，当前：${currentSchemeLabel}，点击切换到：${nextSchemeLabel}`"
          @click.stop.prevent="handleColorSchemeToggle"
        >
          <span class="scheme-switch__inner"></span>
        </button>

        <button class="sc-btn-primary" @click="router.push('/agent')">进入系统</button>

        <button v-if="!userStore.token" @click.stop="emitLoginEvent" class="login-capsule">登录</button>

        <div v-else class="user-profile" @click="handleUserClick" title="个人中心">
          <img v-if="displayAvatar" :src="displayAvatar" alt="avatar" class="header-avatar" />
          <div v-else class="header-avatar-placeholder">
            <svg
              viewBox="0 0 24 24"
              width="20"
              height="20"
              stroke="currentColor"
              stroke-width="2"
              fill="none"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </div>
        </div>

        <button v-if="userStore.token" class="icon-btn logout-btn" @click="handleLogout" title="退出登录">
          <svg
            viewBox="0 0 24 24"
            width="20"
            height="20"
            stroke="currentColor"
            stroke-width="2"
            fill="none"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
            <polyline points="16 17 21 12 16 7"></polyline>
            <line x1="21" y1="12" x2="9" y2="12"></line>
          </svg>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/stores/auth.js';
import { useAppearanceTransition } from '@/composables/useAppearanceTransition';
import { COLOR_SCHEME_OPTIONS, useSettingsStore } from '@/stores/settings';
import { resolveAvatarUrl } from '@/utils/avatar.js';

const props = defineProps({
  transparentTop: {
    type: Boolean,
    default: true,
  },
  topText: {
    type: String,
    default: 'dark',
  },
  forceScrolled: {
    type: Boolean,
    default: false,
  },
});

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const settingsStore = useSettingsStore();

const scrolled = ref(false);
const noImg = ref(false);
const isDark = ref(false);
const isSchemeSwitching = ref(false);
let themeObserver = null;
const shouldStayTransparent = computed(() => route.name === 'showcase' || route.name === 'showcase-screen');
const { isAppearanceTransitioning } = useAppearanceTransition([shouldStayTransparent]);

const colorSchemes = COLOR_SCHEME_OPTIONS;
const isScrolled = computed(() => scrolled.value || props.forceScrolled);

const currentSchemeIndex = computed(() => {
  const currentValue = settingsStore.settings.color_scheme;
  const matchedIndex = colorSchemes.findIndex((item) => item.value === currentValue);
  return matchedIndex >= 0 ? matchedIndex : 0;
});

const currentSchemeLabel = computed(() => colorSchemes[currentSchemeIndex.value].label);
const nextSchemeValue = computed(() => settingsStore.getNextColorScheme(settingsStore.settings.color_scheme));
const nextSchemeLabel = computed(() => {
  const targetScheme = colorSchemes.find((item) => item.value === nextSchemeValue.value);
  return targetScheme?.label ?? colorSchemes[0].label;
});

const onScroll = () => {
  scrolled.value = window.scrollY > 40;
};

const syncThemeFromDom = () => {
  isDark.value = document.documentElement.getAttribute('data-theme') === 'dark';
};

const toggleTheme = async () => {
  const newTheme = isDark.value ? 'light' : 'dark';
  settingsStore.applyTheme(newTheme);
  settingsStore.settings.theme_mode = newTheme;
  if (userStore.token) {
    await settingsStore.updateSettings({ theme_mode: newTheme });
  }
  syncThemeFromDom();
};

const handleColorSchemeToggle = async () => {
  if (isSchemeSwitching.value) return;
  isSchemeSwitching.value = true;
  try {
    await settingsStore.setColorScheme(nextSchemeValue.value, {
      persist: Boolean(userStore.token),
    });
  } finally {
    isSchemeSwitching.value = false;
  }
};

const displayAvatar = computed(() => {
  return resolveAvatarUrl(userStore.user?.avatar_url);
});

const emitLoginEvent = () => window.dispatchEvent(new CustomEvent('open-login-modal'));
const handleUserClick = () => {
  if (userStore.token) router.push('/profile');
};
const handleLogout = () => {
  if (confirm('确定要退出登录吗？')) {
    userStore.logout();
    router.push('/showcase');
  }
};

onMounted(() => {
  onScroll();
  syncThemeFromDom();
  window.addEventListener('scroll', onScroll);
  themeObserver = new MutationObserver(syncThemeFromDom);
  themeObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-theme'],
  });
});

onBeforeUnmount(() => {
  window.removeEventListener('scroll', onScroll);
  themeObserver?.disconnect();
});
</script>

<style scoped>
.sc-header {
  --sc-header-text: var(--shell-text);
  --sc-header-link: var(--shell-text-muted);
  --sc-header-link-hover-bg: var(--shell-glass-hover);
  --sc-header-link-hover-text: var(--shell-text);
  --sc-header-link-active-bg: var(--sidebar-active-bg);
  --sc-header-link-active-shadow:
    0 0 16px var(--scheme-toggle-glow),
    inset 0 0 0 1px var(--sidebar-active-border);
  position: fixed;
  top: 12px;
  left: 50%;
  right: auto;
  width: min(1200px, calc(100vw - 32px), 66.666vw);
  transform: translateX(-50%);
  z-index: 100;
  height: 64px;
  padding: 0 28px;
  background: var(--header-bg);
  backdrop-filter: blur(16px);
  border: 1px solid var(--shell-glass-border);
  border-radius: 999px;
  box-shadow: 0 16px 36px rgba(9, 19, 31, 0.12);
  transition:
    background 0.45s ease,
    box-shadow 0.45s ease,
    border-color 0.45s ease,
    color 0.35s ease;
}

.sc-header.scrolled:not(.transparent-top) {
  background: var(--header-bg);
}

.sc-header.transparent-top:not(.scrolled) {
  background: transparent;
  box-shadow: none;
  border-color: transparent;
  backdrop-filter: none;
}

.sc-header.always-transparent,
.sc-header.always-transparent.scrolled,
.sc-header.always-transparent.transparent-top {
  background: transparent;
  box-shadow: none;
  border-color: transparent;
  backdrop-filter: none;
}

.sc-header.transparent-top.top-light:not(.scrolled),
.sc-header.always-transparent.top-light {
  --sc-header-text: #ffffff;
  --sc-header-link: rgba(255, 255, 255, 0.9);
  --sc-header-link-hover-bg: rgba(255, 255, 255, 0.18);
  --sc-header-link-hover-text: #ffffff;
  --sc-header-link-active-bg: rgba(255, 255, 255, 0.18);
  --sc-header-link-active-shadow:
    0 0 18px rgba(255, 255, 255, 0.16),
    inset 0 0 0 1px rgba(255, 255, 255, 0.3);
}

.sc-header-inner {
  width: 100%;
  max-width: none;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  gap: 32px;
}

.sc-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 18px;
  font-weight: 800;
  color: var(--sc-header-text);
  transition: color 0.35s ease;
}

.sc-logo-img {
  width: 28px;
  height: 28px;
  object-fit: contain;
  filter: none;
}

.sc-nav {
  display: flex;
  gap: 4px;
  flex: 1;
  justify-content: center;
}

.sc-link {
  padding: 6px 16px;
  border-radius: 20px;
  color: var(--sc-header-link);
  text-decoration: none;
  font-size: 14px;
  transition:
    background 0.35s ease,
    color 0.35s ease,
    box-shadow 0.35s ease;
}

.sc-link:hover {
  background: var(--sc-header-link-hover-bg);
  color: var(--sc-header-link-hover-text);
}

.sc-link.router-link-active {
  color: var(--shell-text);
  background: var(--sc-header-link-active-bg);
  box-shadow: var(--sc-header-link-active-shadow);
}

.sc-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.sc-btn-primary {
  border: none;
  color: #fff;
  padding: 8px 20px;
  border-radius: 999px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
  background: var(--scheme-toggle-gradient);
  box-shadow: 0 10px 20px color-mix(in srgb, var(--scheme-toggle-glow) 88%, transparent);
  transition:
    transform 0.2s ease,
    box-shadow 0.35s ease,
    background 0.35s ease;
}

.sc-btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 14px 24px color-mix(in srgb, var(--scheme-toggle-glow) 100%, transparent);
}

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--sc-header-link);
  transition: color 0.35s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-btn:hover {
  color: var(--sc-header-text);
}

.user-profile {
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--shell-glass-border);
  transition: border-color 0.35s ease;
}

.header-avatar-placeholder {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background-color: var(--shell-glass-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--sc-header-text);
  transition: background-color 0.35s ease, color 0.35s ease;
}

.login-capsule {
  background-color: var(--shell-glass-bg);
  color: var(--sc-header-text);
  border: 1px solid var(--shell-glass-border);
  padding: 7px 16px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition:
    background 0.35s ease,
    border-color 0.35s ease,
    color 0.35s ease;
}

.login-capsule:hover {
  background-color: var(--shell-glass-hover);
}

.scheme-switch {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: 1px solid var(--shell-glass-border);
  background: var(--scheme-toggle-gradient);
  box-shadow:
    inset 0 0 0 1px rgba(255, 255, 255, 0.12),
    0 0 16px var(--scheme-toggle-glow);
  cursor: pointer;
  padding: 0;
  overflow: hidden;
  appearance: none;
  transition:
    transform 0.2s ease,
    box-shadow 0.35s ease,
    background 0.35s ease,
    border-color 0.35s ease;
}

.scheme-switch::before {
  content: '';
  position: absolute;
  inset: 4px;
  border-radius: 50%;
  background:
    radial-gradient(circle at 30% 28%, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0) 44%),
    linear-gradient(145deg, rgba(255, 255, 255, 0.28), rgba(255, 255, 255, 0) 62%);
  pointer-events: none;
}

.scheme-switch__inner {
  position: absolute;
  inset: 10px;
  border-radius: 50%;
  background: rgba(7, 14, 24, 0.22);
  border: 1px solid rgba(255, 255, 255, 0.22);
  backdrop-filter: blur(3px);
  pointer-events: none;
  transition: background 0.35s ease, border-color 0.35s ease;
}

.scheme-switch:hover {
  transform: translateY(-1px);
  box-shadow:
    inset 0 0 0 1px rgba(255, 255, 255, 0.12),
    0 0 20px var(--scheme-toggle-glow);
}

.scheme-switch.is-switching {
  opacity: 0.7;
}

.scheme-switch:disabled {
  cursor: wait;
}

.theme-switch {
  --toggle-size: 10px;
  --container-width: 5.625em;
  --container-height: 2.5em;
  --container-radius: 6.25em;
  --container-light-bg: #3d7eae;
  --container-night-bg: #1d1f2c;
  --circle-container-diameter: 3.375em;
  --sun-moon-diameter: 2.125em;
  --sun-bg: #ecca2f;
  --moon-bg: #c4c9d1;
  --spot-color: #959db1;
  --circle-container-offset: calc((var(--circle-container-diameter) - var(--container-height)) / 2 * -1);
  --stars-color: #fff;
  --clouds-color: #f3fdff;
  --back-clouds-color: #aacadf;
  --transition: 0.5s cubic-bezier(0, -0.02, 0.4, 1.25);
  --circle-transition: 0.3s cubic-bezier(0, -0.02, 0.35, 1.17);
  font-size: var(--toggle-size);
  cursor: pointer;
}

.theme-switch *,
.theme-switch *::before,
.theme-switch *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  font-size: var(--toggle-size);
}

.theme-switch__checkbox {
  display: none;
}

.theme-switch__container {
  width: var(--container-width);
  height: var(--container-height);
  background-color: var(--container-light-bg);
  border-radius: var(--container-radius);
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 -0.062em 0.062em rgba(0, 0, 0, 0.25), 0 0.062em 0.125em rgba(255, 255, 255, 0.94);
  transition: var(--transition);
  position: relative;
}

.theme-switch__container::before {
  content: '';
  position: absolute;
  z-index: 1;
  inset: 0;
  box-shadow: 0 0.05em 0.187em rgba(0, 0, 0, 0.25) inset, 0 0.05em 0.187em rgba(0, 0, 0, 0.25) inset;
  border-radius: var(--container-radius);
}

.theme-switch__checkbox:checked + .theme-switch__container {
  background-color: var(--container-night-bg);
}

.theme-switch__circle-container {
  width: var(--circle-container-diameter);
  height: var(--circle-container-diameter);
  background-color: rgba(255, 255, 255, 0.1);
  position: absolute;
  left: var(--circle-container-offset);
  top: var(--circle-container-offset);
  border-radius: 50%;
  box-shadow:
    inset 0 0 0 3.272em rgba(255, 255, 255, 0.1),
    inset 0 0 0 3.272em rgba(255, 255, 255, 0.1),
    0 0 0 0.625em rgba(255, 255, 255, 0.1),
    0 0 0 1.25em rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--circle-transition);
}

.theme-switch__checkbox:checked + .theme-switch__container .theme-switch__circle-container {
  left: calc(100% - var(--circle-container-offset) - var(--circle-container-diameter));
}

.theme-switch__sun-moon-container {
  pointer-events: none;
  position: relative;
  z-index: 2;
  width: var(--sun-moon-diameter);
  height: var(--sun-moon-diameter);
  background-color: var(--sun-bg);
  border-radius: 50%;
  box-shadow: 0.062em 0.062em 0.062em 0 rgba(254, 255, 239, 0.61) inset, 0 -0.062em 0.062em 0 #a1872a inset;
  filter: drop-shadow(0.062em 0.125em 0.125em rgba(0, 0, 0, 0.25))
    drop-shadow(0 0.062em 0.125em rgba(0, 0, 0, 0.25));
  overflow: hidden;
  transition: var(--transition);
}

.theme-switch__checkbox:checked + .theme-switch__container .theme-switch__sun-moon-container {
  background-color: var(--moon-bg);
  box-shadow: 0.062em 0.062em 0.062em 0 rgba(254, 255, 239, 0.61) inset, 0 -0.062em 0.062em 0 #969696 inset;
}

.theme-switch__moon {
  transform: translateX(100%);
  width: 100%;
  height: 100%;
  background-color: var(--moon-bg);
  border-radius: inherit;
  transition: var(--transition);
  box-shadow: 0.062em 0.062em 0.062em 0 rgba(254, 255, 239, 0.61) inset, 0 -0.062em 0.062em 0 #969696 inset;
}

.theme-switch__checkbox:checked + .theme-switch__container .theme-switch__moon {
  transform: translateX(0);
}

.theme-switch__spot {
  position: absolute;
  top: 0.75em;
  left: 0.312em;
  width: 0.75em;
  height: 0.75em;
  border-radius: 50%;
  background-color: var(--spot-color);
  box-shadow: 0 0.0312em 0.062em rgba(0, 0, 0, 0.25) inset;
}

.theme-switch__spot:nth-of-type(2) {
  width: 0.375em;
  height: 0.375em;
  top: 0.937em;
  left: 1.375em;
}

.theme-switch__spot:nth-of-type(3) {
  width: 0.25em;
  height: 0.25em;
  top: 0.312em;
  left: 1em;
}

.theme-switch__clouds {
  width: 1.25em;
  height: 1.25em;
  background-color: var(--clouds-color);
  border-radius: 50%;
  position: absolute;
  bottom: -0.625em;
  left: 0.312em;
  box-shadow:
    0.937em 0.312em 0 var(--clouds-color),
    -0.312em -0.312em 0 0.625em var(--clouds-color),
    1.437em 0.375em 0 0.5em var(--clouds-color),
    0.5em -0.125em 0 0.625em var(--clouds-color),
    2.187em 0 0 0.312em var(--clouds-color);
  transition: 0.5s cubic-bezier(0, -0.02, 0.4, 1.25);
}

.theme-switch__checkbox:checked + .theme-switch__container .theme-switch__clouds {
  bottom: -1.25em;
}

.theme-switch__stars-container {
  position: absolute;
  color: var(--stars-color);
  top: -100%;
  left: 0.312em;
  width: 2.75em;
  height: auto;
  transition: var(--transition);
}

.theme-switch__checkbox:checked + .theme-switch__container .theme-switch__stars-container {
  top: 0.312em;
}

@media (max-width: 1120px) {
  .sc-header {
    width: calc(100vw - 24px);
    padding: 0 18px;
  }

  .sc-nav {
    display: none;
  }

  .sc-header-inner {
    gap: 16px;
  }
}

@media (max-width: 720px) {
  .sc-header {
    top: 8px;
    width: calc(100vw - 16px);
    padding: 0 14px;
  }

  .sc-actions {
    gap: 8px;
  }

  .theme-switch,
  .scheme-switch {
    display: none;
  }

  .sc-btn-primary {
    display: none;
  }

  .sc-logo span {
    font-size: 16px;
  }
}
</style>
