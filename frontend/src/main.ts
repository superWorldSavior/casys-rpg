import { createApp } from 'vue'
import { createHead } from '@vueuse/head'
import App from './App.vue'
import router from './router'
import './assets/main.css'

const app = createApp(App)
const head = createHead()

// Configure error handling
app.config.errorHandler = (err, vm, info) => {
  console.error('Vue Error:', err)
  console.error('Error Info:', info)
}

app.config.warnHandler = (msg, vm, trace) => {
  console.warn('Vue Warning:', msg)
  console.warn('Trace:', trace)
}

// Add plugins
app.use(router)
app.use(head)

// Mount the app
app.mount('#app')
