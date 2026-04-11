<template>
  <div class="avatar-editor">
    <h3>选择或上传头像</h3>

    <div class="current-avatar-preview">
      <img v-if="currentAvatarSrc" :src="currentAvatarSrc" alt="Current Avatar" class="avatar-lg" />
    </div>

    <div class="default-avatars-grid">
      <div
        v-for="avatar in defaultAvatars"
        :key="avatar.value"
        class="default-avatar-item"
        :class="{ selected: selectedDefaultAvatar === avatar.value }"
        @click="selectDefaultAvatar(avatar.value)"
      >
        <img :src="avatar.path" :alt="avatar.name" class="avatar-sm" />
      </div>
    </div>

    <div class="upload-section">
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        style="display: none;"
        @change="handleFileUpload"
      />
      <button class="action-btn outline" @click="triggerFileInput">
        <svg
          viewBox="0 0 24 24"
          width="18"
          height="18"
          stroke="currentColor"
          stroke-width="2"
          fill="none"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M21.2 15c.7-1.2 1-2.5.7-3.9-.6-3.1-4-5.4-7.5-5.4-3.3 0-6.4 2.1-7.7 5.1C2.8 11.5 2 13.8 2 16c0 2.2.8 4.2 2.1 5.8"></path>
          <path d="M12 16v6"></path>
          <path d="M15 19l-3 3-3-3"></path>
        </svg>
        上传新头像
      </button>
      <span v-if="uploadingFile" class="file-name">{{ uploadingFile.name }}</span>
    </div>

    <div class="actions">
      <button class="action-btn primary" :disabled="isSaving" @click="saveAvatar">
        {{ isSaving ? '保存中...' : '保存' }}
      </button>
      <button class="action-btn" @click="$emit('close')">取消</button>
    </div>

    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue';
import { useUserStore } from '@/stores/auth.js';
import { apiClient, API_ROUTES } from '@/router/api_routes';
import {
  defaultAvatarOptions,
  normalizeDefaultAvatarValue,
  resolveAvatarUrl,
} from '@/utils/avatar.js';

const emit = defineEmits(['close', 'saved']);

const userStore = useUserStore();
const fileInput = ref(null);
const uploadingFile = ref(null);
const errorMessage = ref('');
const isSaving = ref(false);
const objectPreviewUrl = ref(null);

const defaultAvatars = defaultAvatarOptions;
const initialDefaultAvatar = normalizeDefaultAvatarValue(userStore.user?.avatar_url);
const selectedDefaultAvatar = ref(initialDefaultAvatar?.startsWith('default:') ? initialDefaultAvatar : null);

const clearObjectPreview = () => {
  if (objectPreviewUrl.value) {
    URL.revokeObjectURL(objectPreviewUrl.value);
    objectPreviewUrl.value = null;
  }
};

watch(
  uploadingFile,
  (file) => {
    clearObjectPreview();
    if (file) {
      objectPreviewUrl.value = URL.createObjectURL(file);
    }
  },
  { immediate: true }
);

onBeforeUnmount(() => {
  clearObjectPreview();
});

const currentAvatarSrc = computed(() => {
  if (objectPreviewUrl.value) {
    return objectPreviewUrl.value;
  }

  if (selectedDefaultAvatar.value) {
    return resolveAvatarUrl(selectedDefaultAvatar.value);
  }

  const currentUserAvatar = resolveAvatarUrl(userStore.user?.avatar_url);
  if (currentUserAvatar) {
    return currentUserAvatar;
  }

  return defaultAvatars[0]?.path || '';
});

const triggerFileInput = () => {
  fileInput.value?.click();
};

const handleFileUpload = (event) => {
  const file = event.target.files?.[0];
  if (!file) return;

  if (!file.type.startsWith('image/')) {
    errorMessage.value = '请选择图片文件。';
    uploadingFile.value = null;
    event.target.value = '';
    return;
  }

  if (file.size > 5 * 1024 * 1024) {
    errorMessage.value = '文件大小不能超过 5MB。';
    uploadingFile.value = null;
    event.target.value = '';
    return;
  }

  uploadingFile.value = file;
  selectedDefaultAvatar.value = null;
  errorMessage.value = '';
};

const selectDefaultAvatar = (avatarValue) => {
  selectedDefaultAvatar.value = avatarValue;
  uploadingFile.value = null;
  errorMessage.value = '';
  if (fileInput.value) {
    fileInput.value.value = '';
  }
};

const saveAvatar = async () => {
  isSaving.value = true;
  errorMessage.value = '';

  try {
    let newAvatarUrl = null;

    if (uploadingFile.value) {
      const formData = new FormData();
      formData.append('file', uploadingFile.value);
      const uploadRes = await apiClient.post(API_ROUTES.UPLOAD_AVATAR, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      newAvatarUrl = uploadRes.data.avatar_url;
    } else if (selectedDefaultAvatar.value) {
      newAvatarUrl = selectedDefaultAvatar.value;
    } else {
      emit('close');
      return;
    }

    await apiClient.patch(API_ROUTES.GET_ME, { avatar_url: newAvatarUrl });

    if (userStore.user) {
      userStore.user.avatar_url = newAvatarUrl;
    }

    emit('saved');
    emit('close');
  } catch (error) {
    console.error('保存头像失败:', error);
    errorMessage.value = error.response?.data?.detail || '保存头像失败';
  } finally {
    isSaving.value = false;
  }
};
</script>

<style scoped>
.avatar-editor {
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

h3 {
  font-size: 20px;
  color: #333;
  margin-bottom: 10px;
}

.current-avatar-preview {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid #eee;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f9f9f9;
}

.avatar-lg {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.default-avatars-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
  gap: 10px;
  width: 100%;
  max-width: 400px;
  margin-top: 10px;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 12px;
}

.default-avatar-item {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
  background-color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.default-avatar-item:hover {
  border-color: #ccc;
}

.default-avatar-item.selected {
  border-color: #000;
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
}

.avatar-sm {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-section {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 20px;
}

.file-name {
  font-size: 14px;
  color: #666;
}

.actions {
  display: flex;
  gap: 15px;
  margin-top: 30px;
}

.action-btn {
  padding: 10px 25px;
  border-radius: 20px;
  font-size: 15px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #ddd;
  background-color: #fff;
  color: #333;
}

.action-btn.outline {
  background: transparent;
  border-color: #ccc;
  color: #666;
  display: flex;
  align-items: center;
  gap: 5px;
}

.action-btn.outline:hover {
  border-color: #000;
  color: #000;
}

.action-btn.primary {
  background-color: #000;
  color: #fff;
  border-color: #000;
}

.action-btn.primary:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  color: #ff4d4f;
  margin-top: 15px;
  font-size: 14px;
}
</style>
