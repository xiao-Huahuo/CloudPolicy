import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/auth.js'
import Home from '../views/Home.vue'
import DiscoveryHome from '../views/DiscoveryHome.vue'
import DataAnalysisAndVisualization from '../views/DataAnalysisAndVisualization.vue'
import History from '../views/History.vue'
import Favorites from '../views/Favorites.vue'
import Profile from '../views/Profile.vue'
import Search from '../views/Search.vue'
import Rewrite from '../views/Rewrite.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Settings from '../views/Settings.vue'
import TodoList from '../views/TodoList.vue'
import Admin from '../views/Admin.vue'
import Agent from '../views/Agent.vue'
import PublicOpinionHall from '../views/PublicOpinionHall.vue'
import CertifiedAnalysis from '../views/CertifiedAnalysis.vue'
import PolicyPublishCenter from '../views/PolicyPublishCenter.vue'
import PolicySwipe from '../views/PolicySwipe.vue'
import ShowcaseLanding from '../views/showcase/ShowcaseLanding.vue'
import ShowcaseDiscovery from '../views/showcase/ShowcaseDiscovery.vue'
import ShowcaseScreen from '../views/showcase/ShowcaseScreen.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    return { top: 0, left: 0 }
  },
  routes: [
    { path: '/', redirect: '/agent' },
    { path: '/home', name: 'home', component: Home },
    { path: '/discovery-home', name: 'discovery-home', component: DiscoveryHome, meta: { standalone: true } },
    { path: '/data-analysis-and-visualization', name: 'data-analysis-and-visualization', component: DataAnalysisAndVisualization },
    { path: '/history', name: 'history', component: History },
    { path: '/favorites', name: 'favorites', component: Favorites },
    { path: '/profile', name: 'profile', component: Profile },
    { path: '/settings', name: 'settings', component: Settings },
    { path: '/search', name: 'search', component: Search },
    { path: '/rewrite', name: 'rewrite', component: Rewrite },
    { path: '/login', name: 'login', component: Login, meta: { standalone: true } },
    { path: '/register', name: 'register', component: Register, meta: { standalone: true } },
    { path: '/todo', name: 'todo', component: TodoList },
    { path: '/admin', name: 'admin', component: Admin, meta: { requiresAdmin: true } },
    { path: '/agent', name: 'agent', component: Agent },
    { path: '/public-opinion-hall', name: 'public-opinion-hall', component: PublicOpinionHall },
    { path: '/certified-analysis', name: 'certified-analysis', component: CertifiedAnalysis },
    { path: '/policy-publish-center', name: 'policy-publish-center', component: PolicyPublishCenter },
    { path: '/policy-swipe', name: 'policy-swipe', component: PolicySwipe },
    { path: '/showcase', name: 'showcase', component: ShowcaseLanding, meta: { showcase: true } },
    { path: '/showcase/discovery', name: 'showcase-discovery', component: ShowcaseDiscovery, meta: { showcase: true } },
    { path: '/showcase/screen', name: 'showcase-screen', component: ShowcaseScreen, meta: { showcase: true } },
  ],
})

router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresAdmin) {
    const userStore = useUserStore()
    if (userStore.token && !userStore.user) {
      await userStore.fetchUser()
    }
    if (!userStore.isAdmin) return next('/agent')
  }
  next()
})

export default router
