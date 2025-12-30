import { createRouter, createWebHistory } from 'vue-router'
import Health from '../views/Health.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'health',
      component: Health,
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/LeagueDashboard.vue'),
      meta: {
        title: 'League Dashboard',
      },
    },
    {
      path: '/demo',
      name: 'demo',
      // Lazy load demo page to reduce initial bundle size
      component: () => import('../views/Demo.vue'),
    },
  ],
})

export default router
