import React from 'react';
import { Box, Slider, Typography } from '@mui/material';
import SpeedIcon from '@mui/icons-material/Speed';

function SpeedControl({ speed, setSpeed }) {
  return (
    <Box sx={{ width: '100%', mt: 2 }}>
      <Typography gutterBottom variant="subtitle1" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <SpeedIcon /> Reading Speed
      </Typography>
      <Slider
        value={speed}
        min={1}
        max={10}
        step={1}
        marks
        onChange={(_, newValue) => setSpeed(newValue)}
        valueLabelDisplay="auto"
        aria-label="Reading speed"
      />
    </Box>
  );
}

export default SpeedControl;
