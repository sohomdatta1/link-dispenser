import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AnalyzedResultsView from '../views/AnalyzedResultsView.vue'
import LLMResultsView from '@/views/LLMResultsView.vue'
import AnalysisView from '../views/AnalysisView.vue'
import LLMAnalysisView from '../views/LLMAnalysisView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/auth/login',
      name: 'loginPrompt',
      component: () => import('../views/LoginPromptView.vue'),
      meta: { public: true }
    },
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { public: true }
    },
    {
      path: '/analyze/:lang/:articleName(.*)',
      name: 'analyze',
      component: AnalyzedResultsView
    },
    {
      path: '/llmanalyze/:lang/:articleName(.*)',
      name: 'llmanalyze',
      component: LLMResultsView
    },
    {
      path: '/analyze/:articleName(.*)',
      name: 'legacyAnalyze',
      component: AnalyzedResultsView,
      props: route => ({
        lang: 'en',
        articleName: route.params.articleName
      })
    },
    {
      path: '/llmanalyze/:articleName(.*)',
      name: 'legacyLlmanalyze',
      component: LLMResultsView,
      props: route => ({
        lang: 'en',
        articleName: route.params.articleName
      })
    },
    {
      path: '/analysis/:uuid',
      name: 'analysis',
      component: AnalysisView
    },
    {
      path: '/llmanalysis/:uuid',
      name: 'llmanalysis',
      component: LLMAnalysisView
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
      meta: { public: true }
    }
  ]
})

let authChecked = false
let cachedAuthenticated = false
async function isAuthenticated(): Promise<boolean> {
  if (authChecked) {
    return cachedAuthenticated
  }
  try {
    const resp = await fetch('/api/whoami')
    const json = await resp.json()
    cachedAuthenticated = Boolean(json?.authenticated)
  } catch (_) {
    cachedAuthenticated = false
  }
  authChecked = true
  return cachedAuthenticated
}

router.beforeEach(async (to) => {
  console.log(to);
  if (to.matched.some((r) => r.meta?.public)) {
    return true
  }

  if (await isAuthenticated()) {
    return true
  }

  return {
    name: 'loginPrompt',
    query: { next: to.fullPath }
  }
})

export default router
