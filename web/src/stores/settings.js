import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiClient, API_ROUTES } from '@/router/api_routes';

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref({
    default_audience: 'none',
    theme_mode: 'light',
    system_notifications: true,
    color_scheme: 'classic'
  });

  const loading = ref(false);

  // 获取设置
  const fetchSettings = async () => {
    loading.value = true;
    try {
      const response = await apiClient.get(API_ROUTES.SETTINGS_ME);
      settings.value = {
        ...settings.value,
        ...response.data,
      };
      applyTheme(settings.value.theme_mode);
      applyColorScheme(settings.value.color_scheme);
    } catch (error) {
      console.error('获取设置失败:', error);
    } finally {
      loading.value = false;
    }
  };

  // 更新设置
  const updateSettings = async (newSettings) => {
    try {
      const response = await apiClient.patch(API_ROUTES.SETTINGS_ME, newSettings);
      settings.value = {
        ...settings.value,
        ...response.data,
      };
      if (newSettings.theme_mode !== undefined) {
        applyTheme(settings.value.theme_mode);
      }
      if (newSettings.color_scheme !== undefined) {
        applyColorScheme(settings.value.color_scheme);
      }
      return true;
    } catch (error) {
      console.error('更新设置失败:', error);
      return false;
    }
  };

  // 应用主题到整个应用
  const applyTheme = (theme) => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.setAttribute('data-theme', 'dark');
    } else if (theme === 'light') {
      root.setAttribute('data-theme', 'light');
    } else {
      // System
      if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        root.setAttribute('data-theme', 'dark');
      } else {
        root.setAttribute('data-theme', 'light');
      }
    }
    localStorage.setItem('theme_mode', theme);
  };

  const applyColorScheme = (scheme) => {
    const root = document.documentElement;
    root.setAttribute('data-color-scheme', scheme || 'classic');
    localStorage.setItem('color_scheme', scheme || 'classic');
  };

  const updateColorScheme = (scheme) => {
    settings.value.color_scheme = scheme;
    applyColorScheme(scheme);
  };

  const initAppearance = () => {
    const storedTheme = localStorage.getItem('theme_mode');
    const storedScheme = localStorage.getItem('color_scheme');
    if (storedTheme) settings.value.theme_mode = storedTheme;
    if (storedScheme) settings.value.color_scheme = storedScheme;
    applyTheme(settings.value.theme_mode);
    applyColorScheme(settings.value.color_scheme);
  };

  return {
    settings,
    loading,
    fetchSettings,
    updateSettings,
    applyTheme,
    applyColorScheme,
    updateColorScheme,
    initAppearance,
  };
});
