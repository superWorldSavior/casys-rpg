import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Box, Typography, Button } from '@mui/material';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import remarkGfm from 'remark-gfm';
import ReaderSettings from './ReaderSettings';

const KindleReader = ({ 
  content,
  bookId,
  customTheme,
  onProgressChange,
  onNextChapter,
  onPreviousChapter
}) => {
  const [displayedText, setDisplayedText] = useState('');
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [isChapterEnd, setIsChapterEnd] = useState(false);
  const contentRef = useRef(null);
  
  const [readerTheme, setReaderTheme] = useState({
    backgroundColor: customTheme?.backgroundColor || '#F6F3E9',
    textColor: customTheme?.textColor || '#2c2c2c',
    fontFamily: customTheme?.fontFamily || '"Bookerly", "Georgia", serif',
    fontSize: customTheme?.fontSize || '1.2rem',
    lineHeight: customTheme?.lineHeight || 1.8,
  });

  const detectChapterEnd = useCallback((element) => {
    if (!element) return;
    
    const { scrollTop, scrollHeight, clientHeight } = element;
    const isNearBottom = scrollTop + clientHeight >= scrollHeight - 100;
    setIsChapterEnd(isNearBottom);

    const progress = Math.min(100, Math.round((scrollTop / (scrollHeight - clientHeight)) * 100));
    setProgress(progress);
    if (onProgressChange) {
      onProgressChange(progress);
    }
  }, [onProgressChange]);

  useEffect(() => {
    const initializeContent = async () => {
      try {
        setError(null);
        setIsLoading(true);

        if (!content) {
          setDisplayedText('');
          return;
        }

        // Normalize content based on type
        let processedContent = '';
        try {
          if (typeof content === 'string') {
            processedContent = content;
          } else if (content?.chapter) {
            processedContent = content.chapter;
          } else if (typeof content === 'object') {
            processedContent = JSON.stringify(content, null, 2);
          }

          // Add debug logs
          console.log('Raw content:', content);
          console.log('Content type:', typeof content);
          console.log('Processed content:', processedContent);

        // Clean up formatting issues and handle markdown
        processedContent = processedContent
          .replace(/\\n/g, '\n')
          .replace(/\\r/g, '')
          .replace(/\\/g, '')
          .replace(/\u0000/g, '')
          .replace(/#{1,6}\s+/g, (match) => match.trim() + ' ') // Fix markdown headings
          .replace(/(?:\r\n|\r|\n){2,}/g, '\n\n') // Normalize line breaks
          .trim();

        if (!processedContent) {
          throw new Error('Le contenu est invalide ou vide après traitement');
        }

        setDisplayedText(processedContent);
        setError(null);
      } catch (err) {
        console.error('Error processing content:', err);
        setError(err.message || 'Erreur lors du traitement du contenu');
      } finally {
        setIsLoading(false);
      }
    };

    initializeContent();
  }, [content]);

  useEffect(() => {
    if (!bookId) return;
    
    const readingState = {
      progress,
      timestamp: Date.now(),
      theme: readerTheme
    };
    
    try {
      localStorage.setItem(
        `kindle-reader-${bookId}`,
        JSON.stringify(readingState)
      );
    } catch (err) {
      console.warn('Failed to save reading state:', err);
    }
  }, [bookId, progress, readerTheme]);

  if (isLoading) {
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
        className="kindle-reader-content"
        ref={(el) => {
          contentRef.current = el;
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
          scrollBehavior: 'smooth',
          fontSize: readerTheme.fontSize,
          fontFamily: readerTheme.fontFamily,
          lineHeight: readerTheme.lineHeight,
          '&::-webkit-scrollbar': {
            width: '8px',
          },
          '&::-webkit-scrollbar-track': {
            background: 'transparent',
          },
          '&::-webkit-scrollbar-thumb': {
            background: `${readerTheme.textColor}33`,
            borderRadius: '4px',
          },
          '&::-webkit-scrollbar-thumb:hover': {
            background: `${readerTheme.textColor}66`,
          },
          scrollbarWidth: 'thin',
          scrollbarColor: `${readerTheme.textColor}33 transparent`,
        }}
      >
        <ReactMarkdown
          rehypePlugins={[rehypeRaw]}
          remarkPlugins={[remarkGfm]}
          components={{
            p: ({node, ...props}) => (
              <Typography 
                component="p" 
                sx={{
                  mb: 2,
                  textAlign: 'justify',
                  hyphens: 'auto',
                  lineHeight: readerTheme.lineHeight,
                  fontFamily: readerTheme.fontFamily,
                  fontSize: readerTheme.fontSize,
                  color: readerTheme.textColor,
                  '&:first-of-type': {
                    mt: 3,
                  },
                  '&:last-of-type': {
                    mb: 4,
                  }
                }}
                {...props}
              />
            ),
            h1: ({node, ...props}) => (
              <Typography
                variant="h1"
                sx={{
                  fontSize: '2rem',
                  mb: 3,
                  mt: 4,
                  textAlign: 'center',
                  fontWeight: 700,
                  color: readerTheme.textColor,
                  fontFamily: readerTheme.fontFamily,
                }}
                {...props}
              />
            ),
            h2: ({node, ...props}) => (
              <Typography
                variant="h2"
                sx={{
                  fontSize: '1.5rem',
                  mb: 2,
                  mt: 3,
                  fontWeight: 600,
                  color: readerTheme.textColor,
                  fontFamily: readerTheme.fontFamily,
                }}
                {...props}
              />
            ),
            h3: ({node, ...props}) => (
              <Typography
                variant="h3"
                sx={{
                  fontSize: '1.25rem',
                  mb: 2,
                  mt: 3,
                  fontWeight: 600,
                  color: readerTheme.textColor,
                  fontFamily: readerTheme.fontFamily,
                }}
                {...props}
              />
            ),
            blockquote: ({node, ...props}) => (
              <Box
                component="blockquote"
                sx={{
                  borderLeft: '4px solid',
                  borderColor: `${readerTheme.textColor}40`,
                  pl: 2,
                  my: 2,
                  color: `${readerTheme.textColor}CC`,
                }}
                {...props}
              />
            ),
            pre: ({node, ...props}) => (
              <Box
                component="pre"
                sx={{
                  p: 2,
                  mb: 2,
                  backgroundColor: `${readerTheme.textColor}10`,
                  borderRadius: 1,
                  overflow: 'auto',
                  fontSize: '0.9em',
                }}
                {...props}
              />
            )
          }}
        >
          {displayedText}
        </ReactMarkdown>
      </Box>

      <Box
        sx={{
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          p: 2,
          bgcolor: `${readerTheme.backgroundColor}CC`,
          borderTop: 1,
          borderColor: 'divider',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backdropFilter: 'blur(8px)',
          zIndex: 1000,
        }}
      >
        <Button
          variant="contained"
          onClick={onPreviousChapter}
          sx={{
            bgcolor: readerTheme.textColor,
            color: readerTheme.backgroundColor,
            '&:hover': {
              bgcolor: readerTheme.textColor,
              opacity: 0.9,
            },
          }}
        >
          Chapitre précédent
        </Button>
        <Button
          variant="contained"
          onClick={onNextChapter}
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

      <ReaderSettings
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        theme={readerTheme}
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
