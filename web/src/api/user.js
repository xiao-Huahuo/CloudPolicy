import { apiClient, API_ROUTES } from '@/router/api_routes';

export const login = (identity, password) => {
  const params = new URLSearchParams();
  params.append('username', identity);
  params.append('password', password);
  return apiClient.post(API_ROUTES.LOGIN, params, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
};

export const passwordLogin = (identity, password) => {
  return apiClient.post(API_ROUTES.AUTH_PASSWORD_LOGIN, { identity, password });
};

export const getCaptcha = () => {
  return apiClient.get(API_ROUTES.AUTH_CAPTCHA);
};

export const sendPhoneCode = (payload) => {
  return apiClient.post(API_ROUTES.AUTH_PHONE_SEND_CODE, payload);
};

export const phoneRegister = (payload) => {
  return apiClient.post(API_ROUTES.AUTH_PHONE_REGISTER, payload);
};

export const phoneLogin = (payload) => {
  return apiClient.post(API_ROUTES.AUTH_PHONE_LOGIN, payload);
};

export const register = (userData) => {
  return apiClient.post(API_ROUTES.REGISTER, userData);
};

export const verifyEmail = (email, code) => {
  return apiClient.post(API_ROUTES.VERIFY_EMAIL, { email, code });
};

export const resendVerification = (email) => {
  return apiClient.post(API_ROUTES.RESEND_VERIFICATION, { email });
};

export const getRecoveryOptions = (identifier) => {
  return apiClient.post(API_ROUTES.AUTH_RECOVERY_OPTIONS, { identifier });
};

export const sendRecoveryCode = (payload) => {
  return apiClient.post(API_ROUTES.AUTH_RECOVERY_SEND, payload);
};

export const resetPassword = (payload) => {
  return apiClient.post(API_ROUTES.AUTH_PASSWORD_RESET, payload);
};

export const setPassword = (payload) => {
  return apiClient.post(API_ROUTES.AUTH_PASSWORD_SET, payload);
};

export const changePassword = (payload) => {
  return apiClient.post(API_ROUTES.AUTH_PASSWORD_CHANGE, payload);
};

export const sendEmailCode = (payload) => {
  return apiClient.post(API_ROUTES.AUTH_EMAIL_SEND_CODE, payload);
};

export const bindEmail = (payload) => {
  return apiClient.post(API_ROUTES.AUTH_EMAIL_BIND, payload);
};

export const bindPhone = (payload) => {
  return apiClient.post(API_ROUTES.AUTH_PHONE_BIND, payload);
};

export const getMe = (token) => {
  return apiClient.get(API_ROUTES.GET_ME, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
};
