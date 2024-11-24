import React from 'react';
import { HexColorPicker } from 'react-colorful';
import { Box, Card, CardContent } from '@mui/material';

const FONT_FAMILIES = [
  { name: 'Default', value: 'var(--bs-body-font-family)' },
  { name: 'Serif', value: 'Georgia, serif' },
  { name: 'Monospace', value: 'monospace' },
  { name: 'Sans-serif', value: 'Arial, sans-serif' }
];

const FONT_SIZES = [
  { name: 'Small', value: '0.9rem' },
  { name: 'Medium', value: '1rem' },
  { name: 'Large', value: '1.2rem' },
  { name: 'Extra Large', value: '1.4rem' }
];

function ThemeControl({ theme, onThemeChange }) {
  return (
    <Box className="theme-control" sx={{ mb: 3 }}>
      <Card>
        <CardContent>
          <Box
            component="h2"
            sx={{
              fontSize: '1.25rem',
              fontWeight: 500,
              mb: 2,
              color: 'inherit'
            }}
          >
            Theme Settings
          </Box>
          
          <div className="mb-3">
            <label className="form-label">Font Family</label>
            <select 
              className="form-select"
              value={theme.fontFamily}
              onChange={(e) => onThemeChange({ ...theme, fontFamily: e.target.value })}
            >
              {FONT_FAMILIES.map(font => (
                <option key={font.name} value={font.value}>
                  {font.name}
                </option>
              ))}
            </select>
          </div>

          <div className="mb-3">
            <label className="form-label">Font Size</label>
            <select 
              className="form-select"
              value={theme.fontSize}
              onChange={(e) => onThemeChange({ ...theme, fontSize: e.target.value })}
            >
              {FONT_SIZES.map(size => (
                <option key={size.name} value={size.value}>
                  {size.name}
                </option>
              ))}
            </select>
          </div>

          <div className="mb-3">
            <label className="form-label">Text Color</label>
            <HexColorPicker 
              color={theme.textColor} 
              onChange={(color) => onThemeChange({ ...theme, textColor: color })}
              style={{ width: '100%', height: '150px' }}
            />
          </div>

          <div className="mb-3">
            <label className="form-label">Line Height</label>
            <input 
              type="range" 
              className="form-range"
              min="1"
              max="2"
              step="0.1"
              value={theme.lineHeight}
              onChange={(e) => onThemeChange({ ...theme, lineHeight: e.target.value })}
            />
          </div>
        </CardContent>
      </Card>
    </Box>
  );
}

export default ThemeControl;
