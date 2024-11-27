import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";
import path from "path";

export default defineConfig({
  // base: "./",
  plugins: [
    react({
      jsxRuntime: "automatic",
      jsxImportSource: "@emotion/react",
      babel: {
        plugins: ["@emotion/babel-plugin"],
      },
    }),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["favicon.ico", "apple-touch-icon.png", "masked-icon.svg"],
      manifest: {
        name: "Text Flow Navigator",
        short_name: "TextFlow",
        description: "Solo RPG AI Narrator application",
        theme_color: "#ffffff",
        icons: [
          {
            src: "pwa-192x192.png",
            sizes: "192x192",
            type: "image/png",
          },
          {
            src: "pwa-512x512.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "any maskable",
          },
        ],
      },
    }),
  ],
  server: {
    port: 4173,
    host: "0.0.0.0",
    cors: true,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
      "Access-Control-Allow-Headers":
        "Content-Type, Authorization, X-Requested-With",
      "Access-Control-Allow-Credentials": "true",
    },
    fs: {
      strict: false,
      allow: [".."],
    },
    proxy: {
      "/api": {
        target: "http://0.0.0.0:5000",
        changeOrigin: true,
        secure: false,
        ws: false,
        configure: (proxy, _options) => {
          proxy.on("error", (err, _req, _res) => {
            console.error("Proxy error:", err);
          });
          proxy.on("proxyReq", (proxyReq, req, _res) => {
            console.log("Sending Request:", req.method, req.url);
            if (req.body) {
              const bodyData = JSON.stringify(req.body);
              proxyReq.setHeader("Content-Type", "application/json");
              proxyReq.setHeader("Content-Length", Buffer.byteLength(bodyData));
              proxyReq.write(bodyData);
            }
          });
          proxy.on("proxyRes", (proxyRes, req, _res) => {
            console.log("Received Response:", proxyRes.statusCode, req.url);
          });
        },
      },
    },
  },
  optimizeDeps: {
    include: [
      "@emotion/react",
      "@emotion/styled",
      "@emotion/cache",
      "react",
      "react-dom",
      "@mui/material",
      "@mui/icons-material",
    ],
    exclude: [],
    esbuildOptions: {
      target: "es2020",
    },
  },
  define: {
    "process.env.NODE_ENV": JSON.stringify(process.env.NODE_ENV),
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
    dedupe: [
      "react",
      "react-dom",
      "@emotion/react",
      "@emotion/styled",
      "@emotion/cache",
    ],
  },
  build: {
    outDir: "dist",
    assetsDir: "assets",
    sourcemap: true,
    manifest: true,
    // rollupOptions: {
    //   output: {
    //     manualChunks: {
    //       vendor: ["react", "react-dom", "@emotion/cache"],
    //       router: ["react-router-dom"],
    //       mui: ["@mui/material"],
    //       "mui-deps": ["@emotion/react", "@emotion/styled"],
    //     },
    //   },
    // },
  },
});
