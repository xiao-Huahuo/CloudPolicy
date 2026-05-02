import { describe, expect, it } from 'vitest'
import SidebarSource from './Sidebar.vue?raw'

describe('Sidebar brand typography', () => {
  it('uses a dedicated brand font stack for the cloud policy title', () => {
    expect(SidebarSource).toContain('<span class="logo-text">云枢观策</span>')
    expect(SidebarSource).toMatch(/\.logo-text\s*\{[\s\S]*font-family:/)
  })
})
