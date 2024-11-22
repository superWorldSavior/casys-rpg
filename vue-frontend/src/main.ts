import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import './style.css'

function initApp() {
  const app = createApp(App)
  const pinia = createPinia()
  
  app.use(pinia)
  app.use(router)
  
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
