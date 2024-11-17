import React, { Suspense } from 'react';
import { 
  createBrowserRouter,
  RouterProvider,
  createRoutesFromElements,
  Route,
  Navigate
} from 'react-router-dom';
import { CircularProgress, Container } from '@mui/material';
import MainLayout from './layouts/MainLayout';
import ErrorBoundary from './components/common/ErrorBoundary';

// Lazy load pages
const HomePage = React.lazy(() => import('./pages/Home'));
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
          <MainLayout />
        </ErrorBoundary>
      }
    >
      <Route
        index
        element={
          <ErrorBoundary fallbackMessage="An error occurred while loading the library">
            <Suspense fallback={<LoadingFallback />}>
              <HomePage />
            </Suspense>
          </ErrorBoundary>
        }
      />
      <Route
        path="reader/:bookId"
        element={
          <ErrorBoundary fallbackMessage="An error occurred while loading the reader">
            <Suspense fallback={<LoadingFallback />}>
              <ReaderPage />
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

function App() {
  return <RouterProvider router={router} />;
}

export default App;