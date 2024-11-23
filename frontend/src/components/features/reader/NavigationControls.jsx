import React from 'react';
import { Button } from '@mui/material';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import NavigateBeforeIcon from '@mui/icons-material/NavigateBefore';
import PauseIcon from '@mui/icons-material/Pause';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

function NavigationControls({
  currentSection,
  setCurrentSection,
  totalSections,
  isPaused,
  setIsPaused
}) {
  return (
    <div className="controls mb-3">
      <div className="d-flex justify-content-between align-items-center">
        <Button
          variant="contained"
          onClick={() => setCurrentSection(prev => prev - 1)}
          disabled={currentSection <= 0}
          startIcon={<NavigateBeforeIcon />}
        >
          Previous
        </Button>
        <Button
          variant="contained"
          onClick={() => setIsPaused(prev => !prev)}
          startIcon={isPaused ? <PlayArrowIcon /> : <PauseIcon />}
        >
          {isPaused ? 'Resume' : 'Pause'}
        </Button>
        <Button
          variant="contained"
          onClick={() => setCurrentSection(prev => prev + 1)}
          disabled={currentSection >= totalSections - 1}
          endIcon={<NavigateNextIcon />}
        >
          Next
        </Button>
      </div>
    </div>
  );
}

export default NavigationControls;
