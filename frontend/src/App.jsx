import React, { StrictMode } from 'react';
import { RouterProvider } from 'react-router-dom';
import { ThemeProvider } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import { router } from './router/routes';
import { casysTheme } from './theme/casysTheme';
import { AuthProvider } from './contexts/AuthContext';

function App() {
  return (
    <StrictMode>
      <ThemeProvider theme={casysTheme}>
        <CssBaseline />
        <AuthProvider>
          <RouterProvider router={router} fallbackElement={<div>Chargement...</div>} />
        </AuthProvider>
      </ThemeProvider>
    </StrictMode>
  );
}

export default App;
