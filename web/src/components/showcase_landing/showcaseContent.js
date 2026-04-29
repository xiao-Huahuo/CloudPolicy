import highlightAgentImage from '@/assets/photos/showcase-highlights/云小圆.png'
import highlightScreenImage from '@/assets/photos/showcase-highlights/公共数据大屏.png'
import highlightScanImage from '@/assets/photos/showcase-highlights/可视化知识图谱.png'
import highlightSwipeImage from '@/assets/photos/showcase-highlights/刷剧资讯体验.png'

const sortEntries = (modules) => Object.entries(modules).sort(([a], [b]) => a.localeCompare(b, 'zh-CN'))
const normalizeModuleList = (modules) => sortEntries(modules).map(([, mod]) => mod.default)
const pickImage = (...candidates) => candidates.find(Boolean) || null

const discoverSlides = normalizeModuleList(
  import.meta.glob('/src/assets/photos/discover/slide*.jpg', { eager: true })
)
const discoverNews = normalizeModuleList(
  import.meta.glob('/src/assets/photos/discover/news/*.{jpg,jpeg,png,webp}', { eager: true })
)
const mainExamples = normalizeModuleList(
  import.meta.glob('/src/assets/photos/main-examples/*.{jpg,jpeg,png,webp}', { eager: true })
)
const opinionSlides = normalizeModuleList(
  import.meta.glob('/src/assets/photos/opinion-carousel/*.{jpg,jpeg,png,webp}', { eager: true })
)
const whyUsImages = normalizeModuleList(
  import.meta.glob('/src/assets/photos/landing/why-us/*.{jpg,jpeg,png,webp}', { eager: true })
)
const philosophyImages = normalizeModuleList(
  import.meta.glob('/src/assets/photos/landing/phylosophy/*.{jpg,jpeg,png,webp}', { eager: true })
)
const partnerLogos = sortEntries(
  import.meta.glob('/src/assets/photos/partners/*.{svg,png,jpg,jpeg,webp}', { eager: true })
)

const titleize = (value) =>
  value
    .split(' ')
    .filter(Boolean)
    .map((word) => {
      if (word.length <= 4) {
        return word.toUpperCase()
      }
      return word.charAt(0).toUpperCase() + word.slice(1)
    })
    .join(' ')

const formatPartnerName = (path) => {
  const raw = path
    .split('/')
    .pop()
    ?.replace(/\.[^.]+$/, '')
    .replace(/^material-icon-theme--/i, '')
    .replace(/\s*\(\d+\)\s*/g, '')
    .replace(/[-_]+/g, ' ')
    .trim()

  return raw ? titleize(raw) : 'Partner'
}

export const heroPreviewSignals = [
  { label: '策略图谱', value: '实时同步', accent: '#ff875b' },
  { label: 'Agent 回应', value: '链式分析', accent: '#56d6ff' },
  { label: '群众反馈', value: '秒级聚合', accent: '#7ef0aa' },
]

export const uiSlides = [
  {
    eyebrow: '智能检索',
    title: '从一句话问题直接进入政策原文',
    subtitle: '搜索、摘要、卡片与证据定位同屏联动。',
    description:
      '围绕政策检索、摘要生成和证据定位构建同屏体验，让用户从提问到进入原文只保留一条清晰路径。',
    bullets: ['多模态检索入口', '结构化政策卡片', '摘要与重点高亮'],
    resourceTitle: '检索体验已接入首页展示',
    resourceDesc: '首页轮播使用真实政策资讯、文档示例和检索场景图片，呈现从问题到答案的完整路径。',
    accent: '#ff7a18',
    images: [
      pickImage(discoverSlides[0], discoverNews[0], mainExamples[0]),
      pickImage(mainExamples[0], mainExamples[1], discoverSlides[1]),
      pickImage(mainExamples[6], mainExamples[3], discoverNews[1]),
    ],
  },
  {
    eyebrow: '数据大屏',
    title: '把复杂统计压缩成一眼能读懂的仪表视图',
    subtitle: '数字、图表、趋势与地区分布形成一块整屏叙事面板。',
    description:
      '面向管理端和展示端统一数据语言，让趋势、地区分布和用户反馈在同一组视觉节奏里被快速理解。',
    bullets: ['实时趋势图', '地区与角色分布', '高亮指标级联展示'],
    resourceTitle: '大屏素材用于支撑汇报场景',
    resourceDesc: '轮播图组以政策广场、舆情图表和数据面板图片组合，补足演示时的数据氛围。',
    accent: '#41c6ff',
    images: [
      pickImage(discoverSlides[1], discoverSlides[2], opinionSlides[0]),
      pickImage(discoverSlides[2], opinionSlides[1], discoverSlides[3]),
      pickImage(opinionSlides[0], opinionSlides[1], discoverNews[2]),
    ],
  },
  {
    eyebrow: 'Agent 对话',
    title: '把政策解释能力收拢进一个持续对话界面',
    subtitle: '消息气泡、结构化结论和证据片段一起出现。',
    description:
      '用户在同一个沉浸式空间内完成提问、追问、证据核验和任务推进，减少跨页面来回跳转。',
    bullets: ['多轮上下文理解', '证据链片段回指', '任务结果结构化输出'],
    resourceTitle: '对话场景突出 Agent 闭环',
    resourceDesc: '轮播中的文档、答案和资讯图片共同说明云小圆如何承接复杂政策理解任务。',
    accent: '#86f7a7',
    images: [
      pickImage(mainExamples[7], mainExamples[8], opinionSlides[2]),
      pickImage(mainExamples[8], mainExamples[5], discoverNews[3]),
      pickImage(opinionSlides[2], opinionSlides[3], discoverSlides[4]),
    ],
  },
  {
    eyebrow: '政策广场',
    title: '一边浏览政策，一边阅读原文与群众反馈',
    subtitle: '发现、阅读、理解和评价被折叠成一个连续体验。',
    description:
      '政策广场以图片资讯、专题内容和反馈信息组织成连续阅读体验，让大量内容仍保持首页级秩序。',
    bullets: ['信息流式发现', '阅读视图并排展开', '民意反馈同步浮现'],
    resourceTitle: '政策广场已经填充真实资讯图',
    resourceDesc: '发现页与资讯图组共用同一批图片资源，保证演示首页和内容广场之间视觉一致。',
    accent: '#ffd56a',
    images: [
      pickImage(discoverNews[4], discoverNews[5], discoverSlides[0]),
      pickImage(discoverSlides[3], discoverSlides[4], discoverNews[6]),
      pickImage(opinionSlides[4], discoverNews[7], mainExamples[2]),
    ],
  },
  {
    eyebrow: '个人中心',
    title: '把账号、偏好与系统能力收口到统一控制台',
    subtitle: '设置面板与个性化统计并列出现，既强大也清晰。',
    description:
      '个人中心承接账号安全、历史记录、偏好管理和长期运营，让演示从视觉亮点落回完整产品闭环。',
    bullets: ['偏好与权限管理', '历史记录归档', '跨端风格统一'],
    resourceTitle: '个人中心补足产品闭环',
    resourceDesc: '用示例文档、扫描图片和资讯图片组合展示账号管理后的持续使用场景。',
    accent: '#ff7dc2',
    images: [
      pickImage(mainExamples[9], mainExamples[4], discoverNews[8]),
      pickImage(mainExamples[4], mainExamples[5], opinionSlides[1]),
      pickImage(mainExamples[2], discoverNews[9], discoverSlides[2]),
    ],
  },
]

export const features = [
  {
    title: '智能解析',
    desc: '将政策原文自动拆成适用对象、办理事项、材料清单和风险提醒，直接进入可执行视图。',
    color: '#ff8b64',
    icon: '<rect x="4" y="4" width="16" height="16" rx="3"/><path d="M8 9h8M8 13h8M8 17h5"/>',
  },
  {
    title: '全景政策广场',
    desc: '聚合已审核政策文件与动态专题，让发现新政策不再依赖低效搜索。',
    color: '#61c8ff',
    icon: '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.4-3.4"/>',
  },
  {
    title: '民生大厅',
    desc: '把群众意见和评分可视化展示出来，让政策理解与真实反馈同屏发生。',
    color: '#87f0a6',
    icon: '<path d="M4 5h16v10H7l-3 3V5z"/><path d="M8 9h8M8 13h5"/>',
  },
  {
    title: '数据可视化',
    desc: '从宏观指标到微观分布都能被直观读取，适合大屏展示、运营复盘和对外演示。',
    color: '#9eb7ff',
    icon: '<path d="M6 18V10"/><path d="M12 18V6"/><path d="M18 18v-4"/>',
  },
  {
    title: '云小圆',
    desc: '你的专属 AI Agent，围绕政策咨询、流程答疑和任务推进持续提供帮助。',
    color: '#ffc46a',
    icon: '<path d="M12 3a8 8 0 1 0 8 8"/><path d="M12 8v4l3 3"/><circle cx="18.5" cy="5.5" r="1.5"/>',
  },
  {
    title: '认证主体服务',
    desc: '面向机构提供发布、审核、数据追踪和用户触达分析，形成完整政务协作闭环。',
    color: '#ff93be',
    icon: '<path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6l7-3z"/><path d="M9 12l2 2 4-4"/>',
  },
]

export const advantageCards = [
  {
    title: '政策理解速度更快',
    desc: '从原文到摘要、卡片和执行建议被压缩在同一界面里，减少往返跳转和重复阅读。',
    image: whyUsImages[0] || null,
  },
  {
    title: '品牌化展示更完整',
    desc: '产品不再只是业务后台，而是具备公开展示、招商演示和业务传播的企业级首页气质。',
    image: whyUsImages[1] || null,
  },
  {
    title: '反馈链路更真实',
    desc: '政策发布、用户阅读、意见互动和 Agent 分析形成闭环，真正反映信息传播后的真实触达。',
    image: whyUsImages[2] || null,
  },
]

export const disadvantageCards = [
  {
    title: '传统页面割裂',
    desc: '内容散落在多个列表和表单中，用户很难形成完整心智，更谈不上沉浸式体验。',
    image: whyUsImages[3] || null,
  },
  {
    title: '信息密度不均衡',
    desc: '要么只有数字没有故事，要么只有故事没有数据，展示层和业务层始终脱节。',
    image: whyUsImages[4] || null,
  },
  {
    title: '品牌记忆点不足',
    desc: '缺少大标题、动态切换和统一的视觉语言，用户看完后无法快速记住产品能力。',
    image: whyUsImages[5] || null,
  },
]

export const philosophyText = '将人们与世界衔接，引领群众响应国家号召'

export const philosophyNotes = [
  '把复杂政策翻译成可感知、可行动、可传播的界面语言。',
  '既做工具，也做叙事，把技术能力包装成有气场的公共产品。',
]

export const philosophyHeroImage = philosophyImages[0] || pickImage(whyUsImages[1], discoverSlides[2], opinionSlides[0])

export const highlightCards = [
  {
    title: 'Agent 智能体',
    description: '把政策问答、解释、重写和行动建议全部交给云小圆接管。',
    route: '/agent',
    gradient: 'linear-gradient(135deg, rgba(255,125,120,0.95), rgba(255,182,92,0.92))',
    tag: 'AI Agent',
    image: highlightAgentImage,
    imageName: '云小圆.png',
    imagePath: 'web/src/assets/photos/showcase-highlights/云小圆.png',
    imageCaption: '云小圆智能体对话与任务协同展示',
  },
  {
    title: '超酷炫公共数据大屏',
    description: '为演示、汇报和传播准备的沉浸式可视化舞台，数字一眼可读。',
    route: '/showcase/screen',
    gradient: 'linear-gradient(135deg, rgba(64,168,255,0.95), rgba(90,227,255,0.92))',
    tag: 'Visual Screen',
    image: highlightScreenImage,
    imageName: '公共数据大屏.png',
    imagePath: 'web/src/assets/photos/showcase-highlights/公共数据大屏.png',
    imageCaption: '公共数据大屏与汇报型可视化展示',
  },
  {
    title: '可视化政策扫描图谱',
    description: '把散乱的原文和要点提取成结构化结果，让阅读像浏览地图一样轻松。',
    route: '/home',
    gradient: 'linear-gradient(135deg, rgba(131,239,166,0.95), rgba(70,212,214,0.92))',
    tag: 'Scan Map',
    image: highlightScanImage,
    imageName: '可视化知识图谱.png',
    imagePath: 'web/src/assets/photos/showcase-highlights/可视化知识图谱.png',
    imageCaption: '可视化知识图谱与政策关系扫描体验',
  },
  {
    title: '刷剧式无底资讯体验',
    description: '政策与资讯连续流动，适合快速浏览、持续停留和高频发现。',
    route: '/policy-swipe',
    gradient: 'linear-gradient(135deg, rgba(255,118,204,0.95), rgba(132,116,255,0.92))',
    tag: 'Swipe Feed',
    image: highlightSwipeImage,
    imageName: '刷剧资讯体验.png',
    imagePath: 'web/src/assets/photos/showcase-highlights/刷剧资讯体验.png',
    imageCaption: '连续资讯流与刷剧式浏览体验',
  },
]

export const flowSteps = [
  {
    title: '注册并完成身份接入',
    desc: '保留简洁入口与清晰引导，用户第一次到访就能快速理解系统是做什么的。',
    tip: '30 秒内可开始体验',
    process: ['手机号验证码一键进入', '完善身份与偏好', '根据角色开启对应功能'],
    outcome: '建立账号基础与权限边界',
  },
  {
    title: '发现政策与主题内容',
    desc: '在政策广场、大屏和首页叙事之间无缝切换，快速锁定真正需要的内容。',
    tip: '支持连续浏览与筛选',
    process: ['浏览政策广场和资讯流', '打开政策原文阅读区', '收藏、点赞或提交反馈'],
    outcome: '沉淀个人政策阅读路径',
  },
  {
    title: '交给 AI Agent 深入解析',
    desc: '从摘要提炼到任务建议，整个分析链路以对话和结构化结果同步呈现。',
    tip: '输出可直接行动',
    process: ['上传或选择政策文件', '提取材料、对象和办理事项', '生成可执行建议与证据回指'],
    outcome: '形成可复用的政策理解结果',
  },
]

export const landingImageManifest = [
  '02 轮播图组：web/src/assets/photos/discover/slide1.jpg - slide5.jpg；web/src/assets/photos/discover/news/discover-news-01.jpg - discover-news-22.jpg；web/src/assets/photos/main-examples/*.png',
  '04 优势与痛点：web/src/assets/photos/landing/why-us/advantage-1.jpg - advantage-3.jpg；disadvantage-1.jpg - disadvantage-3.jpg',
  '05 理念卡片：当前不再使用右下角配图，保留纯文案主张表达',
  '06 亮点卡片：web/src/assets/photos/showcase-highlights/云小圆.png；web/src/assets/photos/showcase-highlights/公共数据大屏.png；web/src/assets/photos/showcase-highlights/可视化知识图谱.png；web/src/assets/photos/showcase-highlights/刷剧资讯体验.png',
]

export const ctaMetrics = [
  { label: '全链路体验', value: '10 个章节' },
  { label: '可复用 UI 语言', value: '统一动效' },
  { label: '公开演示能力', value: '即开即看' },
]

export const sponsors = (partnerLogos.length
  ? partnerLogos
  : [
      ['/fallback/vue.svg', { default: null }],
      ['/fallback/python.svg', { default: null }],
      ['/fallback/docker.svg', { default: null }],
    ]
)
  .slice(0, 18)
  .map(([path, mod]) => ({
    name: formatPartnerName(path),
    logo: mod.default,
  }))

export const footerLinks = [
  { label: '首页', route: '/showcase' },
  { label: '政策广场', route: '/showcase/discovery' },
  { label: '数据大屏', route: '/showcase/screen' },
  { label: '进入系统', route: '/agent' },
]
