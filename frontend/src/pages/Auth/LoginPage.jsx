import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  Box,
  Button,
  Container,
  TextField,
  Typography,
  Paper,
  useTheme,
  useMediaQuery,
  CircularProgress,
  Alert,
  IconButton,
  InputAdornment,
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';

const LoginPage = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const navigate = useNavigate();
  const { login } = useAuth();
  
  const [credentials, setCredentials] = useState({
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setCredentials(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // TODO: Implement actual login logic with API
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
      const userData = { id: '1', email: credentials.email, username: 'User' };
      await login(userData);
      navigate('/home');
    } catch (error) {
      setError('Identifiants invalides. Veuillez réessayer.');
      console.error('Login failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <Container 
      component="main" 
      maxWidth="xs" 
      sx={{ 
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: isMobile ? 2 : 3
      }}
    >
      <Paper 
        elevation={3} 
        sx={{ 
          p: isMobile ? 3 : 4,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          width: '100%',
          borderRadius: isMobile ? 2 : 3,
          position: 'relative'
        }}
      >
        <Typography 
          component="h1" 
          variant={isMobile ? "h5" : "h4"} 
          sx={{ 
            mb: 3,
            fontWeight: 600,
            color: theme.palette.primary.main
          }}
        >
          Connexion
        </Typography>

        {error && (
          <Alert severity="error" sx={{ width: '100%', mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box 
          component="form" 
          onSubmit={handleSubmit} 
          sx={{ 
            width: '100%',
            mt: 1
          }}
        >
          <TextField
            margin="normal"
            required
            fullWidth
            id="email"
            label="Email"
            name="email"
            autoComplete="email"
            autoFocus
            value={credentials.email}
            onChange={handleChange}
            disabled={loading}
            sx={{ 
              mb: 2,
              '& .MuiOutlinedInput-root': {
                borderRadius: theme.shape.borderRadius
              }
            }}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="Mot de passe"
            type={showPassword ? 'text' : 'password'}
            id="password"
            autoComplete="current-password"
            value={credentials.password}
            onChange={handleChange}
            disabled={loading}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle password visibility"
                    onClick={togglePasswordVisibility}
                    edge="end"
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
            sx={{ 
              mb: 3,
              '& .MuiOutlinedInput-root': {
                borderRadius: theme.shape.borderRadius
              }
            }}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            disabled={loading}
            sx={{ 
              mb: 2,
              py: 1.5,
              position: 'relative',
              borderRadius: theme.shape.borderRadius
            }}
          >
            {loading ? (
              <CircularProgress 
                size={24}
                sx={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  marginTop: '-12px',
                  marginLeft: '-12px',
                }}
              />
            ) : 'Se connecter'}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default LoginPage;
