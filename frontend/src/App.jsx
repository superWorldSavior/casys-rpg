import React, { Suspense } from 'react';
import { 
  createBrowserRouter,
  RouterProvider,
  createRoutesFromElements,
  Route,
  Navigate,
  useLocation
} from 'react-router-dom';
import { CircularProgress, Container, ThemeProvider } from '@mui/material';
import ErrorBoundary from './components/common/ErrorBoundary';
import { casysTheme } from './theme/casysTheme';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { publicRoutes, protectedRoutes } from './router/config';

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

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

// Create router with future flags
const router = createBrowserRouter(
  createRoutesFromElements(
    <>
      {/* Public Routes */}
      {publicRoutes.map((route) => (
        <Route
          key={route.path}
          path={route.path}
          element={
            <ErrorBoundary fallbackMessage="Une erreur s'est produite">
              <Suspense fallback={<LoadingFallback />}>
                {route.element}
              </Suspense>
            </ErrorBoundary>
          }
        />
      ))}

      {/* Protected Routes */}
      {protectedRoutes.map((route) => (
        <Route
          key={route.path}
          path={route.path}
          element={
            <ErrorBoundary fallbackMessage="Une erreur s'est produite">
              <ProtectedRoute>
                <Suspense fallback={<LoadingFallback />}>
                  {route.element}
                </Suspense>
              </ProtectedRoute>
            </ErrorBoundary>
          }
        >
          {route.children?.map((childRoute) => (
            <Route
              key={childRoute.path || 'index'}
              index={childRoute.index}
              path={childRoute.path}
              element={
                <ErrorBoundary fallbackMessage="Une erreur s'est produite">
                  <Suspense fallback={<LoadingFallback />}>
                    {childRoute.element}
                  </Suspense>
                </ErrorBoundary>
              }
            />
          ))}
        </Route>
      ))}

      <Route path="*" element={<Navigate to="/login" replace />} />
    </>
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
  return (
    <ThemeProvider theme={casysTheme}>
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
