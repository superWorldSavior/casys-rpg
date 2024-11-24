import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useInView } from 'react-intersection-observer';
import { useParams } from 'react-router-dom';
import { Box, LinearProgress, IconButton, useTheme } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import TextDisplay from '../../components/features/reader/TextDisplay';
import NavigationControls from '../../components/features/reader/NavigationControls';
import CommandInput from '../../components/features/reader/CommandInput';
import SpeedControl from '../../components/features/reader/SpeedControl';
import ThemeControl from '../../components/features/reader/ThemeControl';
import TableOfContents from '../../components/features/reader/TableOfContents';
import { storageService } from '../../services/storage';

import { Box, IconButton, LinearProgress } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import { useInView } from 'react-intersection-observer';

const DEFAULT_THEME = {
  fontFamily: 'var(--bs-body-font-family)',
  fontSize: '1rem',
  textColor: '#ffffff',
  lineHeight: '1.6'
};

function ReaderPage() {
  const [tocOpen, setTocOpen] = useState(false);
  const [readingProgress, setReadingProgress] = useState(0);
  const { bookId } = useParams();
  const [currentSection, setCurrentSection] = useState(-1);
  const [isPaused, setIsPaused] = useState(true);
  const [speed, setSpeed] = useState(5);
  const [textContent, setTextContent] = useState([]);
  const [theme, setTheme] = useState(DEFAULT_THEME);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchContent = async () => {
      try {
        const chapters = await storageService.getAllChapters();
        if (chapters && chapters.length > 0) {
          const content = await Promise.all(
            chapters.map(key => storageService.getChapter(key))
          );
          setTextContent(content);
        } else {
          const response = await fetch(`/api/books/${bookId}/content`);
          const data = await response.json();
          if (response.ok) {
            await Promise.all(
              data.map((content, index) => 
                storageService.saveChapter(`book_${bookId}_chapter_${index + 1}`, content)
              )
            );
            setTextContent(data);
          } else {
            setError('Error loading book content');
          }
        }

        const savedTheme = await storageService.getChapter('user_theme');
        if (savedTheme) {
          setTheme(savedTheme);
        }
      } catch (error) {
        console.error('Error fetching content:', error);
        setError('Error loading book content');
      }
    };

    if (bookId) {
      fetchContent();
    }
  }, [bookId]);

  useEffect(() => {
    storageService.saveChapter('user_theme', theme);
  }, [theme]);

  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        {error}
      </div>
    );
  }

  const { ref: loadMoreRef, inView } = useInView({
    threshold: 0.5,
    triggerOnce: false
  });

  const debouncedScroll = useCallback((e) => {
    if (e.target.scrollTop === 0) {
      // At the top - load previous content if available
      if (currentSection > 0) {
        setCurrentSection(prev => prev - 1);
      }
    }
  }, [currentSection]);

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ 
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 1000,
        bgcolor: 'background.paper',
        borderBottom: 1,
        borderColor: 'divider',
        px: 2,
        py: 1,
        display: 'flex',
        alignItems: 'center',
        gap: 2
      }}>
        <IconButton onClick={() => setTocOpen(true)}>
          <MenuIcon />
        </IconButton>
        <LinearProgress 
          variant="determinate" 
          value={readingProgress} 
          sx={{ flexGrow: 1 }}
        />
      </Box>

      <TableOfContents
        chapters={textContent}
        currentSection={currentSection}
        onChapterSelect={setCurrentSection}
        open={tocOpen}
        onClose={() => setTocOpen(false)}
      />

      <Box sx={{ 
        flexGrow: 1, 
        overflow: 'auto',
        mt: '64px',
        px: 2,
        py: 1,
               }}>
        <Box 
          component="main"
          sx={{
            height: '100%',
            overflowY: 'auto',
            WebkitOverflowScrolling: 'touch'
          }}
          onScroll={debouncedScroll}
        >
            <TextDisplay
              textContent={textContent}
              currentSection={currentSection}
              speed={speed}
              theme={theme}
              onProgressChange={setReadingProgress}
            />
            <NavigationControls
              currentSection={currentSection}
              setCurrentSection={setCurrentSection}
              totalSections={textContent.length}
              isPaused={isPaused}
              setIsPaused={setIsPaused}
            />
            <SpeedControl speed={speed} setSpeed={setSpeed} />
            <ThemeControl theme={theme} onThemeChange={setTheme} />
            <CommandInput
              onCommand={(command) => {
                switch (command) {
                  case 'commencer':
                    setCurrentSection(0);
                    setIsPaused(false);
                    break;
                  case 'pause':
                    setIsPaused(true);
                    break;
                  case 'resume':
                    setIsPaused(false);
                    break;
                  case 'skip':
                    if (currentSection < textContent.length - 1) {
                      setCurrentSection(prev => prev + 1);
                    }
                    break;
                  case 'help':
                    alert(`Available commands:
- commencer: Start reading
- pause: Pause reading
- resume: Resume reading
- skip: Skip to next section
- help: Show this help message`);
                    break;
                }
              }}
            />
          </Box>
      </Box>
    </Box>
  );
}

export default ReaderPage;
