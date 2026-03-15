import { apiClient, API_ROUTES } from '@/router/api_routes';

// 解析新的文档
export const createChatMessage = (original_text) => {
  return apiClient.post(API_ROUTES.CHAT_MESSAGE, { original_text });
};

// 获取历史解析记录
export const getChatMessages = (params = {}) => {
  return apiClient.get(API_ROUTES.CHAT_MESSAGE, { params });
};

// 切换语气版本 (老人版, 学生版等)
export const rewriteChatMessage = (id, target_audience) => {
  // 注意这里去掉了模板字符串中额外的 '/'
  return apiClient.patch(`${API_ROUTES.CHAT_MESSAGE}${id}`, { target_audience });
};

// 删除单条记录
export const deleteChatMessage = (id) => {
  // 注意这里去掉了模板字符串中额外的 '/'
  return apiClient.delete(`${API_ROUTES.CHAT_MESSAGE}${id}`);
};

// 批量删除记录
export const batchDeleteChatMessages = (ids) => {
  // 注意这里去掉了模板字符串中额外的 '/'
  return apiClient.post(`${API_ROUTES.CHAT_MESSAGE}batch-delete`, { message_ids: ids });
};
