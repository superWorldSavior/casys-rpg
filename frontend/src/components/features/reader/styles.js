export const READER_STYLES = {
  paper: {
    backgroundColor: '#f6f3e9', // Couleur papier Kindle
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '1.5rem',
    '@media (max-width: 600px)': {
      padding: '1rem',
    },
  },
  content: {
    maxWidth: '45em', // Largeur optimale pour la lecture
    width: '100%',
    margin: '0 auto',
    fontSize: '1.2rem',
    lineHeight: 1.8,
    color: '#2c2c2c',
    fontFamily: '"Bookerly", "Georgia", serif',
    '& p': {
      marginBottom: '1.2rem',
      textAlign: 'justify',
      hyphens: 'auto',
    },
    '& h1': {
      fontSize: '1.8rem',
      marginBottom: '2rem',
      color: '#1a1a1a',
      fontFamily: '"Bookerly", "Georgia", serif',
      textAlign: 'center',
    },
    '& h2': {
      fontSize: '1.4rem',
      marginBottom: '1.5rem',
      color: '#1a1a1a',
      fontFamily: '"Bookerly", "Georgia", serif',
    },
  },
  progressBar: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    height: '4px',
    backgroundColor: '#e0e0e0',
    zIndex: 1000,
  },
  progressIndicator: {
    height: '100%',
    backgroundColor: '#2196f3',
    transition: 'width 0.3s ease-in-out',
  },
  controls: {
    position: 'fixed',
    bottom: 0,
    left: 0,
    right: 0,
    padding: '1rem',
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    borderTop: '1px solid #e0e0e0',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    zIndex: 1000,
  },
};

export const animations = {
  fadeIn: {
    '@keyframes fadeIn': {
      from: { opacity: 0 },
      to: { opacity: 1 },
    },
    opacity: 0,
    animation: 'fadeIn 0.5s ease-in-out forwards',
  },
  slideIn: {
    '@keyframes slideIn': {
      from: { transform: 'translateX(-100%)' },
      to: { transform: 'translateX(0)' },
    },
    transform: 'translateX(-100%)',
    animation: 'slideIn 0.5s ease-out forwards',
  },
};
