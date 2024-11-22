import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { VBottomNavigation } from 'vuetify/components'
import { VApp, VMain, VLayout } from 'vuetify/components'
import App from './App.vue'
import router from './router'
import './style.css'

// Vuetify
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'

const vuetify = createVuetify({
  components: {
    VBottomNavigation,
    VApp,
    VMain,
    VLayout,
    ...components
  },
  directives,
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#1a73e8',
          secondary: '#5f6368',
          accent: '#1a73e8',
        },
      },
      dark: {
        colors: {
          primary: '#8ab4f8',
          secondary: '#9aa0a6',
          accent: '#8ab4f8',
        },
      },
    },
  },
})

function initApp() {
  const app = createApp(App)
  const pinia = createPinia()
  
  app.use(pinia)
  app.use(router)
  app.use(vuetify)
  
  // Gestionnaire d'erreur global pour Vue
  app.config.errorHandler = (err, _vm, info) => {
    console.error('Erreur Vue:', err);
    console.error('Info:', info);
  };

  // Gestionnaire global des rejets de promesses non traités
  window.addEventListener('unhandledrejection', function(event) {
    console.error('Rejet de promesse non traité:', event.reason);
    event.preventDefault();
  });

  // Monter l'application
  app.mount('#app')
}

initApp()
