import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

const currentDir = dirname(fileURLToPath(import.meta.url))
const uiSystemCss = readFileSync(resolve(currentDir, '../../assets/ui-system.css'), 'utf8')
const loginFormVue = readFileSync(resolve(currentDir, './LoginForm.vue'), 'utf8')
const registerFormVue = readFileSync(resolve(currentDir, './RegisterForm.vue'), 'utf8')
const forgotPasswordFormVue = readFileSync(resolve(currentDir, './ForgotPasswordForm.vue'), 'utf8')

describe('auth input styles', () => {
  it('keeps auth-page fields transparent and removes browser native dark blocks', () => {
    expect(loginFormVue).toContain('background: transparent !important;')
    expect(registerFormVue).toContain('background: transparent !important;')
    expect(forgotPasswordFormVue).toContain('background: transparent !important;')
    expect(loginFormVue).toContain('.input:-webkit-autofill')
    expect(registerFormVue).toContain('.input:-webkit-autofill')
    expect(forgotPasswordFormVue).toContain('.input:-webkit-autofill')
    expect(loginFormVue).toContain('data-darkreader-inline-bg')
    expect(registerFormVue).toContain('data-darkreader-inline-bg')
    expect(forgotPasswordFormVue).toContain('data-darkreader-inline-bg')
    expect(loginFormVue).toContain('data-darkreader-inline-bgcolor')
    expect(registerFormVue).toContain('data-darkreader-inline-bgcolor')
    expect(forgotPasswordFormVue).toContain('data-darkreader-inline-bgcolor')
    expect(loginFormVue).toContain('data-darkreader-inline-color')
    expect(registerFormVue).toContain('data-darkreader-inline-color')
    expect(forgotPasswordFormVue).toContain('data-darkreader-inline-color')
    expect(loginFormVue).toContain('--darkreader-inline-bg: transparent;')
    expect(registerFormVue).toContain('--darkreader-inline-bg: transparent;')
    expect(forgotPasswordFormVue).toContain('--darkreader-inline-bg: transparent;')
    expect(loginFormVue).toContain('--darkreader-inline-bgcolor: transparent;')
    expect(registerFormVue).toContain('--darkreader-inline-bgcolor: transparent;')
    expect(forgotPasswordFormVue).toContain('--darkreader-inline-bgcolor: transparent;')
    expect(uiSystemCss).toContain("[data-theme='dark'] .auth-page .inputForm")
    expect(uiSystemCss).toContain("background: transparent !important;")
    expect(uiSystemCss).toContain("[data-theme='dark'] .auth-page :where(input, textarea, select)")
    expect(uiSystemCss).toContain('.auth-page input::-ms-reveal')
    expect(uiSystemCss).toContain('.auth-page input::-ms-clear')
    expect(uiSystemCss).toContain('.auth-page input::-webkit-credentials-auto-fill-button')
  })

  it('uses the same serif brand font for login and register titles', () => {
    expect(loginFormVue).toMatch(/\.logo-text\s*\{[\s\S]*font-family: "STKaiti", "KaiTi", "Noto Serif SC", "Source Han Serif SC", serif;/)
    expect(registerFormVue).toMatch(/\.logo-text\s*\{[\s\S]*font-family: "STKaiti", "KaiTi", "Noto Serif SC", "Source Han Serif SC", serif;/)
  })
})
