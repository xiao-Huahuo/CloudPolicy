import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

const currentDir = dirname(fileURLToPath(import.meta.url))
const homeVue = readFileSync(resolve(currentDir, './Home.vue'), 'utf8')

describe('Home result view theme styles', () => {
  it('uses theme variables for the result title and top actions', () => {
    expect(homeVue).toMatch(/\.back-btn\s*\{[\s\S]*background: color-mix\(in srgb, var\(--color-primary\) 4%, var\(--card-bg\)\);[\s\S]*color: var\(--text-primary\);/)
    expect(homeVue).toMatch(/\.result-header-btn\s*\{[\s\S]*background: color-mix\(in srgb, var\(--color-primary\) 4%, var\(--card-bg\)\);[\s\S]*color: var\(--text-primary\);/)
    expect(homeVue).toMatch(/\.result-header h2\s*\{[\s\S]*color: var\(--text-primary\);/)
    expect(homeVue).toMatch(/\.result-title\s*\{[\s\S]*color: var\(--text-primary\);/)
    expect(homeVue).toMatch(/\.response-section\s*\{[\s\S]*background: var\(--card-bg\);/)
    expect(homeVue).toMatch(/\.result-action-btn\s*\{[\s\S]*background: color-mix\(in srgb, var\(--color-primary\) 5%, var\(--card-bg\)\);[\s\S]*color: var\(--text-secondary\);/)
    expect(homeVue).toContain(":stroke=\"isFavorited ? 'var(--color-primary)' : 'currentColor'\"")
    expect(homeVue).toContain(":fill=\"isFavorited ? 'var(--color-primary)' : 'none'\"")
  })
})
