import React, { Suspense, lazy } from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { ThemeProvider, CircularProgress } from '@mui/material';
import { Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { casysTheme } from './theme/casysTheme';
import { ProtectedRoute } from './router/ProtectedRoute';

// Lazy load components
const LoginPage = lazy(() => import('./pages/Auth/LoginPage'));
const HomePage = lazy(() => import('./pages/Home'));
const ReaderPage = lazy(() => import('./pages/Reader'));

// Loading fallback
const LoadingFallback = () => (
  <div style={{ 
    display: 'flex', 
    justifyContent: 'center', 
    alignItems: 'center', 
    height: '100vh' 
  }}>
    <CircularProgress />
  </div>
);

const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/login" replace />
  },
  {
    path: '/login',
    element: <Suspense fallback={<LoadingFallback />}><LoginPage /></Suspense>
  },
  {
    path: '/home',
    element: (
      <ProtectedRoute>
        <Suspense fallback={<LoadingFallback />}>
          <HomePage />
        </Suspense>
      </ProtectedRoute>
    )
  },
  {
    path: '/reader/:bookId',
    element: (
      <ProtectedRoute>
        <Suspense fallback={<LoadingFallback />}>
          <ReaderPage />
        </Suspense>
      </ProtectedRoute>
    )
  }
], {
  future: {
    v7_startTransition: true
  }
});

function App() {
  return (
    <ThemeProvider theme={casysTheme}>
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
