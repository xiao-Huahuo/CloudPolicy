import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const routeState = {
  name: 'agent',
  query: {},
}

const backMock = vi.fn()
const pushMock = vi.fn()
const logoutMock = vi.fn()
const updateSettingsMock = vi.fn()
const setColorSchemeMock = vi.fn()
const applyThemeMock = vi.fn()
const getNextColorSchemeMock = vi.fn(() => 'coral')

const userStore = {
  token: 'token',
  user: {
    avatar_url: '',
  },
  logout: logoutMock,
}

const settingsStore = {
  settings: {
    color_scheme: 'classic',
    system_notifications: true,
    theme_mode: 'light',
  },
  updateSettings: updateSettingsMock,
  setColorScheme: setColorSchemeMock,
  applyTheme: applyThemeMock,
  getNextColorScheme: getNextColorSchemeMock,
}

vi.mock('vue-router', () => ({
  useRoute: () => routeState,
  useRouter: () => ({
    back: backMock,
    push: pushMock,
  }),
}))

vi.mock('@/api/history', () => ({
  trackHistoryEvent: vi.fn(() => Promise.resolve()),
}))

vi.mock('@/stores/auth.js', () => ({
  useUserStore: () => userStore,
}))

vi.mock('@/stores/settings', () => ({
  COLOR_SCHEME_OPTIONS: [
    { value: 'classic', label: '经典红' },
    { value: 'coral', label: '珊瑚蓝' },
  ],
  useSettingsStore: () => settingsStore,
}))

vi.mock('@/composables/useAppearanceTransition', () => ({
  useAppearanceTransition: () => ({
    isAppearanceTransitioning: false,
  }),
}))

vi.mock('@/utils/avatar.js', () => ({
  resolveAvatarUrl: vi.fn(() => ''),
}))

vi.mock('@/utils/unifiedSearch', () => ({
  buildSearchRouteQuery: vi.fn((query, types = []) => ({ q: query, types: types.join(',') })),
  normalizeSearchTypes: vi.fn(() => []),
}))

import Header from './Header.vue'

const flushView = async () => {
  await Promise.resolve()
  await nextTick()
}

describe('Header logout flow', () => {
  beforeEach(() => {
    routeState.name = 'agent'
    routeState.query = {}
    logoutMock.mockReset()
    pushMock.mockReset()
    backMock.mockReset()
    updateSettingsMock.mockReset()
    setColorSchemeMock.mockReset()
    applyThemeMock.mockReset()
    getNextColorSchemeMock.mockClear()
    document.documentElement.setAttribute('data-theme', 'light')
  })

  it('opens a confirm dialog before logging out', async () => {
    const confirmSpy = vi.spyOn(window, 'confirm')

    const wrapper = mount(Header, {
      props: {
        isIconMode: true,
      },
      global: {
        stubs: {
          UnifiedSearchBox: {
            template: '<div class="search-box-stub"></div>',
          },
          LogoutPillButton: {
            emits: ['click'],
            template: '<button class="logout-pill-stub" @click="$emit(\'click\')">退出</button>',
          },
          Modal: {
            props: ['isOpen'],
            template: '<div v-if="isOpen" class="modal-stub"><slot /></div>',
          },
        },
      },
    })

    await wrapper.find('.logout-pill-stub').trigger('click')
    await flushView()

    expect(confirmSpy).not.toHaveBeenCalled()
    expect(wrapper.find('.logout-dialog').exists()).toBe(true)
    expect(logoutMock).not.toHaveBeenCalled()

    await wrapper.find('.logout-dialog__btn--primary').trigger('click')
    await flushView()

    expect(logoutMock).toHaveBeenCalledTimes(1)
    expect(pushMock).toHaveBeenCalledWith('/showcase')

    confirmSpy.mockRestore()
    wrapper.unmount()
  })
})
