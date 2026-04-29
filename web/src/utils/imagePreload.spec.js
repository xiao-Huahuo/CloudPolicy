import { describe, expect, it, vi } from 'vitest'

import { getImageLoadingAttrs, normalizeImageSources, preloadImages } from './imagePreload'

describe('imagePreload utilities', () => {
  it('normalizes image sources by trimming blanks and removing duplicates', () => {
    expect(normalizeImageSources([' /a.png ', '', null, '/b.png', '/a.png', '   '])).toEqual([
      '/a.png',
      '/b.png',
    ])
  })

  it('marks only the first visible images as eager and high priority', () => {
    expect(getImageLoadingAttrs(0, 3)).toEqual({ loading: 'eager', fetchpriority: 'high' })
    expect(getImageLoadingAttrs(2, 3)).toEqual({ loading: 'eager', fetchpriority: 'high' })
    expect(getImageLoadingAttrs(3, 3)).toEqual({ loading: 'lazy', fetchpriority: 'low' })
  })

  it('preloads only the normalized image sources up to the configured limit', () => {
    vi.useFakeTimers()
    const createdImages = []
    const imageFactory = () => {
      const image = {
        decode: vi.fn(() => Promise.resolve()),
      }
      createdImages.push(image)
      return image
    }

    const scheduledSources = preloadImages([' /a.png ', '/b.png', '/a.png'], {
      limit: 2,
      imageFactory,
      useIdleCallback: false,
    })

    expect(scheduledSources).toEqual(['/a.png', '/b.png'])
    expect(createdImages).toHaveLength(0)

    vi.runAllTimers()

    expect(createdImages).toHaveLength(2)
    expect(createdImages[0].src).toBe('/a.png')
    expect(createdImages[1].src).toBe('/b.png')
    expect(createdImages[0].decode).toHaveBeenCalledTimes(1)
    expect(createdImages[1].decode).toHaveBeenCalledTimes(1)

    vi.useRealTimers()
  })
})
