import React from 'react';
import { RouterProvider } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { router } from './router/routes';
import { casysTheme } from './theme/casysTheme';
import { AuthProvider } from './contexts/AuthContext';

function App() {
  return (
    <React.StrictMode>
      <ThemeProvider theme={casysTheme}>
        <CssBaseline />
        <AuthProvider>
          <RouterProvider router={router} />
        </AuthProvider>
      </ThemeProvider>
    </React.StrictMode>
  );
}

export default App;
