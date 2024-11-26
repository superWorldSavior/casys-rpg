import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import history from 'connect-history-api-fallback';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 5176;

// Middleware de logging détaillé
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.originalUrl}`);
  next();
});

// Configuration CORS avec gestion sécurisée
app.use((req, res, next) => {
  const allowedOrigins = ['http://localhost:5176', 'https://localhost:5176', 'http://0.0.0.0:5176'];
  const origin = req.headers.origin;
  
  if (allowedOrigins.includes(origin)) {
    res.header('Access-Control-Allow-Origin', origin);
  }
  
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  res.header('Access-Control-Allow-Credentials', 'true');
  
  if (req.method === 'OPTIONS') {
    return res.sendStatus(200);
  }
  next();
});

// Chemin vers les fichiers statiques
const staticPath = path.join(__dirname, 'dist');
console.log('Serving static files from:', staticPath);

// Configuration du cache pour les assets statiques
const staticOptions = {
  etag: true,
  lastModified: true,
  setHeaders: (res, filePath) => {
    if (filePath.endsWith('.html')) {
      res.setHeader('Cache-Control', 'no-cache');
      res.setHeader('Content-Type', 'text/html; charset=utf-8');
    } else if (filePath.match(/\.(js|mjs)$/)) {
      res.setHeader('Cache-Control', 'public, max-age=31536000');
      res.setHeader('Content-Type', 'application/javascript; charset=utf-8');
      res.setHeader('X-Content-Type-Options', 'nosniff');
    } else if (filePath.endsWith('.css')) {
      res.setHeader('Cache-Control', 'public, max-age=31536000');
      res.setHeader('Content-Type', 'text/css; charset=utf-8');
    } else if (filePath.match(/\.(png|jpg|jpeg|gif|ico|svg|woff2?)$/)) {
      res.setHeader('Cache-Control', 'public, max-age=31536000');
    } else {
      res.setHeader('Cache-Control', 'public, max-age=0');
    }
  }
};

// Servir les fichiers statiques avant le middleware history
app.use(express.static(staticPath, staticOptions));

// Configuration pour le SPA routing
app.use(history({
  verbose: true,
  rewrites: [
    { 
      from: /^\/assets\/.*$/,
      to: context => context.parsedUrl.pathname
    },
    {
      from: /^\/manifest\.webmanifest$/,
      to: '/manifest.webmanifest'
    },
    {
      from: /^\/sw\.js$/,
      to: '/sw.js'
    },
    {
      from: /^\/workbox-.*$/,
      to: context => context.parsedUrl.pathname
    }
  ]
}));

// Servir à nouveau les fichiers statiques après le middleware history
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
