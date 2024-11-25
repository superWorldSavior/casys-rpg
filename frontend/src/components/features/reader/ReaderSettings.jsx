import React from 'react';
import { Box, Drawer, IconButton, Typography, Divider, Slider, Button, ButtonGroup } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import FormatSizeIcon from '@mui/icons-material/FormatSize';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import SpeedControl from './SpeedControl';
import ThemeControl from './ThemeControl';

const FONT_SIZES = {
  small: '1rem',
  medium: '1.2rem',
  large: '1.4rem',
};

const THEMES = {
  light: {
    name: 'Jour',
    backgroundColor: '#F6F3E9',
    textColor: '#2c2c2c',
  },
  sepia: {
    name: 'Sépia',
    backgroundColor: '#F4ECD8',
    textColor: '#5C4B37',
  },
  dark: {
    name: 'Nuit',
    backgroundColor: '#131516',
    textColor: '#e1e1e1',
  },
  warmLight: {
    name: 'Lumière chaude',
    backgroundColor: '#FCF8E8',
    textColor: '#4A4A4A',
  },
  green: {
    name: 'Vert doux',
    backgroundColor: '#E8F3E8',
    textColor: '#2C3E2C',
  }
};

const FONTS = {
  bookerly: '"Bookerly", "Georgia", serif',
  helvetica: '"Helvetica Neue", "Arial", sans-serif',
  palatino: '"Palatino", "Times New Roman", serif',
  openDyslexic: '"OpenDyslexic", sans-serif',
  georgia: '"Georgia", serif',
};

const LINE_HEIGHTS = {
  compact: '1.5',
  comfortable: '1.8',
  relaxed: '2.0',
};

const MARGINS = {
  narrow: '1rem',
  medium: '2rem',
  wide: '3rem',
};

const ReaderSettings = ({ 
  open, 
  onClose, 
  speed, 
  onSpeedChange, 
  theme, 
  onThemeChange,
  onExitReader
}) => {
  const currentTheme = theme || THEMES.light;
  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      sx={{
        '& .MuiDrawer-paper': {
          width: { xs: '100%', sm: 400 },
          p: 3,
        },
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Paramètres de lecture</Typography>
        <IconButton onClick={onClose}>
          <CloseIcon />
        </IconButton>
      </Box>

      <Divider sx={{ mb: 3 }} />

      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" gutterBottom>
          Taille du texte
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <FormatSizeIcon sx={{ fontSize: '1rem' }} />
          <Slider
            value={parseInt(currentTheme?.fontSize || '16px') || 16}
            min={14}
            max={24}
            step={1}
            onChange={(_, value) => onThemeChange('fontSize', `${value}px`)}
            sx={{ flexGrow: 1 }}
            marks={[
              { value: 14, label: 'A' },
              { value: 19, label: 'A' },
              { value: 24, label: 'A' },
            ]}
          />
          <FormatSizeIcon sx={{ fontSize: '1.5rem' }} />
        </Box>
      </Box>

      <Divider sx={{ my: 3 }} />

      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" gutterBottom>
          Vitesse de défilement
        </Typography>
        <SpeedControl speed={speed} setSpeed={onSpeedChange} />
      </Box>

      <Divider sx={{ my: 3 }} />

      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" gutterBottom>
          Thème
        </Typography>
        <ButtonGroup variant="outlined" fullWidth>
          {Object.entries(THEMES).map(([key, value]) => (
            <Button
              key={key}
              onClick={() => onThemeChange('theme', value)}
              variant={currentTheme.backgroundColor === value.backgroundColor ? 'contained' : 'outlined'}
              startIcon={key === 'dark' ? <Brightness4Icon /> : <Brightness7Icon />}
              sx={{
                bgcolor: value.backgroundColor,
                color: value.textColor,
                '&:hover': {
                  bgcolor: value.backgroundColor,
                  opacity: 0.9,
                },
              }}
            >
              {value.name}
            </Button>
          ))}
        </ButtonGroup>
      </Box>
    </Drawer>
  );
};

export default ReaderSettings;
