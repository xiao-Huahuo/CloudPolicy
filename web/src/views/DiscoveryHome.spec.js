import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { describe, expect, it, vi, afterEach } from 'vitest'

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}))

const hotNewsItems = Array.from({ length: 8 }, (_, index) => ({
  title: `新闻 ${index + 1}`,
  description: `描述 ${index + 1}`,
  link: `https://example.com/news-${index + 1}`,
  pubDate: '2026-04-29',
}))

const centralDocsItems = Array.from({ length: 3 }, (_, index) => ({
  title: `政策 ${index + 1}`,
  description: `政策描述 ${index + 1}`,
  link: `https://example.com/doc-${index + 1}`,
  pubDate: '2026-04-29',
}))

vi.mock('@/api/news', () => ({
  getHotNews: vi.fn(async () => ({ data: { items: hotNewsItems } })),
  getCentralDocs: vi.fn(async () => ({ data: { items: centralDocsItems } })),
  getDailySummary: vi.fn(async () => ({
    data: {
      update_time: '09:00',
      news_count: 8,
      doc_count: 3,
      top_news: '今日热点',
      top_doc: '最新政策',
    },
  })),
  searchNews: vi.fn(async () => ({ data: { items: [] } })),
}))

vi.mock('@/router/api_routes', () => ({
  apiClient: {
    get: vi.fn(async () => ({ data: [] })),
    post: vi.fn(async () => ({ data: { like_count: 1 } })),
  },
  API_ROUTES: {
    POLICY_DOCS_APPROVED: '/policy-docs/approved',
    POLICY_DOC_LIKE: (id) => `/policy-docs/${id}/like`,
  },
}))

vi.mock('@/stores/auth.js', () => ({
  useUserStore: () => ({
    token: '',
  }),
}))

import DiscoveryHome from './DiscoveryHome.vue'

const flushView = async () => {
  await Promise.resolve()
  await nextTick()
  await Promise.resolve()
  await nextTick()
}

describe('DiscoveryHome image loading strategy', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('eagerly loads every rendered news cover so scrolling does not trigger blank cards', async () => {
    vi.useFakeTimers()
    const originalImage = globalThis.Image
    const imageStub = vi.fn(function ImageStub() {
      this.decode = vi.fn(() => Promise.resolve())
    })
    globalThis.Image = imageStub
    window.requestIdleCallback = (callback) => callback()

    const wrapper = mount(DiscoveryHome, {
      global: {
        stubs: {
          RouterLink: {
            template: '<a><slot /></a>',
          },
        },
      },
    })

    await flushView()

    const covers = wrapper.findAll('.nc-cover')
    expect(covers.length).toBeGreaterThan(6)
    expect(covers.every((cover) => cover.attributes('loading') === 'eager')).toBe(true)

    wrapper.unmount()
    globalThis.Image = originalImage
    vi.useRealTimers()
  })
})
