import { apiClient, API_ROUTES } from '@/router/api_routes';

export const chatWithAI = (message) => {
  return apiClient.post(API_ROUTES.CHAT_AI, { message });
};
