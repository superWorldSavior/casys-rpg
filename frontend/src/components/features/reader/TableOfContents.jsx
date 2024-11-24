import React from 'react';
import { Box, List, ListItem, ListItemButton, ListItemText, Typography, Drawer } from '@mui/material';
import MenuBookIcon from '@mui/icons-material/MenuBook';

function TableOfContents({ chapters, currentSection, onChapterSelect, open, onClose }) {
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
          <MenuBookIcon /> Table des matières
        </Typography>
        <List>
          {chapters.map((chapter, index) => (
            <ListItem key={index} disablePadding>
              <ListItemButton
                selected={currentSection === index}
                onClick={() => {
                  onChapterSelect(index);
                  onClose();
                }}
              >
                <ListItemText 
                  primary={`Chapitre ${index + 1}`}
                  secondary={chapter.substring(0, 50) + '...'}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Box>
    </Drawer>
  );
}

export default TableOfContents;
