import { createBrowserRouter, Navigate, Link } from "react-router-dom";
import { lazy, Suspense } from "react";
import { Box, Typography, Button } from "@mui/material";
import Layout from "../layouts/MainLayout.jsx"; // Importation correcte
import { ProtectedRoute } from "../components/common/ProtectedRoute.jsx";

// Lazy load components
const LoginPage = lazy(() => import("../pages/Auth/LoginPage.jsx"));
const HomePage = lazy(() => import("../pages/Home/index.jsx"));
const ReaderPage = lazy(() => import("../pages/Reader"));
const BrowsePage = lazy(() => import("../pages/Browse/index.jsx"));
const LibraryPage = lazy(() => import("../pages/Library/index.jsx"));
const ProfilePage = lazy(() => import("../pages/Profile/index.jsx"));
const BookDetailsPage = lazy(() => import("../pages/Book/BookDetailsPage.jsx"));

const AuthenticatedLayout = () => {
  return (
    <ProtectedRoute>
      <Layout />
    </ProtectedRoute>
  );
};

const SuspenseWrapper = ({ children }) => (
  <Suspense fallback={<div>Chargement...</div>}>{children}</Suspense>
);

const HomeErrorBoundary = () => (
  <Box sx={{ p: 3, textAlign: "center" }}>
    <Typography variant="h6">
      Une erreur est survenue lors du chargement de la page
    </Typography>
    <Button component={Link} to="/" sx={{ mt: 2 }}>
      Retourner à l'accueil
    </Button>
  </Box>
);

const routerOptions = {
  future: {
    v7_startTransition: true,
    v7_normalizeFormMethod: true,
    v7_relativeSplatPath: true,
    v7_fetcherPersist: true,
    v7_partialHydration: true,
    v7_skipActionErrorRevalidation: true,
  },
};

const router = createBrowserRouter([
  {
    path: "/",
    element: <Navigate to="/login" replace />,
  },
  {
    path: "/login",
    element: (
      <SuspenseWrapper>
        <LoginPage />
      </SuspenseWrapper>
    ),
    errorElement: <HomeErrorBoundary />,
  },
  {
    path: "/reader/:bookId",
    element: (
      <SuspenseWrapper>
        <ReaderPage />
      </SuspenseWrapper>
    ),
    errorElement: <HomeErrorBoundary />,
  },
  {
    path: "/",
    element: <AuthenticatedLayout />,
    errorElement: <HomeErrorBoundary />,
    children: [
      {
        index: true,
        element: (
          <SuspenseWrapper>
            <HomePage />
          </SuspenseWrapper>
        ),
      },
      {
        path: "library",
        element: (
          <SuspenseWrapper>
            <LibraryPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: "browse",
        element: (
          <SuspenseWrapper>
            <BrowsePage />
          </SuspenseWrapper>
        ),
      },
      {
        path: "profile",
        element: (
          <SuspenseWrapper>
            <ProfilePage />
          </SuspenseWrapper>
        ),
      },
      {
        path: "books/:bookId",
        element: (
          <SuspenseWrapper>
            <BookDetailsPage />
          </SuspenseWrapper>
        ),
      },
      {
        path: "*",
        element: <Navigate to="/" replace />,
      },
    ],
  },
], {
  future: routerOptions.future,
});

export { router };
