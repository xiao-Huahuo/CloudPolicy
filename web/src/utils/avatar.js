const avatarModules = import.meta.glob('../assets/photos/default-avatars/*.{jpg,jpeg,png,webp,gif}', {
  eager: true,
  import: 'default',
});

function normalizeAvatarName(name) {
  try {
    return decodeURIComponent(name);
  } catch {
    return name;
  }
}

export const defaultAvatarOptions = Object.entries(avatarModules)
  .map(([modulePath, assetUrl]) => {
    const fileName = modulePath.split('/').pop();
    const normalizedName = normalizeAvatarName(fileName);
    return {
      name: normalizedName,
      path: assetUrl,
      value: `default:${encodeURIComponent(normalizedName)}`,
    };
  })
  .sort((a, b) => a.name.localeCompare(b.name, 'zh-Hans-CN'));

const defaultAvatarMap = new Map(defaultAvatarOptions.map((item) => [item.value, item.path]));

export function normalizeDefaultAvatarValue(avatarUrl) {
  if (!avatarUrl?.startsWith('default:')) return avatarUrl || null;
  const rawName = avatarUrl.substring(8);
  return `default:${encodeURIComponent(normalizeAvatarName(rawName))}`;
}

export function resolveAvatarUrl(avatarUrl) {
  if (!avatarUrl) return null;
  if (!avatarUrl.startsWith('default:')) return avatarUrl;
  return defaultAvatarMap.get(normalizeDefaultAvatarValue(avatarUrl)) || null;
}
