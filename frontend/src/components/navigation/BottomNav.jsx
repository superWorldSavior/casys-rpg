import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Paper, BottomNavigation, BottomNavigationAction } from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import LibraryBooksIcon from '@mui/icons-material/LibraryBooks';
import ExploreIcon from '@mui/icons-material/Explore';
import PersonIcon from '@mui/icons-material/Person';

const BottomNav = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [value, setValue] = React.useState(() => {
    const path = location.pathname;
    return path === '/' || path === '/home' ? '/home' : path;
  });

  const handleChange = (event, newValue) => {
    setValue(newValue);
    navigate(newValue);
  };

  return (
    <Paper 
      sx={{ 
        position: 'fixed', 
        bottom: 0, 
        left: 0, 
        right: 0,
        display: { xs: 'block', sm: 'none' },
        zIndex: 1000
      }} 
      elevation={3}
    >
      <BottomNavigation value={value} onChange={handleChange}>
        <BottomNavigationAction
          label="Accueil"
          value="/home"
          icon={<HomeIcon />}
        />
        <BottomNavigationAction
          label="Bibliothèque"
          value="/library"
          icon={<LibraryBooksIcon />}
        />
        <BottomNavigationAction
          label="Parcourir"
          value="/browse"
          icon={<ExploreIcon />}
        />
        <BottomNavigationAction
          label="Profil"
          value="/profile"
          icon={<PersonIcon />}
        />
      </BottomNavigation>
    </Paper>
  );
};

export default BottomNav;
