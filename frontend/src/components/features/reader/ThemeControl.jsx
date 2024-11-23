import React from 'react';
import { Box, FormControl, InputLabel, Select, MenuItem, TextField } from '@mui/material';
import PaletteIcon from '@mui/icons-material/Palette';

function ThemeControl({ theme, onThemeChange }) {
  const handleChange = (property, value) => {
    onThemeChange({ ...theme, [property]: value });
  };

  return (
    <Box sx={{ mt: 2 }}>
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel>Font Family</InputLabel>
        <Select
          value={theme.fontFamily}
          label="Font Family"
          onChange={(e) => handleChange('fontFamily', e.target.value)}
        >
          <MenuItem value="Arial">Arial</MenuItem>
          <MenuItem value="Times New Roman">Times New Roman</MenuItem>
          <MenuItem value="Courier New">Courier New</MenuItem>
          <MenuItem value="Georgia">Georgia</MenuItem>
          <MenuItem value="Verdana">Verdana</MenuItem>
        </Select>
      </FormControl>

      <FormControl fullWidth sx={{ mb: 2 }}>
        <TextField
          label="Font Size"
          type="text"
          value={theme.fontSize}
          onChange={(e) => handleChange('fontSize', e.target.value)}
          placeholder="e.g., 1rem, 16px"
        />
      </FormControl>

      <FormControl fullWidth sx={{ mb: 2 }}>
        <TextField
          label="Line Height"
          type="text"
          value={theme.lineHeight}
          onChange={(e) => handleChange('lineHeight', e.target.value)}
          placeholder="e.g., 1.5, 24px"
        />
      </FormControl>

      <FormControl fullWidth>
        <TextField
          label="Text Color"
          type="color"
          value={theme.textColor}
          onChange={(e) => handleChange('textColor', e.target.value)}
          sx={{ '& input': { height: '50px' } }}
        />
      </FormControl>
    </Box>
  );
}

export default ThemeControl;
