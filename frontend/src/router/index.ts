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
  ],
})

export default router
