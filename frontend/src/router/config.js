import { createBrowserRouter } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import MainLayout from '../layouts/MainLayout';
import LandingPage from '../components/pages/LandingPage';
import LoginPage from '../components/pages/LoginPage';
import RegisterPage from '../components/pages/RegisterPage';
import ProtectedRoute from '../components/ProtectedRoute';
import { CircularProgress, Container } from '@mui/material';

// Lazy load pages
const LibraryPage = lazy(() => import('../pages/Home'));
const ReaderPage = lazy(() => import('../pages/Reader'));

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

// Router configuration
export const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
      {
        index: true,
        element: <LandingPage />
      },
      {
        path: "login",
        element: <LoginPage />
      },
      {
        path: "register",
        element: <RegisterPage />
      },
      {
        path: "library",
        element: (
          <ProtectedRoute>
            <Suspense fallback={<LoadingFallback />}>
              <LibraryPage />
            </Suspense>
          </ProtectedRoute>
        )
      },
      {
        path: "reader/:bookId",
        element: (
          <ProtectedRoute>
            <Suspense fallback={<LoadingFallback />}>
              <ReaderPage />
            </Suspense>
          </ProtectedRoute>
        )
      }
    ]
  }
], {
  future: {
    v7_startTransition: true,
    v7_relativeSplatPath: true,
    v7_fetcherPersist: true,
    v7_normalizeFormMethod: true,
    v7_partialHydration: true,
    v7_skipActionErrorRevalidation: true
  }
});
