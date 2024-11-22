import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import App from './App.vue'
import router from './router'
import './style.css'

// Vuetify
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#6E1187',
          secondary: '#2B2B2B',
          accent: '#A870B7',
          surface: '#FBFBFB',
          background: '#F7F7F7',
          cassis: '#6E1187',
        },
      },
      dark: {
        colors: {
          primary: '#6E1187',
          secondary: '#2B2B2B',
          accent: '#A870B7',
          surface: '#1A1A1A',
          background: '#111111',
          cassis: '#6E1187',
        },
      },
    },
  },
})

// Appliquer la police Courier New globalement
document.documentElement.style.setProperty('font-family', '"Courier New", monospace');

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
