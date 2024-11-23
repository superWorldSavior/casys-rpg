import React, { StrictMode } from 'react';
import { RouterProvider } from 'react-router-dom';
import { ThemeProvider } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import router from './router/routes';
import { casysTheme } from './theme/casysTheme';
import { AuthProvider } from './contexts/AuthContext';
import { FeedbackProvider } from './contexts/FeedbackContext';

function App() {
  return (
    <StrictMode>
      <ThemeProvider theme={casysTheme}>
        <CssBaseline />
        <FeedbackProvider>
          <AuthProvider>
            <RouterProvider 
              router={router}
              future={{
                v7_startTransition: true
              }} 
            />
          </AuthProvider>
        </FeedbackProvider>
      </ThemeProvider>
    </StrictMode>
  );
}

export default App;
