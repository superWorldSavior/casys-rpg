import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5174,
    host: '0.0.0.0',
    hmr: {
      clientPort: 443,
      host: '0.0.0.0'
    }
  },
  preview: {
    port: 5174,
    host: '0.0.0.0'
  },
  base: '',
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
