const FALLBACK_COLORS = {
  primary: '#c0392b',
  primaryLight: '#e45846',
  primaryDark: '#8e231b',
  secondary: '#e67e22',
  accentCool: '#58cbff',
  accentMint: '#80fab0',
  textPrimary: '#111111',
  textSecondary: '#666666',
  textMuted: '#aaaaaa',
  border: '#e0e0e0',
  cardBg: '#ffffff',
};

const getRoot = () => document.documentElement;

const readCssVar = (name, fallback) => {
  if (typeof window === 'undefined') {
    return fallback;
  }
  const value = getComputedStyle(getRoot()).getPropertyValue(name).trim();
  return value || fallback;
};

const expandHex = (value) => {
  if (value.length === 4) {
    return `#${value[1]}${value[1]}${value[2]}${value[2]}${value[3]}${value[3]}`;
  }
  return value;
};

const parseColor = (value) => {
  if (!value) return null;
  const color = value.trim();

  if (color.startsWith('#')) {
    const normalized = expandHex(color);
    const hex = normalized.slice(1);
    if (hex.length !== 6) return null;
    return {
      r: parseInt(hex.slice(0, 2), 16),
      g: parseInt(hex.slice(2, 4), 16),
      b: parseInt(hex.slice(4, 6), 16),
    };
  }

  const rgbMatch = color.match(/^rgba?\(([^)]+)\)$/i);
  if (!rgbMatch) return null;

  const parts = rgbMatch[1]
    .split(',')
    .map((part) => Number.parseFloat(part.trim()))
    .filter((part) => Number.isFinite(part));

  if (parts.length < 3) return null;

  return {
    r: parts[0],
    g: parts[1],
    b: parts[2],
  };
};

export const withAlpha = (color, alpha) => {
  const parsed = parseColor(color);
  if (!parsed) {
    return color;
  }
  return `rgba(${parsed.r}, ${parsed.g}, ${parsed.b}, ${alpha})`;
};

export const getChartTheme = () => {
  const root = getRoot();
  const dark = root.getAttribute('data-theme') === 'dark';
  const primary = readCssVar('--color-primary', FALLBACK_COLORS.primary);
  const primaryLight = readCssVar('--color-primary-light', FALLBACK_COLORS.primaryLight);
  const primaryDark = readCssVar('--color-primary-dark', FALLBACK_COLORS.primaryDark);
  const secondary = readCssVar('--color-secondary', FALLBACK_COLORS.secondary);
  const accentCool = readCssVar('--color-accent-cool', FALLBACK_COLORS.accentCool);
  const accentMint = readCssVar('--color-accent-mint', FALLBACK_COLORS.accentMint);
  const textPrimary = readCssVar('--text-primary', FALLBACK_COLORS.textPrimary);
  const textSecondary = readCssVar('--text-secondary', FALLBACK_COLORS.textSecondary);
  const textMuted = readCssVar('--text-muted', FALLBACK_COLORS.textMuted);
  const border = readCssVar('--border-color', FALLBACK_COLORS.border);
  const cardBg = readCssVar('--card-bg', FALLBACK_COLORS.cardBg);

  return {
    dark,
    primary,
    primaryLight,
    primaryDark,
    secondary,
    accentCool,
    accentMint,
    textPrimary,
    textSecondary,
    textMuted,
    border,
    cardBg,
    palette: [
      primary,
      secondary,
      accentCool,
      accentMint,
      primaryLight,
      primaryDark,
      withAlpha(primary, dark ? 0.78 : 0.68),
      withAlpha(accentCool, dark ? 0.78 : 0.68),
    ],
    trio: [primary, secondary, accentCool],
    tooltipBg: dark ? withAlpha(cardBg, 0.96) : 'rgba(255, 255, 255, 0.96)',
    tooltipBorder: withAlpha(border, dark ? 0.76 : 0.9),
    axisLine: withAlpha(textSecondary, dark ? 0.34 : 0.22),
    splitLine: withAlpha(textSecondary, dark ? 0.18 : 0.12),
    softPrimary: withAlpha(primary, dark ? 0.28 : 0.18),
    softSecondary: withAlpha(secondary, dark ? 0.28 : 0.18),
    softAccent: withAlpha(accentCool, dark ? 0.28 : 0.18),
    glowPrimary: withAlpha(primary, dark ? 0.34 : 0.24),
    glowAccent: withAlpha(accentCool, dark ? 0.34 : 0.24),
  };
};

export const observeChartAppearance = (callback) => {
  if (typeof MutationObserver === 'undefined') {
    return null;
  }
  const observer = new MutationObserver((mutations) => {
    const changed = mutations.some((mutation) => (
      mutation.type === 'attributes'
      && (mutation.attributeName === 'data-theme' || mutation.attributeName === 'data-color-scheme')
    ));
    if (changed) {
      callback();
    }
  });
  observer.observe(getRoot(), {
    attributes: true,
    attributeFilter: ['data-theme', 'data-color-scheme'],
  });
  return observer;
};
