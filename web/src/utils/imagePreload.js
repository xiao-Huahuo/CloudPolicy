export function normalizeImageSources(sources = []) {
  const seen = new Set()
  const normalized = []

  for (const source of sources) {
    if (typeof source !== 'string') continue
    const value = source.trim()
    if (!value || seen.has(value)) continue
    seen.add(value)
    normalized.push(value)
  }

  return normalized
}

export function getImageLoadingAttrs(index, eagerCount = 0) {
  if (index < eagerCount) {
    return {
      loading: 'eager',
      fetchpriority: 'high',
    }
  }

  return {
    loading: 'lazy',
    fetchpriority: 'low',
  }
}

export function preloadImages(
  sources,
  {
    limit = Number.POSITIVE_INFINITY,
    imageFactory = () => new Image(),
    useIdleCallback = true,
    idleTimeout = 1200,
    delayMs = 160,
  } = {}
) {
  const normalizedSources = normalizeImageSources(sources).slice(0, limit)
  if (!normalizedSources.length) return []

  const run = () => {
    normalizedSources.forEach((src) => {
      const image = imageFactory()
      image.decoding = 'async'
      image.src = src
      if (typeof image.decode === 'function') {
        image.decode().catch(() => {})
      }
    })
  }

  if (typeof window === 'undefined') {
    return normalizedSources
  }

  if (useIdleCallback && 'requestIdleCallback' in window) {
    window.requestIdleCallback(run, { timeout: idleTimeout })
    return normalizedSources
  }

  window.setTimeout(run, delayMs)
  return normalizedSources
}
