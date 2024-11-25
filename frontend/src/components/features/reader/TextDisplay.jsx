import React, { useState, useEffect, useRef } from 'react';
import { Box, Paper, Typography, useTheme, CircularProgress } from '@mui/material';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import { READER_STYLES, animations } from './styles';

const DISPLAY_SPEED = {
  slow: 50,
  medium: 30,
  fast: 15
};

const calculateSpeed = (speedSetting) => {
  const normalizedSpeed = Math.min(Math.max(speedSetting, 1), 10);
  const baseSpeed = DISPLAY_SPEED.medium;
  // Implement more granular speed control
  const speedMultiplier = Math.pow(normalizedSpeed / 5, 1.5); // Non-linear speed scaling
  return Math.round(baseSpeed / speedMultiplier);
};

function TextDisplay({ textContent = [], currentSection = 0, speed = 5, theme = {}, onProgressChange, setCurrentSection }) {
  const [revealedText, setRevealedText] = useState('');
  const [isRevealing, setIsRevealing] = useState(false);
  const [animationDirection, setAnimationDirection] = useState('none');
  const [wordIndex, setWordIndex] = useState(0);
  const [paragraphIndex, setParagraphIndex] = useState(0);
  const [isFirstRender, setIsFirstRender] = useState(true);
  const containerRef = useRef(null);
  const lastSectionRef = useRef(currentSection);
  const animationFrameRef = useRef();
  const muiTheme = useTheme();

  useEffect(() => {
    if (!textContent[currentSection]) {
      setRevealedText('');
      return;
    }
    
    // Determine animation direction based on section change
    const direction = currentSection > lastSectionRef.current ? 'left' : 
                     currentSection < lastSectionRef.current ? 'right' : 'none';
    setAnimationDirection(direction);
    lastSectionRef.current = currentSection;
    
    setRevealedText('');
    setIsRevealing(true);
    
    const text = textContent[currentSection];
    const displaySpeed = calculateSpeed(speed);
    let currentIndex = 0;
    let paragraphs = text.split('\n');
    let currentParagraph = 0;
    let timer;
    
    const revealNextParagraph = () => {
      if (currentParagraph < paragraphs.length) {
        const words = paragraphs[currentParagraph].split(/\s+/);
        let wordIndex = 0;
        
        const revealNextWord = () => {
          if (wordIndex < words.length) {
            setRevealedText(prev => {
              const currentParagraphText = words.slice(0, wordIndex + 1).join(' ');
              const previousParagraphs = paragraphs.slice(0, currentParagraph).join('\n');
              const nextText = previousParagraphs ? 
                `${previousParagraphs}\n${currentParagraphText}` : 
                currentParagraphText;
              
              // Calculate and update progress
              const totalWords = paragraphs.reduce((acc, p) => acc + p.split(/\s+/).length, 0);
              const wordsRead = paragraphs.slice(0, currentParagraph).reduce((acc, p) => acc + p.split(/\s+/).length, 0) + wordIndex;
              const currentProgress = (wordsRead / totalWords) * 100;
              
              if (onProgressChange) {
                const overallProgress = ((currentSection * 100) + currentProgress) / textContent.length;
                onProgressChange(Math.min(overallProgress, 100));
              }
              
              return nextText;
            });
            wordIndex++;
            // Adjust speed based on punctuation
            const currentWord = words[wordIndex - 1];
            const hasPunctuation = /[,.!?]$/.test(currentWord);
            const nextDelay = hasPunctuation ? displaySpeed * 1.5 : displaySpeed;
            timer = setTimeout(revealNextWord, nextDelay);
          } else {
            currentParagraph++;
            // Longer pause between paragraphs
            timer = setTimeout(revealNextParagraph, displaySpeed * 4);
          }
        };
        
        revealNextWord();
      } else {
        setIsRevealing(false);
        setAnimationDirection('none');
      }
    };
    
    timer = setTimeout(revealNextParagraph, displaySpeed);
    
    return () => {
      if (timer) clearTimeout(timer);
    };
  }, [currentSection, textContent, speed, onProgressChange]);

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyPress = (e) => {
      if ((e.key === 'ArrowRight' || e.key === 'Space') && !isRevealing) {
        if (currentSection < textContent.length - 1) {
          setCurrentSection?.(currentSection + 1);
        }
      } else if (e.key === 'ArrowLeft' && !isRevealing) {
        if (currentSection > 0) {
          setCurrentSection?.(currentSection - 1);
        }
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [currentSection, isRevealing, textContent.length, setCurrentSection]);

  const muiMode = muiTheme?.palette?.mode || 'light';
  const systemDefaultTextColor = muiMode === 'dark' ? '#e1e1e1' : '#2c2c2c';
  const systemDefaultBackgroundColor = muiMode === 'dark' ? '#131516' : '#F6F3E9';
  
  const themeColors = React.useMemo(() => ({
    textColor: theme?.textColor || systemDefaultTextColor,
    backgroundColor: theme?.backgroundColor || systemDefaultBackgroundColor,
  }), [theme?.textColor, theme?.backgroundColor, systemDefaultTextColor, systemDefaultBackgroundColor]);
  
  const baseStyles = {
    fontFamily: theme?.fontFamily || '"Bookerly", "Georgia", serif',
    fontSize: theme?.fontSize || '1.2rem',
    color: themeColors.textColor,
    lineHeight: theme?.lineHeight || 1.8,
    transition: 'all 0.3s ease-in-out',
    WebkitFontSmoothing: 'antialiased',
    MozOsxFontSmoothing: 'grayscale',
    textRendering: 'optimizeLegibility',
    backgroundColor: themeColors.backgroundColor
  };

  if (!Array.isArray(textContent)) {
    console.error('TextContent is not an array:', textContent);
    return (
      <Box 
        sx={{ 
          height: '100vh', 
          display: 'flex', 
          flexDirection: 'column',
          alignItems: 'center', 
          justifyContent: 'center',
          color: theme.textColor || defaultTextColor,
          backgroundColor: theme.backgroundColor || defaultBackgroundColor,
          gap: 2,
          p: 3
        }}
      >
        <Typography variant="h6" align="center">
          Erreur de chargement du contenu
        </Typography>
        <Typography variant="body2" align="center" color="text.secondary">
          Le contenu n'est pas dans le format attendu. Veuillez réessayer.
        </Typography>
      </Box>
    );
  }

  if (!textContent[currentSection]) {
    return (
      <Box 
        sx={{ 
          height: '100vh', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          color: theme.textColor || defaultTextColor,
          backgroundColor: theme.backgroundColor || defaultBackgroundColor,
        }}
      >
        <Typography variant="h6">
          Section non disponible
        </Typography>
      </Box>
    );
  }

  useEffect(() => {
    if (isFirstRender && textContent[currentSection]) {
      setRevealedText(textContent[currentSection]);
      setIsFirstRender(false);
    }
  }, [isFirstRender, textContent, currentSection]);

  return (
    <Paper sx={{
      ...READER_STYLES.paper,
      backgroundColor: themeColors.backgroundColor,
      color: themeColors.textColor,
      position: 'relative',
      overflow: 'hidden',
      minHeight: '100vh'
    }} elevation={0}>
      <Box sx={{
        ...READER_STYLES.content,
        transform: animationDirection === 'left' ? 'translateX(-100%)' : 
                  animationDirection === 'right' ? 'translateX(100%)' : 'translateX(0)',
        opacity: animationDirection === 'none' ? 1 : 0,
        transition: 'transform 0.3s ease-out, opacity 0.3s ease-out',
        padding: { xs: 2, sm: 3, md: 4 },
        maxWidth: '800px',
        margin: '0 auto',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        '& > *': { width: '100%' }
      }} ref={containerRef}>
        {textContent[currentSection] && (
          <Box className="kindle-reader" sx={{
            opacity: isRevealing ? 0.9 : 1,
            transition: 'opacity 0.3s',
            position: 'relative',
            '&::after': {
              content: '""',
              position: 'absolute',
              left: 0,
              right: 0,
              bottom: 0,
              height: '100px',
              background: 'linear-gradient(transparent, rgba(246, 243, 233, 0.8))',
              pointerEvents: 'none'
            }
          }}>
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeRaw]}
              components={{
                h1: ({node, children, ...props}) => (
                  <Typography variant="h1" sx={{
                    ...baseStyles,
                    fontSize: { xs: '1.5rem', sm: '1.8rem' },
                    mb: 3,
                    fontFamily: 'Bookerly, Georgia, serif',
                    color: muiTheme.palette.text.primary
                  }} {...props}>
                    {children}
                  </Typography>
                ),
                h2: ({node, children, ...props}) => (
                  <Typography variant="h2" sx={{
                    ...baseStyles,
                    fontSize: { xs: '1.3rem', sm: '1.5rem' },
                    mb: 2,
                    fontFamily: 'Bookerly, Georgia, serif',
                    color: muiTheme.palette.text.primary
                  }} {...props}>
                    {children}
                  </Typography>
                ),
                p: ({node, children, ...props}) => (
                  <Typography component="p" sx={{
                    ...baseStyles,
                    mb: 2,
                    textAlign: 'justify',
                    textJustify: 'inter-word',
                    hyphens: 'auto',
                    '&:first-of-type': {
                      '&::first-letter': {
                        fontSize: '3.5em',
                        float: 'left',
                        margin: '0.15em 0.15em 0.15em 0'
                      }
                    }
                  }} {...props}>
                    {children}
                  </Typography>
                ),
                strong: ({node, children, ...props}) => (
                  <Typography component="strong" sx={{
                    ...baseStyles,
                    fontWeight: 600,
                    color: muiTheme.palette.text.primary
                  }} {...props}>
                    {children}
                  </Typography>
                ),
                em: ({node, children, ...props}) => (
                  <Typography component="em" sx={{
                    ...baseStyles,
                    fontStyle: 'italic',
                    color: muiTheme.palette.text.primary
                  }} {...props}>
                    {children}
                  </Typography>
                )
              }}
            >
              {revealedText}
            </ReactMarkdown>
          </Box>
        )}
      </Box>
    </Paper>
  );
}

export default TextDisplay;
