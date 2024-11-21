import React, { Suspense } from 'react';
import { 
  createBrowserRouter,
  RouterProvider,
  createRoutesFromElements,
  Route,
  Navigate
} from 'react-router-dom';
import { CircularProgress, Container, ThemeProvider } from '@mui/material';
import MainLayout from './layouts/MainLayout';
import ErrorBoundary from './components/common/ErrorBoundary';
import { casysTheme } from './theme/casysTheme';

// Lazy load pages
const LandingPage = React.lazy(() => import('./components/pages/LandingPage'));
const LoginPage = React.lazy(() => import('./components/pages/LoginPage'));
const RegisterPage = React.lazy(() => import('./components/pages/RegisterPage'));
const LibraryPage = React.lazy(() => import('./pages/Home'));
const ReaderPage = React.lazy(() => import('./pages/Reader'));

// Loading Component
const LoadingFallback = () => (
  <Container sx={{ 
    mt: 4, 
    display: 'flex', 
    justifyContent: 'center', 
    alignItems: 'center' 
  }}>
    <CircularProgress />
  </Container>
);

// Create router with future flags
const router = createBrowserRouter(
  createRoutesFromElements(
    <Route
      path="/"
      element={
        <ErrorBoundary fallbackMessage="An error occurred in the application layout">
          <AuthProvider>
            <MainLayout />
          </AuthProvider>
        </ErrorBoundary>
      }
    >
      <Route
        index
        element={
          <ErrorBoundary fallbackMessage="An error occurred while loading the landing page">
            <Suspense fallback={<LoadingFallback />}>
              <LandingPage />
            </Suspense>
          </ErrorBoundary>
        }
      />
      <Route
        path="login"
        element={
          <ErrorBoundary fallbackMessage="An error occurred while loading the login page">
            <Suspense fallback={<LoadingFallback />}>
              <LoginPage />
            </Suspense>
          </ErrorBoundary>
        }
      />
      <Route
        path="register"
        element={
          <ErrorBoundary fallbackMessage="An error occurred while loading the register page">
            <Suspense fallback={<LoadingFallback />}>
              <RegisterPage />
            </Suspense>
          </ErrorBoundary>
        }
      />
      <Route
        path="library"
        element={
          <ErrorBoundary fallbackMessage="An error occurred while loading the library">
            <Suspense fallback={<LoadingFallback />}>
              <ProtectedRoute>
                <LibraryPage />
              </ProtectedRoute>
            </Suspense>
          </ErrorBoundary>
        }
      />
      <Route
        path="reader/:bookId"
        element={
          <ErrorBoundary fallbackMessage="An error occurred while loading the reader">
            <Suspense fallback={<LoadingFallback />}>
              <ProtectedRoute>
                <ReaderPage />
              </ProtectedRoute>
            </Suspense>
          </ErrorBoundary>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Route>
  ),
  {
    future: {
      v7_startTransition: true,
      v7_relativeSplatPath: true,
      v7_fetcherPersist: true,
      v7_normalizeFormMethod: true,
      v7_partialHydration: true,
      v7_skipActionErrorRevalidation: true
    }
  }
);

// Import AuthProvider
import { AuthProvider } from './context/AuthContext';

function App() {
  return (
    <ThemeProvider theme={casysTheme}>
      <AuthProvider>
        <RouterProvider 
          router={router}
          fallbackElement={<LoadingFallback />}
        />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
