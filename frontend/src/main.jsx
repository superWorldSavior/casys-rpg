import React, { Suspense } from 'react'
import ReactDOM from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import { ThemeProvider } from '@mui/material'
import CssBaseline from '@mui/material/CssBaseline'
import { ErrorBoundary } from 'react-error-boundary'
import { router } from './router/routes'
import { casysTheme } from './theme/casysTheme'
import { AuthProvider } from './contexts/AuthContext'
import './index.css'

const LoadingFallback = () => (
  <div style={{ 
    display: 'flex', 
    justifyContent: 'center', 
    alignItems: 'center', 
    height: '100vh',
    color: 'white'
  }}>
    Chargement...
  </div>
);

const ErrorFallback = ({ error }) => (
  <div style={{ 
    padding: '20px', 
    color: 'red',
    textAlign: 'center' 
  }}>
    <h2>Une erreur est survenue</h2>
    <pre>{error.message}</pre>
  </div>
);

const App = () => {
  return (
    <React.StrictMode>
      <ErrorBoundary FallbackComponent={ErrorFallback}>
        <Suspense fallback={<LoadingFallback />}>
          <ThemeProvider theme={casysTheme}>
            <CssBaseline />
            <AuthProvider>
              <RouterProvider router={router} fallbackElement={<LoadingFallback />} />
            </AuthProvider>
          </ThemeProvider>
        </Suspense>
      </ErrorBoundary>
    </React.StrictMode>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
