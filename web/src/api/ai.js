import { apiClient, API_ROUTES } from '@/router/api_routes';

// 解析纯文本
export const createChatMessage = (original_text) => {
  return apiClient.post(API_ROUTES.CHAT_MESSAGE, { original_text });
};

// 解析带文件的信息 (包含 file_url 和提取后的文本)
export const createChatMessageWithFile = (original_text, file_url) => {
  return apiClient.post(API_ROUTES.CHAT_MESSAGE, {
      original_text: original_text,
      file_url: file_url
  });
};

// 上传文档并提取文本 (新接口对接)
export const uploadAndExtractDocument = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return apiClient.post(API_ROUTES.UPLOAD_DOCUMENT, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

// 获取历史解析记录
export const getChatMessages = (params = {}) => {
  return apiClient.get(API_ROUTES.CHAT_MESSAGE, { params });
};

// 切换语气版本 (老人版, 学生版等)
export const rewriteChatMessage = (id, target_audience) => {
  return apiClient.patch(`${API_ROUTES.CHAT_MESSAGE}${id}`, { target_audience });
};

// 删除单条记录
export const deleteChatMessage = (id) => {
  return apiClient.delete(`${API_ROUTES.CHAT_MESSAGE}${id}`);
};

// 批量删除记录
export const batchDeleteChatMessages = (ids) => {
  return apiClient.post(`${API_ROUTES.CHAT_MESSAGE}batch-delete`, { message_ids: ids });
};
