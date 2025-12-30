import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import ToastService from 'primevue/toastservice'
import ECharts from 'vue-echarts'
import './plugins/echarts'
import './style.css'
import 'primeicons/primeicons.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

// Enable Pinia DevTools in development
if (import.meta.env.DEV) {
  pinia.use(({ store }) => {
    store._customProperties = store._customProperties || new Set()
  })
}

// Configure PrimeVue with Aura theme
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: '.dark-mode',
      cssLayer: {
        name: 'primevue',
        order: 'tailwind-base, primevue, tailwind-utilities',
      },
    },
  },
})

app.use(ToastService)
app.use(pinia)
app.use(router)

// Register vue-echarts component globally
app.component('VChart', ECharts)

app.mount('#app')
