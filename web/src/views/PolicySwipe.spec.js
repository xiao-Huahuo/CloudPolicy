import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { afterEach, describe, expect, it, vi } from 'vitest'

const routeState = {
  query: {},
}

const replaceMock = vi.fn()
const pushMock = vi.fn()

vi.mock('vue-router', () => ({
  useRoute: () => routeState,
  useRouter: () => ({
    replace: replaceMock,
    push: pushMock,
  }),
}))

const recommendedDocs = Array.from({ length: 3 }, (_, index) => ({
  id: index + 1,
  title: `推荐政策 ${index + 1}`,
  content: `推荐政策正文 ${index + 1}`,
  category: '政策',
  created_time: '2026-04-29T00:00:00Z',
  uploader_name: '认证主体',
  view_count: 10 + index,
  like_count: 2 + index,
  tags: '民生,补贴',
}))

const centralDocsItems = Array.from({ length: 2 }, (_, index) => ({
  title: `中央文件 ${index + 1}`,
  description: `中央文件摘要 ${index + 1}`,
  pubDate: '2026-04-29',
  link: `https://example.com/central-${index + 1}`,
}))

const hotNewsItems = Array.from({ length: 2 }, (_, index) => ({
  title: `热点新闻 ${index + 1}`,
  description: `热点摘要 ${index + 1}`,
  pubDate: '2026-04-29',
  link: `https://example.com/news-${index + 1}`,
}))

const opinionsByDocItems = [
  {
    id: 1,
    doc_id: 1,
    user_name: '群众代表',
    opinion_type: 'review',
    content: '希望这条政策能把办理材料和咨询电话放在同一个入口，方便后续跟进。',
    rating: 4,
    like_count: 6,
    created_time: '2026-04-29T09:00:00Z',
  },
]

vi.mock('@/api/history', () => ({
  trackHistoryEvent: vi.fn(() => Promise.resolve()),
}))

vi.mock('@/stores/auth.js', () => ({
  useUserStore: () => ({
    token: '',
  }),
}))

vi.mock('@/api/news', () => ({
  getCentralDocs: vi.fn(async () => ({ data: { items: centralDocsItems } })),
  getHotNews: vi.fn(async () => ({ data: { items: hotNewsItems } })),
}))

vi.mock('@/router/api_routes', () => ({
  apiClient: {
    get: vi.fn(async (url) => {
      if (String(url).startsWith('/opinions/doc/')) return { data: opinionsByDocItems }
      return { data: recommendedDocs }
    }),
    post: vi.fn(async () => ({ data: { view_count: 99, like_count: 9 } })),
  },
  API_ROUTES: {
    POLICY_DOC_RECOMMEND: '/policy-doc/recommend',
    POLICY_DOC_RECOMMEND_ME: '/policy-doc/recommend-me',
    POLICY_DOC_VIEW: (id) => `/policy-doc/${id}/view`,
    POLICY_DOC_LIKE: (id) => `/policy-doc/${id}/like`,
    POLICY_DOC_DETAIL: (id) => `/policy-doc/${id}`,
    OPINIONS_BY_DOC: (id) => `/opinions/doc/${id}`,
  },
}))

import PolicySwipe from './PolicySwipe.vue'

const flushView = async () => {
  await Promise.resolve()
  await nextTick()
  await Promise.resolve()
  await nextTick()
}

describe('PolicySwipe layout', () => {
  afterEach(() => {
    routeState.query = {}
    replaceMock.mockReset()
    pushMock.mockReset()
    window.localStorage.clear()
  })

  it('keeps the overview column visible and opens the selected policy in a middle reading pane', async () => {
    const wrapper = mount(PolicySwipe, {
      global: {
        stubs: {
          PolicyTitle: {
            template: '<div class="policy-title-stub">{{ title }}</div>',
            props: ['title'],
          },
          UnifiedSearchBox: {
            template: '<div class="search-box-stub"></div>',
          },
          AgentLoader: {
            template: '<div class="agent-loader-stub"></div>',
          },
        },
      },
    })

    await flushView()

    expect(wrapper.find('.middle-section').exists()).toBe(true)
    expect(wrapper.findAll('.overview-item').length).toBe(recommendedDocs.length)

    await wrapper.findAll('.overview-item')[0].trigger('click')
    await flushView()

    expect(wrapper.findAll('.overview-item').length).toBe(recommendedDocs.length)
    expect(wrapper.find('.reader-panel').text()).toContain('推荐政策 1')
    expect(wrapper.find('.reader-panel').text()).toContain('推荐政策正文 1')

    wrapper.unmount()
  })

  it('renders readable chinese labels in the policy reading page', async () => {
    const wrapper = mount(PolicySwipe, {
      global: {
        stubs: {
          PolicyTitle: {
            template: '<div class="policy-title-stub">{{ title }}</div>',
            props: ['title'],
          },
          UnifiedSearchBox: {
            template: '<div class="search-box-stub"></div>',
          },
          AgentLoader: {
            template: '<div class="agent-loader-stub"></div>',
          },
        },
      },
    })

    await flushView()

    expect(wrapper.find('.policy-title-stub').text()).toBe('政策推荐阅读')
    expect(wrapper.find('.swipe-desc').text()).toContain('根据您的职业和浏览偏好')
    expect(wrapper.find('.overview-title').text()).toBe('政策概览')
    expect(wrapper.find('.panel-title').text()).toBe('中央文件')
    expect(wrapper.find('.right-panel-switch').text()).toContain('时事热点')

    wrapper.unmount()
  })

  it('keeps likes responsive and shows a favorite toggle beside the like action', async () => {
    const wrapper = mount(PolicySwipe, {
      global: {
        stubs: {
          PolicyTitle: {
            template: '<div class="policy-title-stub">{{ title }}</div>',
            props: ['title'],
          },
          UnifiedSearchBox: {
            template: '<div class="search-box-stub"></div>',
          },
          AgentLoader: {
            template: '<div class="agent-loader-stub"></div>',
          },
        },
      },
    })

    await flushView()
    await wrapper.findAll('.overview-item')[0].trigger('click')
    await flushView()

    expect(wrapper.find('.rp-like').text()).toContain('2')

    await wrapper.find('.rp-like').trigger('click')
    await flushView()

    expect(wrapper.find('.rp-like').text()).toContain('9')
    expect(wrapper.findAll('.overview-item')[0].text()).toContain('9')

    const favoriteButton = wrapper.find('.rp-favorite')
    expect(favoriteButton.exists()).toBe(true)

    await favoriteButton.trigger('click')
    await flushView()
    expect(wrapper.find('.rp-favorite').classes()).toContain('active')
    expect(wrapper.find('.rp-favorite').text()).toContain('已收藏')

    await wrapper.find('.rp-favorite').trigger('click')
    await flushView()
    expect(wrapper.find('.rp-favorite').classes()).not.toContain('active')
    expect(wrapper.find('.rp-favorite').text()).toContain('收藏')

    wrapper.unmount()
  })

  it('shows a feedback source area under each opened policy with an audit notice', async () => {
    const wrapper = mount(PolicySwipe, {
      global: {
        stubs: {
          PolicyTitle: {
            template: '<div class="policy-title-stub">{{ title }}</div>',
            props: ['title'],
          },
          UnifiedSearchBox: {
            template: '<div class="search-box-stub"></div>',
          },
          AgentLoader: {
            template: '<div class="agent-loader-stub"></div>',
          },
        },
      },
    })

    await flushView()
    await wrapper.findAll('.overview-item')[0].trigger('click')
    await flushView()

    expect(wrapper.find('.policy-feedback-source').exists()).toBe(true)
    expect(wrapper.find('.policy-feedback-source').text()).toContain('民生反馈来源')
    expect(wrapper.find('.policy-comments').text()).toContain('评论区')
    expect(wrapper.find('.policy-comments').text()).toContain('办理材料和咨询电话')
    expect(wrapper.find('.policy-opinion-form').text()).toContain('发表意见')
    expect(wrapper.find('.policy-audit-note').text()).toContain('审核机制')

    wrapper.unmount()
  })
})
