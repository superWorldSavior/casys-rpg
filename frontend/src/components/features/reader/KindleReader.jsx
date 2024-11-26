import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Box, Typography, LinearProgress, Button } from '@mui/material';
import ReaderSettings from './ReaderSettings';

const STORAGE_KEY = 'kindle-reader';
const DISPLAY_SPEED = {
  slow: 50,
  medium: 30,
  fast: 15
};

const calculateSpeed = (speedSetting) => {
  const normalizedSpeed = Math.min(Math.max(speedSetting, 1), 10);
  const baseSpeed = DISPLAY_SPEED.medium;
  const speedMultiplier = Math.pow(normalizedSpeed / 5, 1.5);
  return Math.round(baseSpeed / speedMultiplier);
};

const KindleReader = ({ 
  content = [], 
  initialSection = 0, 
  bookId,
  theme: customTheme,
  onProgressChange 
}) => {
  const [currentSection, setCurrentSection] = useState(initialSection);
  const [displayedText, setDisplayedText] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [streamSpeed, setStreamSpeed] = useState(5);
  const [isChapterEnd, setIsChapterEnd] = useState(false);
  const cancelStreamRef = useRef(false);
  const swipeRef = useRef(null); // Added swipeRef

  const normalizedContent = Array.isArray(content) ? content : [content];
  
  const [readerTheme, setReaderTheme] = useState({
    backgroundColor: customTheme?.backgroundColor || '#F6F3E9',
    textColor: customTheme?.textColor || '#2c2c2c',
    fontFamily: customTheme?.fontFamily || '"Bookerly", "Georgia", serif',
    fontSize: customTheme?.fontSize || '1.2rem',
    lineHeight: customTheme?.lineHeight || 1.8,
  });

  const streamText = useCallback(async (text) => {
    if (!text) {
      console.warn('No text provided for streaming');
      return;
    }
    
    const textContent = typeof text === 'string' ? text : text.content || '';
    const words = textContent.split(/\s+/);
    
    try {
      setIsStreaming(true);
      setError(null);
      setDisplayedText('');
      
      const displaySpeed = calculateSpeed(streamSpeed);
      let currentText = '';
      
      for (let i = 0; i < words.length; i++) {
        if (cancelStreamRef.current) {
          break;
        }
        
        currentText += (i > 0 ? ' ' : '') + words[i];
        setDisplayedText(currentText);
        setProgress((i + 1) / words.length * 100);
        
        if (onProgressChange) {
          onProgressChange((i + 1) / words.length * 100);
        }
        
        // Add natural pauses for punctuation
        const hasPunctuation = /[,.!?]$/.test(words[i]);
        await new Promise(resolve => setTimeout(resolve, hasPunctuation ? displaySpeed * 1.5 : displaySpeed));
      }
      
      setIsStreaming(false);
    } catch (err) {
      setError("Erreur lors de l'affichage du texte");
      console.error("Display error:", err);
      setIsStreaming(false);
    }
  }, [onProgressChange, streamSpeed]);

  const detectChapterEnd = useCallback((element) => {
    if (!element) return;
    
    const { scrollTop, scrollHeight, clientHeight } = element;
    const isNearBottom = scrollTop + clientHeight >= scrollHeight - 100;
    setIsChapterEnd(isNearBottom);
  }, []);

  const navigationHandlers = {
    keyboard: useCallback((e) => {
      if (isStreaming) return;
      
      if (e.key === 'ArrowRight' || e.key === 'Space') {
        if (currentSection < normalizedContent.length - 1) {
          setCurrentSection(prev => prev + 1);
        }
      } else if (e.key === 'ArrowLeft') {
        if (currentSection > 0) {
          setCurrentSection(prev => prev - 1);
        }
      }
    }, [currentSection, isStreaming, normalizedContent.length]),
  };

  const swipeHandlers = {
    onTouchStart: (e) => {
      const touch = e.touches[0];
      swipeRef.current = { x: touch.clientX };
    },
    onTouchMove: (e) => {
      if (!swipeRef.current || isStreaming) return;
      
      const touch = e.touches[0];
      const diff = swipeRef.current.x - touch.clientX;
      const container = document.querySelector('.kindle-reader-content');
      
      if (container) {
        // Add smooth transition during swipe
        container.style.transform = `translateX(${-diff}px)`;
        container.style.transition = 'transform 0.1s ease-out';
        
        if (Math.abs(diff) > 50) {
          if (diff > 0 && currentSection < normalizedContent.length - 1) {
            container.style.transform = 'translateX(-100%)';
            setTimeout(() => {
              setCurrentSection(prev => prev + 1);
              container.style.transform = 'translateX(0)';
            }, 300);
          } else if (diff < 0 && currentSection > 0) {
            container.style.transform = 'translateX(100%)';
            setTimeout(() => {
              setCurrentSection(prev => prev - 1);
              container.style.transform = 'translateX(0)';
            }, 300);
          }
          swipeRef.current = null;
        }
      }
    },
    onTouchEnd: () => {
      swipeRef.current = null;
    }
  };

  useEffect(() => {
    setIsLoading(normalizedContent.length === 0);
  }, [normalizedContent]);

  useEffect(() => {
    if (!bookId || currentSection === undefined) return;
    
    const readingState = {
      currentSection,
      progress,
      timestamp: Date.now(),
      theme: readerTheme,
      speed: streamSpeed
    };
    
    localStorage.setItem(
      `${STORAGE_KEY}-${bookId}`,
      JSON.stringify(readingState)
    );
    
    document.title = `Lecture en cours - ${Math.round(progress)}%`;
  }, [bookId, currentSection, progress, readerTheme, streamSpeed]);

  useEffect(() => {
    if (onProgressChange) {
      const overallProgress = ((currentSection * 100) + progress) / normalizedContent.length;
      onProgressChange(Math.min(overallProgress, 100));
    }
  }, [currentSection, progress, normalizedContent.length, onProgressChange]);

  useEffect(() => {
    if (!bookId) return;
    const saved = localStorage.getItem(`${STORAGE_KEY}-${bookId}`);
    if (saved) {
      const { currentSection: savedSection } = JSON.parse(saved);
      setCurrentSection(savedSection);
    }
  }, [bookId]);

  useEffect(() => {
    window.addEventListener('keydown', navigationHandlers.keyboard);
    return () => window.removeEventListener('keydown', navigationHandlers.keyboard);
  }, [navigationHandlers]);

  useEffect(() => {
    const initializeContent = async () => {
      if (!isLoading && normalizedContent.length > 0) {
        setError(null);
        setIsStreaming(false);
        
        const sectionToDisplay = initialSection >= 0 && initialSection < normalizedContent.length
          ? initialSection
          : currentSection;
        
        if (sectionToDisplay >= 0 && sectionToDisplay < normalizedContent.length) {
          const section = normalizedContent[sectionToDisplay];
          const content = typeof section === 'string' ? section : section?.content;
          
          if (content) {
            setProgress(0);
            cancelStreamRef.current = false;
            
            try {
              await streamText(content);
            } catch (err) {
              console.error('Error displaying text:', err);
              setError('Erreur lors de l\'affichage du texte');
              setDisplayedText(content);
            }
          } else {
            console.error('Invalid content format:', section);
            setError('Format de contenu invalide');
          }
        }
      }
    };

    initializeContent();

    return () => {
      cancelStreamRef.current = true;
    };
  }, [normalizedContent, currentSection, initialSection, streamText, isLoading]);

  if (!normalizedContent.length || isLoading) {
    return (
      <Box 
        display="flex" 
        flexDirection="column"
        justifyContent="center" 
        alignItems="center" 
        minHeight="100vh"
        bgcolor={readerTheme.backgroundColor}
        gap={2}
      >
        <Typography variant="h5" sx={{ color: readerTheme.textColor }}>
          Chargement du contenu...
        </Typography>
        {!normalizedContent.length && (
          <Typography variant="body2" sx={{ color: readerTheme.textColor }}>
            Veuillez patienter pendant le chargement de votre livre
          </Typography>
        )}
      </Box>
    );
  }

  if (error) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        minHeight="100vh"
        bgcolor={readerTheme.backgroundColor}
      >
        <Typography variant="h5" sx={{ color: readerTheme.textColor }}>
          {error}
        </Typography>
      </Box>
    );
  }

  return (
    <Box
      {...swipeHandlers}
      sx={{
        position: 'relative',
        height: '100vh',
        width: '100vw',
        bgcolor: readerTheme.backgroundColor,
        color: readerTheme.textColor,
        p: 0,
        m: 0,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      <Box 
        sx={{ 
          position: 'fixed', 
          top: 0, 
          left: 0, 
          right: 0, 
          zIndex: 1100,
          bgcolor: readerTheme.backgroundColor,
          borderBottom: 1,
          borderColor: 'divider',
          boxShadow: 1
        }}
      >
        <LinearProgress
          variant="determinate"
          value={(currentSection / normalizedContent.length) * 100}
          sx={{
            height: '3px',
            backgroundColor: 'rgba(0, 0, 0, 0.1)',
            '& .MuiLinearProgress-bar': {
              backgroundColor: readerTheme.textColor,
              transition: 'transform 0.3s ease-out',
            },
          }}
        />
        <Typography
          variant="caption"
          sx={{
            position: 'absolute',
            right: '8px',
            top: '8px',
            padding: '4px 8px',
            borderRadius: '12px',
            backgroundColor: 'rgba(0, 0, 0, 0.1)',
            color: readerTheme.textColor,
            fontSize: '0.75rem',
            fontWeight: 500,
          }}
        >
          {`${Math.round(progress)}%`}
        </Typography>
      </Box>

      <Box
        className="kindle-reader-content"
        ref={(el) => {
          if (el) {
            el.addEventListener('scroll', () => detectChapterEnd(el));
          }
        }}
        sx={{
          maxWidth: '65ch',
          mx: 'auto',
          height: 'calc(100vh - 128px)',
          position: 'relative',
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          pt: '64px',
          pb: '64px',
          px: { xs: 3, sm: 4 },
          '& > *:first-of-type': {
            mt: 0
          },
          scrollBehavior: 'smooth',
          fontSize: { xs: '1.1rem', sm: '1.2rem', md: '1.25rem' },
          '& p': {
            mb: 2,
            textAlign: 'justify',
            hyphens: 'auto',
            lineHeight: 1.8,
          },
          '& h1, & h2': {
            textAlign: 'center',
            mb: 3,
          },
          whiteSpace: 'pre-wrap',
          wordWrap: 'break-word',
          fontFamily: readerTheme.fontFamily,
          lineHeight: readerTheme.lineHeight,
          '&::-webkit-scrollbar': {
            width: '8px',
          },
          '&::-webkit-scrollbar-track': {
            background: 'transparent',
          },
          '&::-webkit-scrollbar-thumb': {
            background: (theme) => `${readerTheme.textColor}33`,
            borderRadius: '4px',
          },
          '&::-webkit-scrollbar-thumb:hover': {
            background: (theme) => `${readerTheme.textColor}66`,
          },
          scrollbarWidth: 'thin',
          scrollbarColor: (theme) => `${readerTheme.textColor}33 transparent`,
        }}
      >
        {displayedText}
        {isChapterEnd && (
          <Box 
            sx={{ 
              mt: 4,
              mb: 4,
              textAlign: 'center',
              p: 2,
              borderRadius: 1,
              bgcolor: 'rgba(0, 0, 0, 0.05)',
            }}
          >
            <Button
              variant="contained"
              onClick={() => {
                if (currentSection < normalizedContent.length - 1) {
                  setCurrentSection(prev => prev + 1);
                }
              }}
              sx={{
                bgcolor: readerTheme.textColor,
                color: readerTheme.backgroundColor,
                '&:hover': {
                  bgcolor: readerTheme.textColor,
                  opacity: 0.9,
                },
              }}
            >
              Chapitre suivant
            </Button>
          </Box>
        )}
      </Box>

      <ReaderSettings
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        theme={readerTheme}
        speed={streamSpeed}
        onSpeedChange={setStreamSpeed}
        onThemeChange={(setting, value) => {
          setReaderTheme(prev => ({
            ...prev,
            [setting]: value
          }));
        }}
      />
    </Box>
  );
};

export default KindleReader;