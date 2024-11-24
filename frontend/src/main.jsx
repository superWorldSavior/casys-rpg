import React from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider } from "react-router-dom";
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { ErrorBoundary } from "react-error-boundary";
import { Box, CircularProgress } from "@mui/material";
import { router } from "./router/routes.jsx";
import { casysTheme } from "./theme/casysTheme.js";
import { AuthProvider } from "./contexts/AuthContext.jsx";
import "./index.css";

const LoadingFallback = () => (
  <Box
    display="flex"
    justifyContent="center"
    alignItems="center"
    minHeight="100vh"
    bgcolor="background.default"
    color="text.primary"
  >
    <CircularProgress />
  </Box>
);

const ErrorFallback = ({ error }) => (
  <Box
    display="flex"
    flexDirection="column"
    alignItems="center"
    justifyContent="center"
    minHeight="100vh"
    p={3}
    bgcolor="background.default"
    color="error.main"
  >
    <h2>Une erreur est survenue</h2>
    <pre>{error.message}</pre>
  </Box>
);

function App() {
  return (
    <React.StrictMode>
      <ErrorBoundary FallbackComponent={ErrorFallback}>
        <ThemeProvider theme={casysTheme}>
          <CssBaseline />
          <AuthProvider>
            <RouterProvider
              router={router}
              hydrationData={window.__INITIAL_DATA__}
              HydrateFallback={LoadingFallback}
            />
          </AuthProvider>
        </ThemeProvider>
      </ErrorBoundary>
    </React.StrictMode>
  );
}

// Initialize React with development checks
let root;

// Ensure we only create root once
if (!window.__ROOT__) {
  const container = document.getElementById("root");
  root = ReactDOM.createRoot(container);
  window.__ROOT__ = root;
} else {
  root = window.__ROOT__;
}

root.render(<App />);

// Enable React Router v7 features gradually
if (import.meta.env.DEV) {
  console.log("React Router v7 features are being enabled gradually");
}
