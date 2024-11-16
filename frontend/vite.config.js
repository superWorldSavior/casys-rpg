import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://0.0.0.0:5000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    outDir: path.resolve(__dirname, 'dist'),
    assetsDir: 'assets',
    emptyOutDir: true,
    sourcemap: true,
    manifest: true,
    rollupOptions: {
      output: {
        manualChunks: undefined
      }
    }
  },
  base: '/',
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom', '@mui/material', '@emotion/react', '@emotion/styled']
  }
})
