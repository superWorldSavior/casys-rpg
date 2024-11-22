import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'node:url'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      '@components': fileURLToPath(new URL('./src/components', import.meta.url)),
      '@layouts': fileURLToPath(new URL('./src/layouts', import.meta.url)),
      '@pages': fileURLToPath(new URL('./src/pages', import.meta.url)),
      '@assets': fileURLToPath(new URL('./src/assets', import.meta.url)),
      '@lib': fileURLToPath(new URL('./src/lib', import.meta.url))
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5174,
    watch: {
      usePolling: true
    }
  },
  build: {
    target: 'esnext',
    outDir: 'dist',
    minify: 'esbuild',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html')
      }
    }
  },
  optimizeDeps: {
    include: [
      'vue',
      'vue-router',
      '@vueuse/core',
      '@vueuse/head',
      'class-variance-authority',
      'clsx',
      'tailwind-merge',
      'radix-vue',
      'vue-sonner'
    ]
  }
})
