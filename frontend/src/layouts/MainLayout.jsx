import React, { Suspense } from 'react';
import { Link, Outlet } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Container, Button, Box, CircularProgress } from '@mui/material';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import BottomNav from '../components/navigation/BottomNav';

const MainLayout = () => {
  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Box display="flex" alignItems="center" sx={{ flexGrow: 1 }}>
            <MenuBookIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography 
              variant="h6" 
              component={Link} 
              to="/" 
              sx={{ 
                textDecoration: 'none', 
                color: 'text.primary',
                fontWeight: 600,
                '&:hover': {
                  color: 'primary.main',
                }
              }}
            >
              Casys.AI
            </Typography>
          </Box>
          <Button 
            color="primary" 
            component={Link} 
            to="/library"
            sx={{
              fontWeight: 500,
              display: { xs: 'none', sm: 'block' },
              '&:hover': {
                backgroundColor: 'primary.light',
              }
            }}
          >
            Bibliothèque
          </Button>
        </Toolbar>
      </AppBar>
      <Container 
        maxWidth="xl" 
        sx={{ 
          mt: 4,
          minHeight: 'calc(100vh - 64px)',
          backgroundColor: 'background.default',
          py: 3,
          pb: { xs: 9, sm: 3 }, // Increased bottom padding for mobile to prevent content from being hidden behind the navigation bar
          overflowX: 'hidden' // Prevent horizontal scrolling
        }}
      >
        <Suspense fallback={<Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
          <CircularProgress />
        </Box>}>
          <Outlet />
        </Suspense>
      </Container>
      <BottomNav />
    </>
  );
};

export default MainLayout;
