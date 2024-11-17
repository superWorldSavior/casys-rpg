import React from 'react';
import { Link, Outlet } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Container, Button, Box } from '@mui/material';
import MenuBookIcon from '@mui/icons-material/MenuBook';

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
              Casys.AI Reader
            </Typography>
          </Box>
          <Button 
            color="primary" 
            component={Link} 
            to="/"
            sx={{
              fontWeight: 500,
              '&:hover': {
                backgroundColor: 'primary.light',
              }
            }}
          >
            Library
          </Button>
        </Toolbar>
      </AppBar>
      <Container 
        maxWidth="xl" 
        sx={{ 
          mt: 4,
          minHeight: 'calc(100vh - 64px)',
          backgroundColor: 'background.default',
          py: 3
        }}
      >
        <Outlet />
      </Container>
    </>
  );
};

export default MainLayout;
