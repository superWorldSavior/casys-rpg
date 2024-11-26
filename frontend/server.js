import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import history from 'connect-history-api-fallback';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 5176;

// Configuration du middleware de base
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Enable CORS with more specific options
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  if (req.method === 'OPTIONS') {
    return res.sendStatus(200);
  }
  next();
});

// Configuration du cache pour les assets statiques
const cacheTime = 86400000 * 30; // 30 jours
const staticOptions = {
  etag: true,
  lastModified: true,
  maxAge: cacheTime,
  setHeaders: (res, path) => {
    if (path.endsWith('.html')) {
      res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
      res.setHeader('Pragma', 'no-cache');
      res.setHeader('Expires', '0');
    } else {
      res.setHeader('Cache-Control', `public, max-age=${cacheTime}`);
    }
  },
};

// Servir d'abord les fichiers statiques
app.use(express.static(path.join(__dirname, 'dist'), staticOptions));

// Configuration du fallback pour les routes SPA
const historyMiddleware = history({
  verbose: true,
  disableDotRule: true,
  index: '/index.html',
  htmlAcceptHeaders: ['text/html', 'application/xhtml+xml'],
  rewrites: [
    {
      from: /^\/assets\/.*/,
      to: function(context) {
        return context.parsedUrl.pathname;
      }
    },
    {
      from: /.*/,
      to: function(context) {
        // Ne pas rediriger les requêtes d'assets
        if (context.parsedUrl.pathname.match(/\.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$/)) {
          return context.parsedUrl.pathname;
        }
        return '/index.html';
      }
    }
  ]
});

// Appliquer le middleware history API fallback
app.use(historyMiddleware);

// Servir à nouveau les fichiers statiques après le fallback
app.use(express.static(path.join(__dirname, 'dist'), staticOptions));

// Route finale pour toutes les autres requêtes
app.get('*', (req, res, next) => {
  // Si c'est une requête pour un fichier statique
  if (req.path.match(/\.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$/)) {
    const filePath = path.join(__dirname, 'dist', req.path);
    return res.sendFile(filePath, err => {
      if (err) {
        next();
      }
    });
  }
  
  // Pour toutes les autres routes, servir index.html
  res.sendFile(path.join(__dirname, 'dist', 'index.html'), err => {
    if (err) {
      next(err);
    }
  });
});

// Gestion des erreurs
app.use((err, req, res, next) => {
  console.error('Error:', err.stack);
  res.status(500).send('Something broke!');
});

// Démarrage du serveur
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running at http://0.0.0.0:${PORT}`);
  console.log('Static files served from:', path.join(__dirname, 'dist'));
  console.log('History API fallback enabled for SPA routes');
});
