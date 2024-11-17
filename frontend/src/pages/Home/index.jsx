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
  LinearProgress,
  Alert,
  CardActions,
  Snackbar,
  useTheme,
  useMediaQuery,
  Chip,
  CircularProgress,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import PreviewIcon from '@mui/icons-material/Preview';
import ErrorIcon from '@mui/icons-material/Error';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import PDFPreview from '../../components/features/books/PDFPreview';

const MAX_CONCURRENT_PROCESSING = 3; // Maximum number of PDFs to process concurrently

const HomePage = () => {
  const [books, setBooks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [previewOpen, setPreviewOpen] = useState(false);
  const [selectedBook, setSelectedBook] = useState(null);
  const [processingBooks, setProcessingBooks] = useState(new Set());
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const navigate = useNavigate();

  useEffect(() => {
    fetchBooks();
    // Poll for updates every 5 seconds if there are queued or processing books
    const interval = setInterval(() => {
      if (books.some(book => ['queued', 'processing'].includes(book.processing_status))) {
        fetchBooks();
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [books]);

  const fetchBooks = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/books');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setBooks(data);
      
      // Update processing books set
      const currentlyProcessing = new Set(
        data
          .filter(book => book.processing_status === 'processing')
          .map(book => book.id)
      );
      setProcessingBooks(currentlyProcessing);
    } catch (error) {
      console.error('Error fetching books:', {
        message: error.message,
        stack: error.stack,
        type: error.name
      });
      setError(`Erreur de connexion au serveur: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    const invalidFiles = files.filter(file => file.type !== 'application/pdf');
    if (invalidFiles.length > 0) {
      setError('Certains fichiers ne sont pas au format PDF valide');
      return;
    }

    const formData = new FormData();
    files.forEach(file => {
      formData.append('pdf', file);
    });

    try {
      setUploading(true);
      setError(null);
      const response = await fetch('/api/upload-pdf', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setBooks(prevBooks => [...prevBooks, ...result.files]);
      setSuccessMessage(`${files.length} fichier(s) téléchargé(s) avec succès`);
      event.target.value = '';
    } catch (error) {
      console.error('Error uploading PDFs:', {
        message: error.message,
        stack: error.stack,
        type: error.name
      });
      setError(`Erreur lors du téléchargement des fichiers: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleReadBook = (book) => {
    if (!book.available) {
      setError('Ce livre n\'est pas disponible pour la lecture');
      return;
    }
    navigate(`/reader/${book.id}`);
  };

  const handlePreviewBook = (book) => {
    if (!book.available) {
      setError('Ce livre n\'est pas disponible pour l\'aperçu');
      return;
    }
    setSelectedBook(book);
    setPreviewOpen(true);
  };

  const getProcessingInfo = (book) => {
    if (book.processing_status === 'processing') {
      return {
        progress: book.progress || 0,
        currentPage: book.current_page || 0,
        totalPages: book.total_pages || '?'
      };
    }
    return null;
  };

  const getStatusChip = (book) => {
    if (book.available) {
      return (
        <Chip
          icon={<CheckCircleIcon />}
          label="Disponible"
          color="success"
          size="small"
          sx={{ mb: 1 }}
        />
      );
    }
    if (book.processing_status === 'processing') {
      const info = getProcessingInfo(book);
      return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <CircularProgress size={20} />
          <Chip
            label={`Traitement (${info?.currentPage || 0}/${info?.totalPages || '?'})`}
            color="primary"
            size="small"
          />
        </Box>
      );
    }
    if (book.processing_status === 'queued') {
      const queuePosition = books.filter(b => 
        b.processing_status === 'queued' && 
        b.upload_time < book.upload_time
      ).length + 1;
      
      return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <HourglassEmptyIcon fontSize="small" />
          <Chip
            label={`En attente (#${queuePosition})`}
            color="warning"
            size="small"
          />
        </Box>
      );
    }
    return (
      <Chip
        icon={<ErrorIcon />}
        label={book.processing_status === 'failed' ? 'Échec du traitement' : 'Non disponible'}
        color="error"
        size="small"
        sx={{ mb: 1 }}
      />
    );
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
            '&:hover': {
              backgroundColor: theme.palette.primary.dark,
            }
          }}
          disabled={uploading}
        >
          {uploading ? 'Téléchargement...' : 'Ajouter des livres PDF'}
          <input
            type="file"
            hidden
            accept=".pdf"
            multiple
            onChange={handleFileUpload}
          />
        </Button>

        {processingBooks.size > 0 && (
          <Typography variant="body2" sx={{ mt: 1, color: 'text.secondary' }}>
            {processingBooks.size}/{MAX_CONCURRENT_PROCESSING} traitement(s) en cours
          </Typography>
        )}
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
                    transform: book.available ? 'translateY(-4px)' : 'none',
                    boxShadow: book.available ? 4 : 1,
                  },
                  opacity: book.available ? 1 : 0.7,
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
                  {getStatusChip(book)}
                  {book.processing_status === 'processing' && (
                    <LinearProgress 
                      variant="determinate" 
                      value={getProcessingInfo(book)?.progress || 0}
                      sx={{ mt: 1 }}
                    />
                  )}
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
                    disabled={!book.available}
                  >
                    Aperçu
                  </Button>
                  <Button
                    variant="contained"
                    size="medium"
                    color="primary"
                    startIcon={<MenuBookIcon />}
                    onClick={() => handleReadBook(book)}
                    disabled={!book.available}
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
