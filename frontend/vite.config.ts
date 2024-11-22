import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'
import path from 'path'

// https://vitejs.dev/config/
import type { VitePWAOptions } from 'vite-plugin-pwa'

const pwaConfig: Partial<VitePWAOptions> = {
  strategies: 'generateSW',
  registerType: 'autoUpdate',
  devOptions: {
    enabled: true,
    type: 'module'
  },
  manifest: {
    name: 'TextFlow Navigator',
    short_name: 'TextFlow',
    description: 'AI-powered audiobook experience',
    theme_color: '#4F46E5',
    background_color: '#ffffff',
    display: 'standalone',
    scope: '/',
    start_url: '/',
    orientation: 'portrait',
    icons: [
      {
        src: '/icon-192x192.png',
        sizes: '192x192',
        type: 'image/png'
      },
      {
        src: '/icon-512x512.png',
        sizes: '512x512',
        type: 'image/png',
        purpose: 'any maskable'
      }
    ]
  },
  injectRegister: 'auto',
  workbox: {
    globPatterns: ['**/*.{js,css,html,ico,png,svg,mp3,wav}'],
    cleanupOutdatedCaches: true,
    skipWaiting: true,
    clientsClaim: true,
    runtimeCaching: [
      {
        urlPattern: /^https:\/\/api\.openai\.com\/v1/,
        handler: 'NetworkFirst',
        options: {
          cacheName: 'api-cache',
          expiration: {
            maxEntries: 50,
            maxAgeSeconds: 24 * 60 * 60
          },
          networkTimeoutSeconds: 10
        }
      },
      {
        urlPattern: /\.(mp3|wav)$/,
        handler: 'CacheFirst',
        options: {
          cacheName: 'audio-cache',
          expiration: {
            maxEntries: 50,
            maxAgeSeconds: 7 * 24 * 60 * 60
          },
          rangeRequests: true
        }
      }
    ]
  }
}

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  plugins: [
    react(),
    VitePWA(pwaConfig),
  ],
  server: {
    port: 5173,
    host: '0.0.0.0',
    strictPort: true,
    cors: true,
    headers: {
      'Cross-Origin-Opener-Policy': 'same-origin-allow-popups',
      'Cross-Origin-Embedder-Policy': 'unsafe-none'
    }
  },
  preview: {
    port: 5173,
    host: '0.0.0.0',
    strictPort: true
  },
  base: "/",
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['@radix-ui/react-navigation-menu', '@radix-ui/react-slider']
        }
      }
    }
  }
})
