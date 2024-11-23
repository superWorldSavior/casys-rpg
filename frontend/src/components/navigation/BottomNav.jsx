import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Paper, BottomNavigation, BottomNavigationAction, Box } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import HomeIcon from '@mui/icons-material/Home';
import LibraryBooksIcon from '@mui/icons-material/LibraryBooks';
import ExploreIcon from '@mui/icons-material/Explore';
import PersonIcon from '@mui/icons-material/Person';

const BottomNav = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [value, setValue] = useState(() => {
    const path = location.pathname;
    return path === '/' || path === '/home' ? '/home' : path;
  });
  const [isPressed, setIsPressed] = useState(false);

  const handleChange = (event, newValue) => {
    setIsPressed(true);
    setValue(newValue);
    navigate(newValue);
    setTimeout(() => setIsPressed(false), 200);
  };

  useEffect(() => {
    const path = location.pathname;
    setValue(path === '/' ? '/home' : path);
  }, [location]);

  return (
    <AnimatePresence>
      <motion.div
        initial={{ y: 100 }}
        animate={{ y: 0 }}
        transition={{ type: "spring", stiffness: 260, damping: 20 }}
      >
        <Paper 
          component={motion.div}
          whileHover={{ y: -2 }}
          sx={{ 
            position: 'fixed', 
            bottom: 0, 
            left: 0, 
            right: 0,
            display: { xs: 'block', sm: 'none' },
            zIndex: 1000,
            borderRadius: '12px 12px 0 0',
            overflow: 'hidden'
          }} 
          elevation={3}
        >
          <BottomNavigation 
            value={value} 
            onChange={handleChange}
            sx={{
              bgcolor: 'background.paper',
              '& .MuiBottomNavigationAction-root': {
                minWidth: 'auto',
                padding: '6px 0',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&.Mui-selected': {
                  '& .MuiSvgIcon-root': {
                    transform: 'scale(1.1)',
                    transition: 'transform 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
                  }
                },
                '&:active': {
                  '& .MuiSvgIcon-root': {
                    transform: 'scale(0.9)',
                  }
                }
              }
            }}
          >
            {[
              { label: "Accueil", value: "/home", icon: <HomeIcon /> },
              { label: "Bibliothèque", value: "/library", icon: <LibraryBooksIcon /> },
              { label: "Parcourir", value: "/browse", icon: <ExploreIcon /> },
              { label: "Profil", value: "/profile", icon: <PersonIcon /> }
            ].map((item) => (
              <BottomNavigationAction
                key={item.value}
                label={item.label}
                value={item.value}
                icon={
                  <Box
                    component={motion.div}
                    animate={{
                      scale: value === item.value ? 1.1 : 1,
                      y: value === item.value ? -4 : 0
                    }}
                    whileTap={{ scale: 0.9 }}
                    transition={{ duration: 0.2 }}
                  >
                    {item.icon}
                  </Box>
                }
                sx={{
                  color: value === item.value ? 'primary.main' : 'text.secondary',
                  '& .MuiBottomNavigationAction-label': {
                    transition: 'all 0.2s',
                    fontSize: value === item.value ? '0.75rem' : '0.7rem',
                    fontWeight: value === item.value ? 600 : 400
                  }
                }}
              />
            ))}
          </BottomNavigation>
        </Paper>
      </motion.div>
    </AnimatePresence>
  );
};

export default BottomNav;
