import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import DesignPhilosophySection from './DesignPhilosophySection.vue'
import UiShowcaseSection from './UiShowcaseSection.vue'
import { highlightCards, showcasePreloadImages } from './showcaseContent'
import HeroSectionSource from './HeroSection.vue?raw'
import ShowcaseHeaderSource from '../showcase/ShowcaseHeader.vue?raw'

describe('showcase landing content', () => {
  it('uses the formal overview copy in section 02', () => {
    vi.useFakeTimers()
    const wrapper = mount(UiShowcaseSection)
    const normalizedText = wrapper.text().replace(/\s+/g, ' ')

    expect(normalizedText).toContain(
      '通过五组核心界面联动展示检索、分析、阅读与交互能力，以统一的叙事节奏呈现产品完整体验， 使展示页兼具信息密度与正式、克制的品牌表达。'
    )

    wrapper.unmount()
    vi.useRealTimers()
  })

  it('removes the image block from the section 05 philosophy card', () => {
    vi.useFakeTimers()
    const wrapper = mount(DesignPhilosophySection)

    expect(wrapper.find('.card-visual').exists()).toBe(false)

    wrapper.unmount()
    vi.useRealTimers()
  })

  it('maps section 06 highlight cards to the real showcase images', () => {
    expect(highlightCards.map((item) => item.imagePath)).toEqual([
      'web/src/assets/photos/showcase-highlights/云小圆.png',
      'web/src/assets/photos/showcase-highlights/公共数据大屏.png',
      'web/src/assets/photos/showcase-highlights/可视化知识图谱.png',
      'web/src/assets/photos/showcase-highlights/刷剧资讯体验.png',
    ])
  })

  it('marks section 02 screenshots as eager once the section is mounted', () => {
    vi.useFakeTimers()
    const wrapper = mount(UiShowcaseSection)
    const slideImages = wrapper.findAll('.stage-slide img')

    expect(slideImages.length).toBeGreaterThan(0)
    expect(slideImages.every((image) => image.attributes('loading') === 'eager')).toBe(true)

    wrapper.unmount()
    vi.useRealTimers()
  })

  it('prepares a dedicated image preload list for the showcase landing page', () => {
    expect(showcasePreloadImages.length).toBeGreaterThan(10)
    expect(showcasePreloadImages).toEqual(expect.arrayContaining(highlightCards.map((item) => item.image)))
  })

  it('uses the formal platform wording on the showcase hero', () => {
    expect(HeroSectionSource).toContain('政策一体化平台')
    expect(HeroSectionSource).not.toContain('政务系统')
  })

  it('uses the shared brand title font in the showcase top bar', () => {
    expect(ShowcaseHeaderSource).toMatch(/\.sc-logo span\s*\{[\s\S]*font-family: "STKaiti", "KaiTi", "Noto Serif SC", "Source Han Serif SC", serif;/)
  })
})
