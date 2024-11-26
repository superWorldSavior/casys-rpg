import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [
    react({
      jsxRuntime: 'automatic',
    })
  ],
  preview: {
    port: 5175,
    host: '0.0.0.0',
    strictPort: true,
    cors: true,
    proxy: {
      '/api': {
        target: 'http://0.0.0.0:5000',
        changeOrigin: true,
        secure: false
      }
    },
    historyApiFallback: {
      disableDotRule: true,
      rewrites: [
        { from: /^\/.*/, to: '/index.html' }
      ]
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['react', 'react-dom'],
          'router': ['react-router-dom'],
          'mui': ['@mui/material'],
          'mui-deps': ['@emotion/react', '@emotion/styled']
        }
      }
    }
  },
  base: '/',
  server: {
    middlewareMode: false,
    fs: {
      strict: false
    }
  },
  resolve: {
    alias: {
      '@': '/src'
    }
  },
  publicDir: 'public',
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom']
  }
});
