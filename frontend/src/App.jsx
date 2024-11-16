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

// Lazy load pages
const HomePage = React.lazy(() => import('./pages/Home'));
const ReaderPage = React.lazy(() => import('./pages/Reader'));

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return (
        <Container sx={{ mt: 4, textAlign: 'center' }}>
          <h2>Something went wrong.</h2>
          <button onClick={() => window.location.href = '/'}>
            Return to Home
          </button>
        </Container>
      );
    }

    return this.props.children;
  }
}

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
        <ErrorBoundary>
          <MainLayout />
        </ErrorBoundary>
      }
    >
      <Route
        index
        element={
          <Suspense fallback={<LoadingFallback />}>
            <HomePage />
          </Suspense>
        }
      />
      <Route
        path="reader/:bookId"
        element={
          <Suspense fallback={<LoadingFallback />}>
            <ReaderPage />
          </Suspense>
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
