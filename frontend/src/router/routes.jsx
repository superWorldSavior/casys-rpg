import { createBrowserRouter, Navigate } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import Layout from '../layouts/MainLayout';
import { ProtectedRoute } from '../components/common/ProtectedRoute';

// Lazy load components
const LoginPage = lazy(() => import('../pages/Auth/LoginPage'));
const HomePage = lazy(() => import('../pages/Home'));
const ReaderPage = lazy(() => import('../pages/Reader'));
const BrowsePage = lazy(() => import('../pages/Browse'));
const LibraryPage = lazy(() => import('../pages/Library'));
const ProfilePage = lazy(() => import('../pages/Profile'));

const AuthenticatedLayout = () => {
  return (
    <ProtectedRoute>
      <Layout />
    </ProtectedRoute>
  );
};

const SuspenseWrapper = ({ children }) => (
  <Suspense fallback={<div>Chargement...</div>}>
    {children}
  </Suspense>
);

const router = createBrowserRouter([
  {
    path: '/login',
    element: <SuspenseWrapper><LoginPage /></SuspenseWrapper>
  },
  {
    path: '/',
    element: <AuthenticatedLayout />,
    children: [
      {
        index: true,
        element: <Navigate to="/home" replace />
      },
      {
        path: 'home',
        element: <SuspenseWrapper><HomePage /></SuspenseWrapper>
      },
      {
        path: 'library',
        element: <SuspenseWrapper><LibraryPage /></SuspenseWrapper>
      },
      {
        path: 'browse',
        element: <SuspenseWrapper><BrowsePage /></SuspenseWrapper>
      },
      {
        path: 'profile',
        element: <SuspenseWrapper><ProfilePage /></SuspenseWrapper>
      },
      {
        path: 'reader/:bookId',
        element: <SuspenseWrapper><ReaderPage /></SuspenseWrapper>
      },
      {
        path: '*',
        element: <Navigate to="/home" replace />
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
    v7_prependBasename: true,
    v7_skipActionErrorRevalidation: true
  }
});

// Configure additional options for the router
router.future = {
  v7_startTransition: true,
  v7_relativeSplatPath: true,
  v7_fetcherPersist: true,
  v7_normalizeFormMethod: true,
  v7_partialHydration: true,
  v7_prependBasename: true,
  v7_skipActionErrorRevalidation: true
};
export default router;
