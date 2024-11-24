import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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

const HomePage = () => {
  const [books, setBooks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const navigate = useNavigate();

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
        setSuccessMessage('Le livre a été téléchargé avec succès');
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

  return (
    <Container maxWidth="lg" sx={{ py: 4, pl: 0 }}>
      <Box
        sx={{
          position: 'relative',
          marginTop: '80px',
          marginRight: '16px',
          textAlign: 'right',
          zIndex: 1
        }}
      >
        <Box sx={{ fontSize: '1rem', color: theme.palette.text.primary }}>Bonjour</Box>
        <Box sx={{ fontSize: '0.875rem', color: theme.palette.text.secondary }}>Vous avez 0 crédits</Box>
        <Box sx={{ display: { xs: 'block', sm: 'none' }, mt: 1 }}>
          <Button 
            variant="contained" 
            size="small"
          >
            Acheter des crédits
          </Button>
        </Box>
      </Box>

      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Box
          component="h1"
          sx={{
            fontSize: isMobile ? '2rem' : '3rem',
            fontWeight: 'bold',
            color: theme.palette.primary.main,
            mb: 2,
            fontFamily: theme.typography.h3.fontFamily
          }}
        >
          Bibliothèque Numérique
        </Box>
        
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
            '&:hover': {
              backgroundColor: theme.palette.primary.dark,
            }
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
        <Grid container spacing={2} sx={{ pl: 0 }}>
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
                  <Box
                    component="h2"
                    sx={{
                      fontSize: '1.5rem',
                      fontWeight: 500,
                      mb: 2,
                      color: theme.palette.text.primary,
                      fontFamily: theme.typography.h5.fontFamily
                    }}
                  >
                    {book.title || 'Livre sans titre'}
                  </Box>
                  <Box
                    sx={{
                      fontSize: '0.875rem',
                      color: theme.palette.text.secondary,
                      mb: 1,
                      fontFamily: theme.typography.body2.fontFamily
                    }}
                  >
                    Auteur: {book.author || 'Inconnu'}
                  </Box>
                  <Box
                    sx={{
                      fontSize: '0.875rem',
                      color: theme.palette.text.secondary,
                      fontFamily: theme.typography.body2.fontFamily
                    }}
                  >
                    Pages: {book.pages || '?'}
                  </Box>
                </CardContent>
                <CardActions sx={{ 
                  padding: 2,
                  backgroundColor: theme.palette.background.paper,
                  borderTop: 1,
                  borderColor: theme.palette.divider
                }}>
                  <Button
                    variant="contained"
                    size="medium"
                    color="primary"
                    startIcon={<MenuBookIcon />}
                    onClick={() => handleReadBook(book.id)}
                    sx={{
                      width: '100%',
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
          <Box
            sx={{
              fontSize: '1.25rem',
              fontWeight: 500,
              color: theme.palette.text.secondary,
              fontFamily: theme.typography.h6.fontFamily
            }}
          >
            Aucun livre dans la bibliothèque
          </Box>
          <Box
            sx={{
              fontSize: '1rem',
              color: theme.palette.text.secondary,
              mt: 1,
              fontFamily: theme.typography.body1.fontFamily
            }}
          >
            Commencez par télécharger un PDF
          </Box>
        </Box>
      )}

      
    </Container>
  );
};

export default HomePage;
