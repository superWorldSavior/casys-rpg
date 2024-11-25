import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { Box, IconButton, Typography, LinearProgress, Button } from '@mui/material';
import NavigateBeforeIcon from '@mui/icons-material/NavigateBefore';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import SettingsIcon from '@mui/icons-material/Settings';
import { useTheme } from '@mui/material/styles';
import { useSwipeable } from 'react-swipeable';
import ReaderSettings from './ReaderSettings';

// Constants
const STORAGE_KEY = 'kindle-reader-state';
const DEFAULT_SPEED = 30;

// Theme helper
const getInitialTheme = (isDark) => ({
  fontFamily: '"Bookerly", "Georgia", serif',
  fontSize: '1.2rem',
  lineHeight: '1.8',
  textColor: isDark ? '#e1e1e1' : '#2c2c2c',
  backgroundColor: isDark ? '#131516' : '#F6F3E9'
});

const KindleReader = ({ content = [], initialSection = 0, bookId, onProgressChange, customTheme }) => {
  // Theme hooks
  const theme = useTheme();
  const [readerTheme, setReaderTheme] = useState(() => 
    customTheme || getInitialTheme(theme.palette.mode === 'dark')
  );
  
  // Refs
  const cancelStreamRef = useRef(false);
  const contentRef = useRef(content);
  
  // State hooks
  const [currentSection, setCurrentSection] = useState(initialSection);
  const [displayedText, setDisplayedText] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [isChapterEnd, setIsChapterEnd] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [streamSpeed, setStreamSpeed] = useState(DEFAULT_SPEED);
  const [error, setError] = useState(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);

  // Memoized content
  const normalizedContent = useMemo(() => {
    if (!content) {
      console.warn('No content available');
      return [];
    }
    
    const contentArray = Array.isArray(content) ? content : [content];
    
    const normalized = contentArray.map((section, index) => {
      try {
        if (typeof section === 'string') {
          // Extraire le titre du contenu markdown
          const lines = section.split('\n');
          const title = lines[0]?.startsWith('#') ? 
            lines[0].replace(/^#+\s*/, '') : 
            `Section ${index + 1}`;
            
          return {
            content: section,
            number: index + 1,
            title,
            key: `section-${index}`
          };
        }
        return {
          ...section,
          number: index + 1,
          title: section.title || `Section ${index + 1}`,
          key: `section-${index}`
        };
      } catch (error) {
        console.error(`Error processing section ${index}:`, error);
        return {
          content: "Erreur de chargement de la section",
          number: index + 1,
          title: `Section ${index + 1}`,
          key: `section-${index}`
        };
      }
    });

    console.log('Content loaded:', normalized.length, 'sections');
    return normalized;
  }, [content]);

  // Navigation callback
  const handleNavigation = useCallback((direction) => {
    if (isStreaming) return;
    
    setCurrentSection(prev => {
      const next = prev + direction;
      return Math.max(0, Math.min(next, normalizedContent.length - 1));
    });
  }, [isStreaming, normalizedContent.length]);

  // Text streaming callback
  const autoScroll = useCallback((element, speed = 1) => {
    if (!element) return;
    
    const scrollStep = () => {
      const isBottom = element.scrollHeight - element.scrollTop === element.clientHeight;
      if (!isBottom) {
        element.scrollBy({
          top: speed,
          behavior: 'smooth'
        });
        requestAnimationFrame(scrollStep);
      }
    };

    requestAnimationFrame(scrollStep);
  }, []);

  const streamText = useCallback(async (text) => {
    if (!text) {
      console.warn('No text provided for streaming');
      return;
    }
    
    const textContent = typeof text === 'string' ? text : text.content || '';
    
    try {
      setIsStreaming(true);
      setDisplayedText('');
      setError(null);
      
      // Afficher le texte directement
      const paragraphs = textContent.split('\n').filter(p => p.trim());
      setDisplayedText(paragraphs.join('\n\n'));
      
      // Mettre à jour la progression
      setProgress(100);
      if (onProgressChange) {
        onProgressChange(100);
      }
      
    } catch (err) {
      setError("Erreur lors de l'affichage du texte");
      console.error("Display error:", err);
    } finally {
      setIsStreaming(false);
    }
  }, [onProgressChange]);

  // Event Handlers
  const navigationHandlers = useMemo(() => {
    const handleKeyPress = (e) => {
      if (e.key === 'ArrowLeft') handleNavigation(-1);
      else if (e.key === 'ArrowRight') handleNavigation(1);
      else if (e.key === 'Escape') {
        cancelStreamRef.current = true;
        setIsStreaming(false);
      }
    };

    return {
      keyboard: handleKeyPress,
      swipe: {
        onSwipedLeft: () => handleNavigation(1),
        onSwipedRight: () => handleNavigation(-1),
        preventDefaultTouchmoveEvent: true,
        trackMouse: true
      }
    };
  }, [handleNavigation]);

  const swipeHandlers = useSwipeable(navigationHandlers.swipe);

  // Effects
  useEffect(() => {
    contentRef.current = content;
  }, [content]);

  useEffect(() => {
    setReaderTheme(prev => ({
      ...prev,
      textColor: theme.palette.mode === 'dark' ? '#e1e1e1' : '#2c2c2c',
      backgroundColor: theme.palette.mode === 'dark' ? '#131516' : '#F6F3E9'
    }));
  }, [theme.palette.mode]);

  useEffect(() => {
    setIsLoading(normalizedContent.length === 0);
  }, [normalizedContent]);

  useEffect(() => {
    if (!bookId || currentSection === undefined) return;
    
    // Save reading progress with more details
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
    
    // Mettre à jour le titre de la page
    document.title = `Lecture en cours - ${Math.round(progress)}%`;
  }, [bookId, currentSection, progress, readerTheme, streamSpeed]);

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
        const sectionToDisplay = initialSection >= 0 && initialSection < normalizedContent.length
          ? initialSection
          : currentSection;
        
        if (sectionToDisplay >= 0 && sectionToDisplay < normalizedContent.length) {
          const section = normalizedContent[sectionToDisplay];
          const content = typeof section === 'string' ? section : section?.content;
          
          if (content) {
            // Reset state before starting new stream
            setDisplayedText('');
            setProgress(0);
            cancelStreamRef.current = false;
            
            try {
              await streamText(content);
            } catch (err) {
              console.error('Error streaming text:', err);
              setError('Erreur lors du streaming du texte');
              // Display full content on error
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

    // Cleanup function
    return () => {
      cancelStreamRef.current = true;
    };
  }, [normalizedContent, currentSection, initialSection, streamText, isLoading]);

  // Render Methods
  const renderConditionalState = () => {
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

    return null;
  };

  const conditionalContent = renderConditionalState();
  if (conditionalContent) {
    return conditionalContent;
  }

  console.log('KindleReader rendering with:', { 
    contentLength: normalizedContent.length,
    currentSection,
    isLoading,
    error
  });

  // Debug logs
  console.log('KindleReader rendering with:', {
    contentLength: content.length,
    currentContent: content[currentSection],
    theme,
    readerTheme
  });

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
      {/* Progress bar with percentage */}
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
          value={(currentSection / (content.length || 1)) * 100}
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

      {/* Empty space to preserve layout */}

      {/* Text content */}
      <Box
        sx={{
          maxWidth: '65ch',
          mx: 'auto',
          pt: { xs: '64px', sm: '72px' }, // Espace pour la barre du haut
          pb: { xs: '80px', sm: '88px' }, // Espace pour la barre du bas
          px: { xs: 3, sm: 4 },
          overflowY: 'auto',
          height: 'calc(100vh - 144px)', // Hauteur totale moins les barres
          position: 'relative',
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
          <Box sx={{ 
            textAlign: 'center',
            mt: 4,
            p: 2,
            borderRadius: 1,
            bgcolor: 'rgba(0, 0, 0, 0.05)',
          }}>
            <Typography variant="body2" sx={{ mb: 2, color: readerTheme.textColor }}>
              Faites défiler ou cliquez pour passer au chapitre suivant
            </Typography>
            <Button
              variant="contained"
              onClick={() => handleNavigation(1)}
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

      {/* Settings dialog */}
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