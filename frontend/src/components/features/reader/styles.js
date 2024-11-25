export const READER_STYLES = {
  paper: {
    backgroundColor: '#F6F3E9', // Classic Kindle paper color
    minHeight: '100vh',
    width: '100vw',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: 0,
    transition: 'background-color 0.3s ease-in-out',
    boxShadow: 'none',
    overscrollBehavior: 'none',
    margin: 0,
    borderRadius: 0,
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    WebkitOverflowScrolling: 'touch',
    backgroundImage: 'radial-gradient(#00000005 1px, transparent 0)',
    backgroundSize: '4px 4px',
    backgroundPosition: '-2px -2px',
    '@media (max-width: 600px)': {
      padding: '0.75rem',
      backgroundImage: 'none',
    },
    '@media (prefers-color-scheme: dark)': {
      backgroundColor: '#131516',
      backgroundImage: 'none',
      boxShadow: 'inset 0 0 100px rgba(255,255,255,0.02)',
    },
  },
  content: {
    maxWidth: '40em',
    width: '100%',
    margin: '0 auto',
    padding: '0 1rem',
    fontSize: { xs: '1.1rem', sm: '1.2rem', md: '1.25rem' },
    lineHeight: 1.8,
    opacity: 1,
    transition: 'opacity 0.3s ease-out',
    '&.streaming': {
      '& p': {
        opacity: 0,
        transform: 'translateY(10px)',
        transition: 'opacity 0.5s ease-out, transform 0.5s ease-out',
        '&.visible': {
          opacity: 1,
          transform: 'translateY(0)'
        }
      }
    },
    color: '#2c2c2c',
    fontFamily: '"Bookerly", "Georgia", serif',
    letterSpacing: '0.01em',
    wordSpacing: '0.02em',
    transition: 'color 0.3s ease-in-out',
    '& p': {
      marginBottom: '1.5rem',
      textAlign: 'justify',
      hyphens: 'auto',
      opacity: 1,
      transform: 'translateY(0)',
      transition: 'opacity 0.3s ease-out, transform 0.3s ease-out',
      '&.appearing': {
        opacity: 0,
        transform: 'translateY(10px)',
      }
    },
    '& h1': {
      fontSize: { xs: '1.6rem', sm: '1.8rem', md: '2rem' },
      marginBottom: '2.5rem',
      color: '#1a1a1a',
      fontFamily: '"Bookerly", "Georgia", serif',
      textAlign: 'center',
      fontWeight: 700,
    },
    '& h2': {
      fontSize: { xs: '1.3rem', sm: '1.4rem', md: '1.5rem' },
      marginBottom: '2rem',
      color: '#1a1a1a',
      fontFamily: '"Bookerly", "Georgia", serif',
      fontWeight: 600,
    },
    '@media (prefers-color-scheme: dark)': {
      color: '#e1e1e1',
      '& h1, & h2': {
        color: '#f5f5f5',
      }
    },
  },
  progressBar: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    height: '2px',
    backgroundColor: 'rgba(0, 0, 0, 0.1)',
    zIndex: 1000,
    '@media (prefers-color-scheme: dark)': {
      backgroundColor: 'rgba(255, 255, 255, 0.1)',
    },
  },
  progressIndicator: {
    height: '100%',
    backgroundColor: '#2c2c2c',
    transition: 'width 0.2s ease-out',
    '@media (prefers-color-scheme: dark)': {
      backgroundColor: '#e1e1e1',
    },
  },
  controls: {
    position: 'fixed',
    bottom: 0,
    left: 0,
    right: 0,
    padding: '0.75rem',
    backdropFilter: 'blur(10px)',
    backgroundColor: 'rgba(246, 243, 233, 0.85)',
    borderTop: '1px solid rgba(0, 0, 0, 0.1)',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    zIndex: 1000,
    transform: 'translateY(0)',
    transition: 'transform 0.3s ease-in-out, opacity 0.3s ease-in-out',
    '&.hidden': {
      transform: 'translateY(100%)',
      opacity: 0,
    },
    '@media (prefers-color-scheme: dark)': {
      backgroundColor: 'rgba(19, 21, 22, 0.85)',
      borderTop: '1px solid rgba(255, 255, 255, 0.1)',
    },
  },
};

export const animations = {
  fadeIn: {
    '@keyframes fadeIn': {
      from: { opacity: 0, transform: 'translateY(10px)' },
      to: { opacity: 1, transform: 'translateY(0)' },
    },
    opacity: 0,
    animation: 'fadeIn 0.4s ease-out forwards',
  },
  slideIn: {
    '@keyframes slideIn': {
      from: { transform: 'translateX(-20px)', opacity: 0 },
      to: { transform: 'translateX(0)', opacity: 1 },
    },
    transform: 'translateX(-20px)',
    opacity: 0,
    animation: 'slideIn 0.4s ease-out forwards',
  },
  pageTransition: {
    '@keyframes pageTransition': {
      '0%': { opacity: 1, transform: 'translateX(0)' },
      '50%': { opacity: 0, transform: 'translateX(-30px)' },
      '51%': { opacity: 0, transform: 'translateX(30px)' },
      '100%': { opacity: 1, transform: 'translateX(0)' },
    },
  },
  textAppear: {
    '@keyframes textAppear': {
      from: { opacity: 0, transform: 'translateY(5px)' },
      to: { opacity: 1, transform: 'translateY(0)' },
    },
  }
};
