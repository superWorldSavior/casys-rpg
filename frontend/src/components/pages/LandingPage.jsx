import React from 'react';
import { Link } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  Typography,
  Grid,
  Paper,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import LoginIcon from '@mui/icons-material/Login';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import AutoStoriesIcon from '@mui/icons-material/AutoStories';
import PsychologyIcon from '@mui/icons-material/Psychology';
import { useAuth } from '../../context/AuthContext';

const DecorativeBox = styled(Box)(({ theme }) => ({
  position: 'relative',
  overflow: 'hidden',
  borderRadius: theme.shape.borderRadius * 2,
  background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
  padding: theme.spacing(2),
  color: theme.palette.primary.contrastText,
  transition: 'transform 0.3s ease-in-out',
  '&:hover': {
    transform: 'translateY(-5px)',
  },
}));

const LandingPage = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { user } = useAuth();

  const features = [
    {
      icon: <AutoStoriesIcon fontSize="large" />,
      title: 'Interactive Reading',
      description: 'Immerse yourself in solo RPG adventures with dynamic storytelling.',
    },
    {
      icon: <PsychologyIcon fontSize="large" />,
      title: 'AI Narration',
      description: 'Experience adaptive storytelling powered by advanced AI technology.',
    },
  ];

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        background: theme.palette.background.default,
      }}
    >
      <Container maxWidth="lg" sx={{ mt: { xs: 4, sm: 8 }, mb: 4 }}>
        <Grid container spacing={4} alignItems="center">
          <Grid item xs={12} md={6}>
            <Typography
              variant={isMobile ? 'h3' : 'h2'}
              component="h1"
              gutterBottom
              sx={{
                fontWeight: 'bold',
                background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                backgroundClip: 'text',
                textFillColor: 'transparent',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Welcome to Casys.AI
            </Typography>
            <Typography variant="h5" color="text.secondary" paragraph>
              Your Personal AI-Powered Solo RPG Adventure Companion
            </Typography>
            
            {!user && (
              <Box sx={{ mt: 4, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  component={Link}
                  to="/login"
                  variant="contained"
                  size="large"
                  startIcon={<LoginIcon />}
                  sx={{ minWidth: 200 }}
                >
                  Login
                </Button>
                <Button
                  component={Link}
                  to="/register"
                  variant="outlined"
                  size="large"
                  startIcon={<PersonAddIcon />}
                  sx={{ minWidth: 200 }}
                >
                  Register
                </Button>
              </Box>
            )}
            
            {user && (
              <Button
                component={Link}
                to="/library"
                variant="contained"
                size="large"
                sx={{ mt: 4, minWidth: 200 }}
              >
                Go to Library
              </Button>
            )}
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Grid container spacing={2}>
              {features.map((feature, index) => (
                <Grid item xs={12} sm={6} key={index}>
                  <DecorativeBox>
                    <Box sx={{ mb: 2 }}>
                      {feature.icon}
                    </Box>
                    <Typography variant="h6" gutterBottom>
                      {feature.title}
                    </Typography>
                    <Typography variant="body2">
                      {feature.description}
                    </Typography>
                  </DecorativeBox>
                </Grid>
              ))}
            </Grid>
          </Grid>
        </Grid>

        <Paper 
          elevation={3}
          sx={{ 
            mt: 8, 
            p: 4, 
            borderRadius: 2,
            background: `linear-gradient(135deg, ${theme.palette.background.paper} 0%, ${theme.palette.background.default} 100%)`,
          }}
        >
          <Typography variant="h4" gutterBottom align="center">
            How It Works
          </Typography>
          <Grid container spacing={4} sx={{ mt: 2 }}>
            {['Choose Your Adventure', 'Let AI Guide You', 'Make Decisions', 'Shape Your Story'].map((step, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography
                    variant="h2"
                    sx={{
                      color: theme.palette.primary.main,
                      opacity: 0.5,
                      fontWeight: 'bold',
                    }}
                  >
                    {index + 1}
                  </Typography>
                  <Typography variant="h6" gutterBottom>
                    {step}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Paper>
      </Container>
    </Box>
  );
};

export default LandingPage;
