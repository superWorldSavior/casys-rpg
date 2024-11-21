import React from 'react';
import { RouterProvider } from 'react-router-dom';
import { ThemeProvider } from '@mui/material';
import ErrorBoundary from './components/common/ErrorBoundary';
import { casysTheme } from './theme/casysTheme';
import { AuthProvider } from './context/AuthContext';
import { router } from './router/config';

function App() {
  return (
    <ThemeProvider theme={casysTheme}>
      <AuthProvider>
        <ErrorBoundary fallbackMessage="An error occurred in the application">
          <RouterProvider 
            router={router}
            fallbackElement={
              <Container sx={{ 
                mt: 4, 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center' 
              }}>
                <CircularProgress />
              </Container>
            }
          />
        </ErrorBoundary>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
