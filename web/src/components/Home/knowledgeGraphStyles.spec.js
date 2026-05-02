import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

const currentDir = dirname(fileURLToPath(import.meta.url))
const uiSystemCss = readFileSync(resolve(currentDir, '../../assets/ui-system.css'), 'utf8')

describe('knowledge graph theme styles', () => {
  it('tints the home knowledge graph frame in dark mode instead of using the default light frame', () => {
    expect(uiSystemCss).toMatch(/\[data-theme='dark'\] \.kg-panel\s*\{[\s\S]*--kg-panel-border: color-mix\(in srgb, var\(--color-primary\) 28%, var\(--border-color\)\);/)
    expect(uiSystemCss).toMatch(/\[data-theme='dark'\] \.kg-panel\s*\{[\s\S]*--kg-card-surface:/)
    expect(uiSystemCss).toMatch(/\[data-theme='dark'\] \.kg-panel\s*\{[\s\S]*--kg-graph-surface:/)
    expect(uiSystemCss).toMatch(/\[data-theme='dark'\] \.kg-panel\s*\{[\s\S]*--kg-soft-border: color-mix\(in srgb, var\(--color-secondary\) 18%, var\(--border-color\)\);/)
  })
})
