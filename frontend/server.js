import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import history from 'connect-history-api-fallback';
import compression from 'compression';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 5176;

// Enable compression
app.use(compression());

// Middleware de logging détaillé
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.originalUrl}`);
  next();
});

// Configuration CORS avec gestion sécurisée
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  
  if (req.method === 'OPTIONS') {
    return res.sendStatus(200);
  }
  next();
});

// Configuration pour le SPA routing
app.use(history({
  verbose: true,
  disableDotRule: true,
  rewrites: [
    { from: /^\/assets\/.*$/, to: context => context.parsedUrl.pathname },
    { from: /^\/manifest\.webmanifest$/, to: '/manifest.webmanifest' },
    { from: /^\/sw\.js$/, to: '/sw.js' },
    { from: /^\/workbox-.*$/, to: context => context.parsedUrl.pathname }
  ]
}));

// Configuration MIME types
app.use((req, res, next) => {
  if (req.url.endsWith('.js')) {
    res.type('application/javascript; charset=utf-8');
  } else if (req.url.endsWith('.mjs')) {
    res.type('application/javascript; charset=utf-8');
  } else if (req.url.endsWith('.css')) {
    res.type('text/css; charset=utf-8');
  }
  next();
});

// Configuration du cache et des types MIME pour les assets statiques
const staticOptions = {
  etag: true,
  lastModified: true,
  index: false,
  setHeaders: (res, filePath) => {
    if (filePath.match(/\.(js|mjs)$/)) {
      res.setHeader('Content-Type', 'application/javascript');
    } else if (filePath.endsWith('.css')) {
      res.setHeader('Content-Type', 'text/css');
    }
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('X-Content-Type-Options', 'nosniff');
  }
};

// Servir les fichiers statiques
const staticPath = path.join(__dirname, 'dist');
app.use(express.static(staticPath, staticOptions));

// Route par défaut pour le SPA
app.get('*', (req, res) => {
  res.sendFile(path.join(staticPath, 'index.html'));
});

// Gestion des erreurs
app.use((err, req, res, next) => {
  console.error('Server error:', err);
  res.status(500).json({
    error: 'Internal Server Error',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
  });
});

// Démarrage du serveur
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running at http://0.0.0.0:${PORT}`);
  console.log('Environment:', process.env.NODE_ENV);
  console.log('Static files path:', staticPath);
});
