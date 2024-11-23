import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useFeedback } from '../contexts/FeedbackContext';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  IconButton,
  LinearProgress,
  Alert,
  CardActions,
  Snackbar,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import PreviewIcon from '@mui/icons-material/Preview';
import PDFPreview from './PDFPreview';

const HomePage = () => {
  const [books, setBooks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [previewOpen, setPreviewOpen] = useState(false);
  const [selectedBook, setSelectedBook] = useState(null);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const navigate = useNavigate();
  const { showSuccess, showError, showLoading } = useFeedback();

  const testFeedbackInteractions = async () => {
    try {
      showLoading("Chargement en cours...");
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      showSuccess("Action réussie !");
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      showError("Une erreur s'est produite");
      
      // Add ripple effect to button
      const button = document.querySelector('[data-testid="test-interactions-button"]');
      if (button) {
        button.style.transform = 'scale(0.95)';
        setTimeout(() => {
          button.style.transform = 'scale(1)';
        }, 200);
      }
    } catch (error) {
      console.error('Error in feedback test:', error);
    }
  };

  useEffect(() => {
    fetchBooks();
  }, []);

  const fetchBooks = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/books');
      if (response.ok) {
        const data = await response.json();
        setBooks(data);
      } else {
        setError('Erreur lors du chargement des livres');
      }
    } catch (error) {
      console.error('Error fetching books:', error);
      setError('Erreur de connexion au serveur');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      setError('Veuillez sélectionner un fichier PDF valide');
      // Ajouter une animation de secousse pour indiquer l'erreur
      const input = event.target;
      input.style.animation = 'shake 0.5s';
      setTimeout(() => {
        input.style.animation = '';
      }, 500);
      return;
    }

    const formData = new FormData();
    formData.append('pdf', file);

    try {
      setUploading(true);
      setError(null);
      const response = await fetch('/api/upload-pdf', {
        method: 'POST',
        body: formData,
      });
      
      if (response.ok) {
        const result = await response.json();
        setBooks(prevBooks => [...prevBooks, result.metadata]);
        handleSuccessMessage('Le livre a été téléchargé avec succès');
        event.target.value = '';
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Erreur lors du téléchargement du PDF');
      }
    } catch (error) {
      console.error('Error uploading PDF:', error);
      setError('Erreur lors du téléchargement du fichier');
    } finally {
      setUploading(false);
    }
  };

  const handleReadBook = (bookId) => {
    navigate(`/chat/${bookId}`);
  };

  const handlePreviewBook = (book) => {
    const button = event.currentTarget;
    const circle = document.createElement('span');
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    const radius = diameter / 2;

    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${event.clientX - button.offsetLeft - radius}px`;
    circle.style.top = `${event.clientY - button.offsetTop - radius}px`;
    circle.classList.add('ripple');

    const ripple = button.getElementsByClassName('ripple')[0];
    if (ripple) {
      ripple.remove();
    }

    button.appendChild(circle);
    setSelectedBook(book);
    setPreviewOpen(true);
  };

  const handleSuccessMessage = (message) => {
    setSuccessMessage(message);
    const snackbar = document.querySelector('.MuiSnackbar-root');
    if (snackbar) {
      snackbar.classList.add('feedback-success');
      setTimeout(() => snackbar.classList.remove('feedback-success'), 500);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography 
          variant={isMobile ? "h4" : "h3"} 
          component="h1" 
          gutterBottom
          sx={{ fontWeight: 'bold', color: theme.palette.primary.main }}
        >
          Bibliothèque Numérique
        </Typography>
        
        <Button
          variant="contained"
          component="label"
          startIcon={<CloudUploadIcon />}
          sx={{ 
            mt: 2,
            px: 3,
            py: 1.5,
            borderRadius: 2,
            backgroundColor: theme.palette.primary.main,
            transition: 'all 0.3s ease-in-out',
            transform: 'scale(1)',
            '&:hover': {
              backgroundColor: theme.palette.primary.dark,
              transform: 'scale(1.05)',
              boxShadow: theme.shadows[4],
            },
            '&:active': {
              transform: 'scale(0.95)',
            },
            ...(uploading && {
              animation: 'pulse 1.5s infinite'
            })
          }}
          disabled={uploading}
        >
          {uploading ? 'Téléchargement...' : 'Ajouter un livre PDF'}
          <input
            type="file"
            hidden
            accept=".pdf"
            onChange={handleFileUpload}
          />
        </Button>
        <Button
          variant="outlined"
          onClick={testFeedbackInteractions}
          sx={{ 
            ml: 2,
            transition: 'all 0.2s ease-in-out',
            '&:hover': {
              transform: 'scale(1.05)',
              backgroundColor: 'rgba(0, 0, 0, 0.04)'
            },
            '&:active': {
              transform: 'scale(0.95)'
            }
          }}
        >
          Tester les Interactions
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Snackbar
        open={!!successMessage}
        autoHideDuration={6000}
        onClose={() => setSuccessMessage('')}
        message={successMessage}
      />

      {isLoading ? (
        <Box sx={{ width: '100%', mt: 4 }}>
          <LinearProgress />
        </Box>
      ) : (
        <Grid container spacing={3}>
          {books.map((book, index) => (
            <Grid item xs={12} sm={6} md={4} key={book.id || index}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 4,
                  }
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography gutterBottom variant="h5" component="h2">
                    {book.title || 'Livre sans titre'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Auteur: {book.author || 'Inconnu'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Pages: {book.pages || '?'}
                  </Typography>
                </CardContent>
                <CardActions sx={{ 
                  padding: 2,
                  justifyContent: 'space-between',
                  backgroundColor: theme.palette.background.paper,
                  borderTop: 1,
                  borderColor: theme.palette.divider
                }}>
                  <Button
                    variant="outlined"
                    size="medium"
                    color="primary"
                    startIcon={<PreviewIcon />}
                    onClick={() => handlePreviewBook(book)}
                    sx={{
                      fontWeight: 'medium',
                      '&:hover': {
                        backgroundColor: theme.palette.primary.light,
                        color: theme.palette.primary.contrastText,
                      }
                    }}
                  >
                    Aperçu
                  </Button>
                  <Button
                    variant="contained"
                    size="medium"
                    color="primary"
                    startIcon={<MenuBookIcon />}
                    onClick={() => handleReadBook(book.id)}
                    sx={{
                      fontWeight: 'medium',
                      '&:hover': {
                        backgroundColor: theme.palette.primary.dark,
                      }
                    }}
                  >
                    Lire
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {!isLoading && books.length === 0 && (
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Typography variant="h6" color="text.secondary">
            Aucun livre dans la bibliothèque
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
            Commencez par télécharger un PDF
          </Typography>
        </Box>
      )}

      {selectedBook && (
        <PDFPreview
          open={previewOpen}
          onClose={() => {
            setPreviewOpen(false);
            setSelectedBook(null);
          }}
          pdfUrl={`/api/books/${selectedBook.filename}`}
          bookTitle={selectedBook.title}
        />
      )}
    </Container>
  );
};

export default HomePage;
