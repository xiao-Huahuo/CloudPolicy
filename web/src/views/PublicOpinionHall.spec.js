import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const pushMock = vi.fn()

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: pushMock,
  }),
}))

vi.mock('@/stores/auth.js', () => ({
  useUserStore: () => ({
    user: { role: 'normal' },
  }),
}))

const feedOpinions = Array.from({ length: 18 }, (_, index) => ({
  id: index + 1,
  opinion_type: index % 3 === 0 ? 'review' : (index % 3 === 1 ? 'correction' : 'message'),
  user_name: `用户${index + 1}`,
  created_time: '2026-05-01T10:00:00Z',
  content: `反馈内容 ${index + 1}`,
  rating: (index % 5) + 1,
  like_count: index,
}))

const docs = Array.from({ length: 5 }, (_, index) => ({
  id: index + 1,
  title: `政策文件 ${index + 1}`,
  category: '民生',
  view_count: 100 + index,
  like_count: 20 + index,
}))

vi.mock('@/router/api_routes', () => ({
  apiClient: {
    get: vi.fn((url) => {
      if (url === '/policy-documents/approved') return Promise.resolve({ data: docs })
      if (url === '/opinions/feed') return Promise.resolve({ data: feedOpinions })
      return Promise.resolve({ data: [] })
    }),
    post: vi.fn(async () => ({ data: { like_count: 99 } })),
  },
  API_ROUTES: {
    POLICY_DOCS_APPROVED: '/policy-documents/approved',
    OPINIONS_FEED: '/opinions/feed',
    OPINIONS_MINE: '/opinions/mine',
    OPINION_LIKE: (id) => `/opinions/${id}/like`,
  },
}))

import PublicOpinionHall from './PublicOpinionHall.vue'

const flushView = async () => {
  await Promise.resolve()
  await nextTick()
  await Promise.resolve()
  await nextTick()
}

describe('PublicOpinionHall feedback pagination', () => {
  beforeEach(() => {
    vi.stubGlobal('IntersectionObserver', class {
      observe() {}
      disconnect() {}
    })
    vi.stubGlobal('requestAnimationFrame', vi.fn(() => 1))
    vi.stubGlobal('cancelAnimationFrame', vi.fn())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    pushMock.mockReset()
  })

  it('paginates feedback with 10 list items and 15 grid items per page', async () => {
    const wrapper = mount(PublicOpinionHall, {
      global: {
        stubs: {
          PolicyTitle: {
            template: '<div class="policy-title-stub">{{ title }}</div>',
            props: ['title'],
          },
          LearnMoreLink: {
            template: '<button class="learn-more-stub" @click="$emit(\'click\')">查看全部</button>',
          },
          AgentLoader: {
            template: '<div class="agent-loader-stub"></div>',
          },
        },
      },
    })

    await flushView()

    expect(wrapper.findAll('.feed-section .opinion-card')).toHaveLength(10)
    expect(wrapper.find('.feedback-pager').text()).toContain('1 / 2')

    await wrapper.find('.mode-btn:nth-of-type(2)').trigger('click')
    await flushView()

    expect(wrapper.findAll('.feed-section .opinion-card')).toHaveLength(15)
    expect(wrapper.find('.feedback-pager').text()).toContain('1 / 2')

    await wrapper.find('.feedback-next').trigger('click')
    await flushView()

    expect(wrapper.findAll('.feed-section .opinion-card')).toHaveLength(3)
    expect(wrapper.find('.feedback-pager').text()).toContain('2 / 2')

    wrapper.unmount()
  })
})
