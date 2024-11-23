import { createTheme } from '@mui/material/styles';

export const casysTheme = createTheme({
  palette: {
    primary: {
      main: '#6200EE',
      light: '#7F39FB',
      dark: '#4B0082',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#343A40',
      light: '#4B545C',
      dark: '#23272B',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#FFFFFF',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#000000',
      secondary: '#343A40',
    },
  },
  typography: {
    fontFamily: "'Arial', 'Helvetica', sans-serif",
    h1: {
      fontWeight: 700,
      fontSize: '2.5rem',
      color: '#343A40',
      marginBottom: '1rem',
    },
    h2: {
      fontWeight: 600,
      fontSize: '2rem',
      color: '#343A40',
      marginBottom: '0.875rem',
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.75rem',
      color: '#343A40',
      marginBottom: '0.75rem',
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.5rem',
      color: '#343A40',
      marginBottom: '0.625rem',
    },
    h5: {
      fontWeight: 500,
      fontSize: '1.25rem',
      color: '#343A40',
      marginBottom: '0.5rem',
    },
    h6: {
      fontWeight: 500,
      fontSize: '1rem',
      color: '#343A40',
      marginBottom: '0.5rem',
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
    button: {
      textTransform: 'none',
      fontWeight: 500,
    },
  },
  spacing: 8,
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '8px 24px',
          fontWeight: 500,
        },
        contained: {
          backgroundColor: '#6200EE',
          '&:hover': {
            backgroundColor: '#4B0082',
          },
          boxShadow: 'none',
        },
        outlined: {
          borderColor: '#6200EE',
          color: '#6200EE',
          '&:hover': {
            borderColor: '#4B0082',
            color: '#4B0082',
            backgroundColor: 'rgba(98, 0, 238, 0.04)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: '#FFFFFF',
          borderRadius: 12,
          boxShadow: '0px 2px 8px rgba(0, 0, 0, 0.1)',
          padding: '24px',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#FFFFFF',
          color: '#000000',
          boxShadow: '0px 1px 4px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiContainer: {
      styleOverrides: {
        root: {
          backgroundColor: '#FFFFFF',
          padding: '24px',
        },
      },
    },
  },
});
