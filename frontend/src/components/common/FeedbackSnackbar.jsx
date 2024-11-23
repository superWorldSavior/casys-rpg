import React from 'react';
import { Snackbar, Alert, CircularProgress, Box } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';

const FeedbackSnackbar = ({ open, message, severity, onClose, loading, animation = 'fade' }) => {
  const getAnimationVariants = () => {
    const baseTransition = {
      duration: 0.4,
      ease: [0.4, 0, 0.2, 1]
    };

    switch (animation) {
      case 'bounce':
        return {
          initial: { opacity: 0, y: 50, scale: 0.3 },
          animate: { 
            opacity: 1, 
            y: 0, 
            scale: 1,
            transition: {
              ...baseTransition,
              scale: { duration: 0.3, ease: "backOut" }
            }
          },
          exit: { 
            opacity: 0, 
            y: 20, 
            scale: 0.5,
            transition: baseTransition
          }
        };
      case 'shake':
        return {
          initial: { opacity: 0, x: 0 },
          animate: { 
            opacity: 1,
            x: [-10, 10, -5, 5, 0],
            transition: { 
              ...baseTransition,
              x: { duration: 0.5, ease: "easeInOut" }
            }
          },
          exit: { 
            opacity: 0, 
            x: 0,
            transition: baseTransition
          }
        };
      default:
        return {
          initial: { opacity: 0, y: 20, scale: 0.95 },
          animate: { 
            opacity: 1, 
            y: 0, 
            scale: 1,
            transition: baseTransition
          },
          exit: { 
            opacity: 0, 
            y: 20, 
            scale: 0.95,
            transition: baseTransition
          }
        };
    }
  };

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          {...getAnimationVariants()}
          transition={{ duration: 0.3, type: 'spring', stiffness: 500, damping: 25 }}
        >
          <Snackbar 
            open={open} 
            autoHideDuration={4000} 
            onClose={onClose}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
          >
            <Alert 
              onClose={onClose} 
              severity={severity} 
              icon={loading ? <CircularProgress size={20} /> : undefined}
              sx={{ 
                width: '100%',
                minWidth: '250px',
                boxShadow: 3,
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                '& .MuiAlert-icon': {
                  marginRight: 1,
                  animation: loading ? 'spin 1s linear infinite' : 'bounce 0.5s ease'
                },
                '& .MuiAlert-message': {
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1
                },
                animation: `${severity === 'success' ? 'pulse' : severity === 'error' ? 'shake' : ''} 0.5s ease-in-out`
              }}
            >
              {message}
              {loading && (
                <Box component="span" sx={{ display: 'inline-flex', ml: 1 }}>
                  <CircularProgress size={16} />
                </Box>
              )}
            </Alert>
          </Snackbar>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default FeedbackSnackbar;
