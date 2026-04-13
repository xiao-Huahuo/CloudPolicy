import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { getMe, login as loginApi, passwordLogin as passwordLoginApi, phoneLogin as phoneLoginApi } from '@/api/user';

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || null);
  const user = ref(null);

  const setToken = (newToken) => {
    token.value = newToken;
    localStorage.setItem('token', newToken);
  };

  const applyAccessToken = async (accessToken) => {
    setToken(accessToken);
    await fetchUser();
  };

  const fetchUser = async () => {
    if (token.value) {
      try {
        const response = await getMe(token.value);
        user.value = response.data;
      } catch (error) {
        console.error('Failed to fetch user:', error);
        // Token 失效，清除
        token.value = null;
        user.value = null;
        localStorage.removeItem('token');
      }
    }
  };

  const login = async (username, password) => {
    const response = await loginApi(username, password);
    await applyAccessToken(response.data.access_token);
  };

  const loginWithPassword = async (identity, password) => {
    const response = await passwordLoginApi(identity, password);
    await applyAccessToken(response.data.access_token);
  };

  const loginWithPhone = async (phone, code) => {
    const response = await phoneLoginApi({ phone, code });
    await applyAccessToken(response.data.access_token);
  };

  const logout = () => {
    token.value = null;
    user.value = null;
    localStorage.removeItem('token');
  };

  const isAdmin = computed(() => user.value?.role === 'admin');
  const isCertified = computed(() => user.value?.role === 'certified');

  return {
    token,
    user,
    isAdmin,
    isCertified,
    login,
    loginWithPassword,
    loginWithPhone,
    applyAccessToken,
    logout,
    fetchUser,
  };
});
