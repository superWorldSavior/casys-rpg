import React from 'react'
import { createRoot } from 'react-dom/client'
import { registerSW } from 'virtual:pwa-register'
import App from './App'
import './index.css'

// Register service worker for PWA functionality with improved error handling
const updateSW = registerSW({
  immediate: true,
  onNeedRefresh() {
    if (confirm('New content available. Reload to update?')) {
      updateSW(true)
    }
  },
  onOfflineReady() {
    console.log('📱 App ready to work offline')
  },
  onRegistered(registration) {
    console.log('SW Registered:', registration)
    // Force update check
    registration?.update()
  },
  onRegisterError(error) {
    console.error('SW registration error:', error)
  }
})

const container = document.getElementById('root')
if (!container) {
  throw new Error('Root element not found')
}

const root = createRoot(container)
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
