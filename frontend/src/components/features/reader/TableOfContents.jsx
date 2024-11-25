import React from 'react';
import { Box, List, ListItem, ListItemButton, ListItemText, Typography, Drawer, Divider, ListItemIcon } from '@mui/material';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import SettingsIcon from '@mui/icons-material/Settings';
import LogoutIcon from '@mui/icons-material/Logout';

function TableOfContents({ chapters, currentSection, onChapterSelect, open, onClose, onSettingsClick, onExitReader }) {
  return (
    <Drawer
      anchor="left"
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: {
          width: 280,
          bgcolor: 'background.default',
          color: 'text.primary',
        },
      }}
    >
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <MenuBookIcon /> Feuille d'aventure
        </Typography>
        <List>
          <ListItem disablePadding>
            <ListItemButton onClick={onSettingsClick}>
              <ListItemIcon sx={{ color: 'text.primary' }}>
                <SettingsIcon />
              </ListItemIcon>
              <ListItemText primary="Paramètres" />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={onExitReader}>
              <ListItemIcon sx={{ color: 'text.primary' }}>
                <LogoutIcon />
              </ListItemIcon>
              <ListItemText primary="Quitter" />
            </ListItemButton>
          </ListItem>
        </List>
      </Box>
    </Drawer>
  );
}

export default TableOfContents;
