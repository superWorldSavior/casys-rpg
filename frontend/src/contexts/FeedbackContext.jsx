import React, { createContext, useContext, useState, useCallback } from 'react';
import FeedbackSnackbar from '../components/common/FeedbackSnackbar';
import { motion, AnimatePresence } from 'framer-motion';

const FeedbackContext = createContext(null);

export const FeedbackProvider = ({ children }) => {
  const [feedback, setFeedback] = useState({
    open: false,
    message: '',
    severity: 'success',
    loading: false,
    animation: 'fade' // 'fade', 'bounce', 'shake'
  });

  const showFeedback = useCallback((message, options = {}) => {
    const { severity = 'success', loading = false, animation = 'fade' } = options;
    
    setFeedback({
      open: true,
      message,
      severity,
      loading,
      animation
    });

    // Add feedback animation class to body
    document.body.classList.add(`feedback-${severity}`);
    setTimeout(() => {
      document.body.classList.remove(`feedback-${severity}`);
    }, 500);
  }, []);

  const showLoading = useCallback((message = 'Chargement...') => {
    showFeedback(message, { severity: 'info', loading: true, animation: 'pulse' });
  }, [showFeedback]);

  const showSuccess = useCallback((message) => {
    showFeedback(message, { severity: 'success', animation: 'bounce' });
  }, [showFeedback]);

  const showError = useCallback((message) => {
    showFeedback(message, { severity: 'error', animation: 'shake' });
  }, [showFeedback]);

  const hideFeedback = useCallback(() => {
    setFeedback(prev => ({
      ...prev,
      open: false,
      loading: false
    }));
  }, []);

  return (
    <FeedbackContext.Provider value={{ 
      showFeedback,
      showLoading,
      showSuccess,
      showError,
      hideFeedback,
      isLoading: feedback.loading
    }}>
      <AnimatePresence mode="wait">
        {children}
      </AnimatePresence>
      <FeedbackSnackbar
        open={feedback.open}
        message={feedback.message}
        severity={feedback.severity}
        onClose={hideFeedback}
        loading={feedback.loading}
        animation={feedback.animation}
      />
    </FeedbackContext.Provider>
  );
};

export const useFeedback = () => {
  const context = useContext(FeedbackContext);
  if (!context) {
    throw new Error('useFeedback must be used within a FeedbackProvider');
  }
  return context;
};
