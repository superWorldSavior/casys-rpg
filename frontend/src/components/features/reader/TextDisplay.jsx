// Move content from TextDisplay.jsx to this location
import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';

const ANIMATION_STYLES = [
  'fade-in',
  'slide-right',
  'slide-up',
const DISPLAY_SPEED = {
  slow: 50,
  medium: 30,
  fast: 15
};

const calculateSpeed = (speedSetting) => {
  const normalizedSpeed = Math.min(Math.max(speedSetting, 1), 10);
  return DISPLAY_SPEED.medium - ((normalizedSpeed - 1) * 2);
};
useEffect(() => {
  if (!textContent[currentSection]) return;
  
  setRevealedText('');
  setIsRevealing(true);
  
  let currentIndex = 0;
  const text = textContent[currentSection];
  const displaySpeed = calculateSpeed(speed);
  
  const timer = setInterval(() => {
    if (currentIndex < text.length) {
      setRevealedText(prev => text.slice(0, currentIndex + 1));
      currentIndex++;
    } else {
      setIsRevealing(false);
      clearInterval(timer);
    }
  }, displaySpeed);
  
  return () => clearInterval(timer);
}, [currentSection, textContent, speed]);
  // Animation styles
export const ANIMATION_STYLES = {
  fadeIn: {
    opacity: 0,
    animation: 'fadeIn 0.5s ease-in-out forwards'
  },
  slideIn: {
    transform: 'translateX(-100%)',
    animation: 'slideIn 0.5s ease-out forwards'
  }
};

import React, { useState, useEffect, useRef } from 'react';
import { Box, Paper, Typography } from '@mui/material';
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
  return DISPLAY_SPEED.medium - ((Math.min(Math.max(speedSetting, 1), 10) - 1) * 2);
};

function TextDisplay({ textContent = [], currentSection = 0, speed = 5, theme = {}, onProgressChange, setCurrentSection }) {
  const [revealedText, setRevealedText] = useState('');
  const [isRevealing, setIsRevealing] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    if (!textContent[currentSection]) {
      setRevealedText('');
      return;
    }
    
    setRevealedText('');
    setIsRevealing(true);
    
    const text = textContent[currentSection];
    const displaySpeed = calculateSpeed(speed);
    let currentIndex = 0;
    let timer;
    
    const revealNextChar = () => {
      if (currentIndex < text.length) {
        setRevealedText(text.slice(0, currentIndex + 1));
        currentIndex++;
        timer = setTimeout(revealNextChar, displaySpeed);
      } else {
        setIsRevealing(false);
        if (onProgressChange) {
          const progress = ((currentSection + 1) / textContent.length) * 100;
          onProgressChange(progress);
        }
      }
    };
    
    timer = setTimeout(revealNextChar, displaySpeed);
    
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

  const baseStyles = {
    fontFamily: theme.fontFamily || '"Bookerly", "Georgia", serif',
    fontSize: theme.fontSize || '1.2rem',
    color: theme.textColor || '#2c2c2c',
    lineHeight: theme.lineHeight || 1.8
  };

  return (
    <Paper sx={{
      ...READER_STYLES.paper,
      backgroundColor: theme.backgroundColor || '#f6f3e9'
    }} elevation={0}>
      <Box sx={{
        ...READER_STYLES.content,
        ...animations.fadeIn
      }} ref={containerRef}>
        {textContent[currentSection] && (
          <Box className="kindle-reader" sx={{ opacity: isRevealing ? 0.9 : 1, transition: 'opacity 0.3s' }}>
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeRaw]}
              components={{
                h1: ({node, children, ...props}) => (
                  <Typography variant="h1" sx={{...baseStyles, fontSize: '1.8rem', mb: 3}} {...props}>
                    {children}
                  </Typography>
                ),
                h2: ({node, children, ...props}) => (
                  <Typography variant="h2" sx={{...baseStyles, fontSize: '1.5rem', mb: 2}} {...props}>
                    {children}
                  </Typography>
                ),
                p: ({node, children, ...props}) => (
                  <Typography component="p" sx={{...baseStyles, mb: 2, textAlign: 'justify'}} {...props}>
                    {children}
                  </Typography>
                ),
                strong: ({node, children, ...props}) => (
                  <Typography component="strong" sx={{...baseStyles, fontWeight: 'bold'}} {...props}>
                    {children}
                  </Typography>
                ),
                em: ({node, children, ...props}) => (
                  <Typography component="em" sx={{...baseStyles, fontStyle: 'italic'}} {...props}>
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
