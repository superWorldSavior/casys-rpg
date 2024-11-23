import React, { Suspense } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Container, Button, Box, CircularProgress, ButtonBase } from '@mui/material';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import BottomNav from '../components/navigation/BottomNav';
import { motion, AnimatePresence } from 'framer-motion';

const MainLayout = () => {
  const location = useLocation();
  const [isLoading, setIsLoading] = React.useState(false);
  const [feedbackMessage, setFeedbackMessage] = React.useState('');

  React.useEffect(() => {
    setIsLoading(true);
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 300);
    return () => clearTimeout(timer);
  }, [location.pathname]);

  return (
    <>
      <AppBar 
        position="static"
        component={motion.div}
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
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
          <ButtonBase 
            component={Link} 
            to="/library"
            sx={{
              fontWeight: 500,
              display: { xs: 'none', sm: 'block' },
              padding: '8px 16px',
              borderRadius: 1,
              color: 'primary.main',
              transition: 'all 0.2s ease-in-out',
              position: 'relative',
              overflow: 'hidden',
              '&:hover': {
                backgroundColor: 'primary.light',
                transform: 'translateY(-2px)',
              },
              '&:active': {
                transform: 'translateY(0)',
              },
              '&::after': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                background: 'radial-gradient(circle, rgba(255,255,255,0.7) 0%, rgba(255,255,255,0) 100%)',
                opacity: 0,
                transition: 'opacity 0.3s ease-in-out',
              },
              '&:active::after': {
                opacity: 1,
                animation: 'ripple 0.6s ease-out',
              }
            }}
          >
            Bibliothèque
          </ButtonBase>
        </Toolbar>
      </AppBar>
      <Container 
        component={motion.div}
        maxWidth="xl" 
        sx={{ 
          mt: 4,
          minHeight: 'calc(100vh - 64px)',
          backgroundColor: 'background.default',
          py: 3,
          pb: { xs: 9, sm: 3 },
          overflowX: 'hidden'
        }}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        whileHover={{ scale: 1.005 }}
        transition={{ 
          duration: 0.3,
          type: "spring",
          stiffness: 300,
          damping: 20
        }}
      >
        <Suspense fallback={
          <Box 
            component={motion.div}
            display="flex" 
            justifyContent="center" 
            alignItems="center" 
            minHeight="200px"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.2 }}
          >
            <CircularProgress />
          </Box>
        }>
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 20 }}
              animate={{ 
                opacity: 1, 
                y: 0,
                transition: {
                  duration: 0.3,
                  type: "spring",
                  stiffness: 300,
                  damping: 25
                }
              }}
              exit={{ 
                opacity: 0, 
                y: -20,
                transition: {
                  duration: 0.2
                }
              }}
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </Suspense>
      </Container>
      <BottomNav />
    </>
  );
};

export default MainLayout;
