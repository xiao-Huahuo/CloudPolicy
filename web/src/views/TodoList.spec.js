import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { describe, expect, it, vi, beforeEach } from 'vitest'

const { apiClient } = vi.hoisted(() => ({
  apiClient: {
    get: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
    post: vi.fn(),
  },
}))

vi.mock('@/router/api_routes.js', () => ({
  apiClient,
  API_ROUTES: {
    TODO: '/todo/',
  },
}))

import TodoList from './TodoList.vue'

const flushView = async () => {
  await Promise.resolve()
  await nextTick()
  await Promise.resolve()
  await nextTick()
}

const baseTodo = {
  id: 1,
  title: '办理备案',
  detail: '补充材料',
  deadline: '2026-05-01',
  is_done: false,
  is_confirmed: true,
}

const doneTodo = {
  ...baseTodo,
  id: 2,
  title: '归档已完成材料',
  is_done: true,
}

describe('TodoList', () => {
  beforeEach(() => {
    apiClient.get.mockReset()
    apiClient.patch.mockReset()
    apiClient.delete.mockReset()
    apiClient.post.mockReset()
  })

  it('keeps the todo text after toggling even if the toggle response is partial', async () => {
    apiClient.get
      .mockResolvedValueOnce({ data: [baseTodo] })
      .mockResolvedValueOnce({ data: [baseTodo] })
    apiClient.patch.mockResolvedValueOnce({ data: { id: 1, is_done: true } })
    apiClient.delete.mockResolvedValueOnce({ data: { ok: true } })

    const wrapper = mount(TodoList, {
      global: {
        stubs: {
          PolicyTitle: {
            template: '<div class="policy-title-stub">{{ title }}</div>',
            props: ['title'],
          },
          AgentLoader: {
            template: '<div class="agent-loader-stub"></div>',
          },
        },
      },
    })

    await flushView()

    expect(wrapper.find('.todo-title').text()).toContain('办理备案')
    await wrapper.find('.completed-toggle input').setValue(true)
    await flushView()

    await wrapper.find('.todo-check').trigger('click')
    await flushView()

    expect(wrapper.find('.todo-title').text()).toContain('办理备案')

    await wrapper.find('.todo-del').trigger('click')
    await flushView()

    expect(apiClient.delete).toHaveBeenCalledWith('/todo/1')
    expect(wrapper.findAll('.todo-item')).toHaveLength(0)

    wrapper.unmount()
  })

  it('toggles a todo when clicking the todo body content', async () => {
    apiClient.get
      .mockResolvedValueOnce({ data: [baseTodo] })
      .mockResolvedValueOnce({ data: [baseTodo] })
    apiClient.patch.mockResolvedValueOnce({
      data: {
        ...baseTodo,
        is_done: true,
      },
    })

    const wrapper = mount(TodoList, {
      global: {
        stubs: {
          PolicyTitle: {
            template: '<div class="policy-title-stub">{{ title }}</div>',
            props: ['title'],
          },
          AgentLoader: {
            template: '<div class="agent-loader-stub"></div>',
          },
        },
      },
    })

    await flushView()

    expect(wrapper.find('.todo-item').classes()).not.toContain('done')
    await wrapper.find('.completed-toggle input').setValue(true)
    await flushView()

    await wrapper.find('.todo-body').trigger('click')
    await flushView()

    expect(apiClient.patch).toHaveBeenCalledWith('/todo/1/toggle')
    expect(wrapper.find('.todo-item').classes()).toContain('done')

    wrapper.unmount()
  })

  it('refreshes the pending list after toggling a todo to done', async () => {
    apiClient.get
      .mockResolvedValueOnce({ data: [baseTodo] })
      .mockResolvedValueOnce({ data: [baseTodo] })
    apiClient.patch.mockResolvedValueOnce({
      data: {
        id: 1,
        is_done: true,
      },
    })

    const wrapper = mount(TodoList, {
      global: {
        stubs: {
          PolicyTitle: {
            template: '<div class="policy-title-stub">{{ title }}</div>',
            props: ['title'],
          },
          AgentLoader: {
            template: '<div class="agent-loader-stub"></div>',
          },
        },
      },
    })

    await flushView()

    await wrapper.findAll('.todo-filters button')[1].trigger('click')
    await nextTick()
    expect(wrapper.findAll('.todo-item')).toHaveLength(1)

    await wrapper.find('.todo-body').trigger('click')
    await flushView()

    expect(wrapper.findAll('.todo-item')).toHaveLength(0)
    expect(wrapper.find('.todo-empty').text()).toContain('暂无待办事项')

    wrapper.unmount()
  })

  it('uses a date picker for the deadline field when creating a todo', async () => {
    apiClient.get
      .mockResolvedValueOnce({ data: [] })
      .mockResolvedValueOnce({ data: [] })

    const wrapper = mount(TodoList, {
      global: {
        stubs: {
          PolicyTitle: {
            template: '<div class="policy-title-stub">{{ title }}</div>',
            props: ['title'],
          },
          AgentLoader: {
            template: '<div class="agent-loader-stub"></div>',
          },
        },
      },
    })

    await flushView()

    await wrapper.find('.add-btn').trigger('click')
    await nextTick()

    expect(wrapper.find('input[type="date"]').exists()).toBe(true)

    wrapper.unmount()
  })

  it('renders readable chinese labels for the todo page actions', async () => {
    apiClient.get
      .mockResolvedValueOnce({ data: [] })
      .mockResolvedValueOnce({ data: [] })

    const wrapper = mount(TodoList, {
      global: {
        stubs: {
          PolicyTitle: {
            template: '<div class="policy-title-stub">{{ title }}</div>',
            props: ['title'],
          },
          AgentLoader: {
            template: '<div class="agent-loader-stub"></div>',
          },
        },
      },
    })

    await flushView()

    expect(wrapper.find('.policy-title-stub').text()).toBe('办事进度中心')
    expect(wrapper.find('.add-btn').text()).toContain('新建待办')
    expect(wrapper.find('.todo-filters').text()).toContain('全部')
    expect(wrapper.find('.todo-filters').text()).toContain('待完成')
    expect(wrapper.find('.todo-filters').text()).toContain('已完成')

    wrapper.unmount()
  })

  it('hides completed todos by default and reveals them with the completed switch', async () => {
    apiClient.get
      .mockResolvedValueOnce({ data: [baseTodo, doneTodo] })
      .mockResolvedValueOnce({ data: [baseTodo, doneTodo] })

    const wrapper = mount(TodoList, {
      global: {
        stubs: {
          PolicyTitle: {
            template: '<div class="policy-title-stub">{{ title }}</div>',
            props: ['title'],
          },
          AgentLoader: {
            template: '<div class="agent-loader-stub"></div>',
          },
        },
      },
    })

    await flushView()

    expect(wrapper.find('.completed-toggle').exists()).toBe(true)
    expect(wrapper.findAll('.todo-item')).toHaveLength(1)
    expect(wrapper.text()).not.toContain('归档已完成材料')

    await wrapper.find('.completed-toggle input').setValue(true)
    await flushView()

    expect(wrapper.findAll('.todo-item')).toHaveLength(2)
    expect(wrapper.text()).toContain('归档已完成材料')

    wrapper.unmount()
  })

  it('keeps the typed title when creating a todo even if the create response is partial', async () => {
    apiClient.get
      .mockResolvedValueOnce({ data: [] })
      .mockResolvedValueOnce({ data: [] })
    apiClient.post.mockResolvedValueOnce({
      data: {
        id: 2,
        is_done: false,
        is_confirmed: true,
      },
    })

    const wrapper = mount(TodoList, {
      global: {
        stubs: {
          PolicyTitle: {
            template: '<div class="policy-title-stub">{{ title }}</div>',
            props: ['title'],
          },
          AgentLoader: {
            template: '<div class="agent-loader-stub"></div>',
          },
        },
      },
    })

    await flushView()

    await wrapper.find('.add-btn').trigger('click')
    await nextTick()

    await wrapper.findAll('.modal-input')[0].setValue('  跟进申报材料  ')
    await wrapper.find('input[type="date"]').setValue('2026-05-03')
    await wrapper.find('.modal-textarea').setValue('联系窗口确认缺失附件')
    await wrapper.find('.confirm-btn').trigger('click')
    await flushView()

    expect(wrapper.findAll('.todo-item')).toHaveLength(1)
    expect(wrapper.find('.todo-title').text()).toBe('跟进申报材料')
    expect(wrapper.find('.todo-deadline').text()).toContain('2026-05-03')
    expect(wrapper.find('.todo-detail').text()).toContain('联系窗口确认缺失附件')

    wrapper.unmount()
  })
})
