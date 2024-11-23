import React from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { ThemeProvider } from '@mui/material';
import { Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { casysTheme } from './theme/casysTheme';
import LoginPage from './pages/Auth/LoginPage';
import HomePage from './pages/Home';
import ReaderPage from './pages/Reader';
import { ProtectedRoute } from './router/ProtectedRoute';

const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/login" replace />
  },
  {
    path: '/login',
    element: <LoginPage />
  },
  {
    path: '/home',
    element: <ProtectedRoute><HomePage /></ProtectedRoute>
  },
  {
    path: '/reader/:bookId',
    element: <ProtectedRoute><ReaderPage /></ProtectedRoute>
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
