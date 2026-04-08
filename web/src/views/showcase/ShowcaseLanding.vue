<template>
  <div class="landing">
    <ShowcaseHeader />

    <!-- Hero -->
    <section class="hero">
      <div class="hero-bg"></div>
      <div class="hero-content" ref="heroRef" :class="{ visible: visibleSections.hero }">
        <div class="hero-badge">智能政策分析平台</div>
        <h1 class="hero-title">云上观策</h1>
        <p class="hero-sub">汇聚政策资讯 · 智能解析分析 · 民意实时反馈</p>
        <div class="hero-btns">
          <button class="btn-primary" @click="$router.push('/')">立即体验</button>
          <button class="btn-ghost" @click="$router.push('/showcase/discovery')">浏览政策广场</button>
        </div>
        <div class="hero-stats">
          <div class="hs" v-for="s in heroStats" :key="s.label">
            <span class="hs-num">{{ s.num }}</span>
            <span class="hs-label">{{ s.label }}</span>
          </div>
        </div>
      </div>
      <div class="hero-scroll-hint">
        <div class="scroll-dot"></div>
      </div>
    </section>

    <!-- Features -->
    <section class="features-section" ref="featuresRef">
      <div class="section-inner">
        <div class="section-tag" :class="{ visible: visibleSections.features }">核心功能</div>
        <h2 class="section-title" :class="{ visible: visibleSections.features }">一站式政策智能服务</h2>
        <div class="features-grid">
          <div class="feat-card" v-for="(f, i) in features" :key="i"
            :class="{ visible: visibleSections.features }" :style="{ transitionDelay: i * 80 + 'ms' }"
            ref="featRefs">
            <div class="feat-icon" :style="{ background: f.color + '18', color: f.color }">
              <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" v-html="f.icon"></svg>
            </div>
            <h3 class="feat-title">{{ f.title }}</h3>
            <p class="feat-desc">{{ f.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Flow -->
    <section class="flow-section" ref="flowRef">
      <div class="section-inner">
        <div class="section-tag">使用流程</div>
        <h2 class="section-title">三步开始智能政策分析</h2>
        <div class="flow-steps">
          <div class="flow-step" v-for="(s, i) in flowSteps" :key="i"
            :class="{ visible: visibleSections.flow }" :style="{ transitionDelay: i * 120 + 'ms' }">
            <div class="fs-num">{{ i + 1 }}</div>
            <div class="fs-body">
              <h3>{{ s.title }}</h3>
              <p>{{ s.desc }}</p>
            </div>
            <div v-if="i < flowSteps.length - 1" class="fs-arrow">→</div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta-section" ref="ctaRef" :class="{ visible: visibleSections.cta }">
      <h2>立即加入云上观策</h2>
      <p>免费注册，即刻体验智能政策分析服务</p>
      <button class="btn-primary large" @click="$router.push('/register')">免费注册</button>
    </section>

    <!-- Footer -->
    <footer class="sc-footer">
      <div class="footer-inner">
        <div class="footer-brand">云上观策</div>
        <div class="footer-links">
          <router-link to="/showcase">首页</router-link>
          <router-link to="/showcase/discovery">政策广场</router-link>
          <router-link to="/showcase/screen">数据大屏</router-link>
          <router-link to="/">进入系统</router-link>
        </div>
        <div class="footer-copy">© 2026 云上观策. All rights reserved.</div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import ShowcaseHeader from '@/components/showcase/ShowcaseHeader.vue'

const heroStats = [
  { num: '10,000+', label: '政策文件' },
  { num: '500+', label: '认证主体' },
  { num: '50,000+', label: '注册用户' },
  { num: '99.9%', label: '服务可用率' },
]

const features = [
  { title: '智能解析', desc: 'AI驱动的政策文件自动解析，提取关键信息，节省阅读时间', color: '#c0392b', icon: '<rect x="3" y="3" width="18" height="14" rx="2"/><path d="M7 21h10"/>' },
  { title: '全景政策广场', desc: '汇聚各方认证主体上传的最新政务文件，实时更新', color: '#2980b9', icon: '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>' },
  { title: '民意评议大厅', desc: '真实透明的社会反馈信息流，让政策落地有据可查', color: '#27ae60', icon: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>' },
  { title: '数据可视化', desc: '多维度数据图表，直观呈现政策触达效果与用户反馈', color: '#8e44ad', icon: '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>' },
  { title: 'ClearFlow智能体', desc: '专属AI助手，随时解答政策疑问，辅助办事流程', color: '#e67e22', icon: '<path d="M12 2a10 10 0 1 0 10 10"/><path d="M12 8v4l3 3"/>' },
  { title: '认证主体服务', desc: '为政府机构提供专属发布渠道和数据追踪分析服务', color: '#16a085', icon: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>' },
]

const flowSteps = [
  { title: '注册账号', desc: '免费注册，邮箱验证即可使用' },
  { title: '浏览政策', desc: '在政策广场发现最新政务文件' },
  { title: '智能分析', desc: 'AI自动解析，获取关键摘要' },
]

const visibleSections = reactive({ hero: false, features: false, flow: false, cta: false })
const heroRef = ref(null)
const featuresRef = ref(null)
const flowRef = ref(null)
const ctaRef = ref(null)

let observer
onMounted(() => {
  observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        if (e.target === heroRef.value) visibleSections.hero = true
        if (e.target === featuresRef.value) visibleSections.features = true
        if (e.target === flowRef.value) visibleSections.flow = true
        if (e.target === ctaRef.value) visibleSections.cta = true
      }
    })
  }, { threshold: 0.1 })
  if (heroRef.value) observer.observe(heroRef.value)
  if (featuresRef.value) observer.observe(featuresRef.value)
  if (flowRef.value) observer.observe(flowRef.value)
  if (ctaRef.value) observer.observe(ctaRef.value)
})
onUnmounted(() => observer?.disconnect())
</script>

<style scoped>
.landing { min-height: 100vh; background: var(--content-bg, #f4f5f7); }

/* Hero */
.hero { position: relative; min-height: 100vh; display: flex; align-items: center; justify-content: center; overflow: hidden; }
.hero-bg {
  position: absolute; inset: 0;
  background: linear-gradient(135deg, #1a0a09 0%, #c0392b 40%, #2980b9 100%);
}
.hero-bg::after {
  content: ''; position: absolute; inset: 0;
  background: radial-gradient(ellipse at 60% 40%, rgba(255,255,255,0.08) 0%, transparent 60%);
}
.hero-content {
  position: relative; text-align: center; color: #fff; padding: 80px 20px 40px; max-width: 800px;
  opacity: 0; transform: translateY(40px);
  transition: opacity 0.8s ease, transform 0.8s ease;
}
.hero-content.visible { opacity: 1; transform: translateY(0); }
.hero-badge { display: inline-block; background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.3); padding: 6px 18px; border-radius: 20px; font-size: 13px; margin-bottom: 24px; backdrop-filter: blur(8px); }
.hero-title { font-size: clamp(48px, 8vw, 88px); font-weight: 900; margin: 0 0 16px; letter-spacing: -2px; text-shadow: 0 4px 24px rgba(0,0,0,0.3); }
.hero-sub { font-size: 18px; color: rgba(255,255,255,0.8); margin: 0 0 36px; line-height: 1.6; }
.hero-btns { display: flex; gap: 12px; justify-content: center; margin-bottom: 48px; flex-wrap: wrap; }
.btn-primary { background: #fff; color: #c0392b; border: none; padding: 14px 32px; border-radius: 30px; font-size: 15px; font-weight: 700; cursor: pointer; transition: all 0.25s; }
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.2); }
.btn-primary.large { padding: 16px 48px; font-size: 16px; }
.btn-ghost { background: rgba(255,255,255,0.12); color: #fff; border: 1px solid rgba(255,255,255,0.4); padding: 14px 32px; border-radius: 30px; font-size: 15px; cursor: pointer; transition: all 0.25s; backdrop-filter: blur(8px); }
.btn-ghost:hover { background: rgba(255,255,255,0.22); }
.hero-stats { display: flex; gap: 40px; justify-content: center; flex-wrap: wrap; }
.hs { display: flex; flex-direction: column; gap: 4px; }
.hs-num { font-size: 28px; font-weight: 900; }
.hs-label { font-size: 12px; color: rgba(255,255,255,0.65); }
.hero-scroll-hint { position: absolute; bottom: 32px; left: 50%; transform: translateX(-50%); }
.scroll-dot { width: 6px; height: 6px; background: rgba(255,255,255,0.6); border-radius: 50%; animation: bounce 1.6s ease-in-out infinite; }
@keyframes bounce { 0%,100% { transform: translateY(0); opacity: 1; } 50% { transform: translateY(10px); opacity: 0.4; } }

/* Sections */
.section-inner { max-width: 1100px; margin: 0 auto; padding: 80px 24px; }
.section-tag { display: inline-block; background: rgba(192,57,43,0.1); color: #c0392b; padding: 4px 14px; border-radius: 12px; font-size: 12px; font-weight: 700; margin-bottom: 12px; opacity: 0; transform: translateY(16px); transition: opacity 0.5s ease, transform 0.5s ease; }
.section-tag.visible { opacity: 1; transform: translateY(0); }
.section-title { font-size: 32px; font-weight: 800; margin: 0 0 40px; color: var(--text-primary, #111); opacity: 0; transform: translateY(16px); transition: opacity 0.5s ease 0.1s, transform 0.5s ease 0.1s; }
.section-title.visible { opacity: 1; transform: translateY(0); }

/* Features */
.features-section { background: var(--card-bg, #fff); }
.features-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.feat-card {
  padding: 28px; border: 1px solid var(--border-color, #eee);
  opacity: 0; transform: translateY(24px);
  transition: opacity 0.5s ease, transform 0.5s ease, box-shadow 0.25s;
}
.feat-card.visible { opacity: 1; transform: translateY(0); }
.feat-card:hover { box-shadow: 0 8px 28px rgba(0,0,0,0.08); transform: translateY(-4px); }
.feat-icon { width: 48px; height: 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center; margin-bottom: 16px; }
.feat-title { font-size: 16px; font-weight: 700; margin: 0 0 8px; color: var(--text-primary, #111); }
.feat-desc { font-size: 13px; color: var(--text-secondary, #666); line-height: 1.6; margin: 0; }

/* Flow */
.flow-section { background: var(--content-bg, #f4f5f7); }
.flow-steps { display: flex; align-items: center; gap: 0; flex-wrap: wrap; }
.flow-step {
  display: flex; align-items: center; gap: 16px; flex: 1; min-width: 200px;
  opacity: 0; transform: translateX(-20px);
  transition: opacity 0.5s ease, transform 0.5s ease;
}
.flow-step.visible { opacity: 1; transform: translateX(0); }
.fs-num { width: 48px; height: 48px; border-radius: 50%; background: #c0392b; color: #fff; font-size: 20px; font-weight: 900; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.fs-body h3 { font-size: 15px; font-weight: 700; margin: 0 0 4px; color: var(--text-primary, #111); }
.fs-body p { font-size: 13px; color: var(--text-secondary, #666); margin: 0; }
.fs-arrow { font-size: 24px; color: #ccc; padding: 0 16px; flex-shrink: 0; }

/* CTA */
.cta-section {
  background: linear-gradient(135deg, #c0392b, #2980b9);
  text-align: center; padding: 80px 24px; color: #fff;
  opacity: 0; transform: translateY(30px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}
.cta-section.visible { opacity: 1; transform: translateY(0); }
.cta-section h2 { font-size: 36px; font-weight: 900; margin: 0 0 12px; }
.cta-section p { font-size: 16px; color: rgba(255,255,255,0.8); margin: 0 0 32px; }
.cta-section .btn-primary { background: #fff; color: #c0392b; }

/* Footer */
.sc-footer { background: #111; color: rgba(255,255,255,0.6); padding: 40px 24px; }
.footer-inner { max-width: 1100px; margin: 0 auto; display: flex; align-items: center; gap: 32px; flex-wrap: wrap; }
.footer-brand { font-size: 18px; font-weight: 800; color: #fff; flex: 1; }
.footer-links { display: flex; gap: 20px; }
.footer-links a { color: rgba(255,255,255,0.6); text-decoration: none; font-size: 13px; transition: color 0.2s; }
.footer-links a:hover { color: #fff; }
.footer-copy { font-size: 12px; }
</style>
