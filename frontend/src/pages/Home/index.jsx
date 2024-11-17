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
import PDFPreview from '../../components/features/books/PDFPreview';

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

  useEffect(() => {
    fetchBooks();
    const interval = setInterval(() => {
      if (books?.some(book => book?.processing_status === 'processing')) {
        fetchBooks();
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [books]);

  const fetchBooks = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/books');
      if (!response.ok) throw new Error('Failed to fetch books');
      const data = await response.json();
      setBooks(data || []);
    } catch (error) {
      console.error('Error fetching books:', error);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      setError('Only PDF files are allowed');
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
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Upload failed with status ${response.status}`);
      }

      const result = await response.json();
      setBooks(prevBooks => [...prevBooks, result.file]);
      setSuccessMessage(`${file.name} uploaded successfully`);
      await fetchBooks(); // Refresh book list to get latest status
      event.target.value = '';
    } catch (error) {
      console.error('Error uploading PDF:', {
        message: error.message,
        stack: error.stack,
        type: error.name
      });
      setError(`Error uploading file: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleReadBook = (book) => {
    if (!book?.available) {
      setError('This book is not yet available for reading');
      return;
    }
    navigate(`/reader/${book.id}`);
  };

  const handlePreviewBook = (book) => {
    if (!book?.available) {
      setError('This book is not yet available for preview');
      return;
    }
    setSelectedBook(book);
    setPreviewOpen(true);
  };

  const getProcessingInfo = (book) => {
    if (book?.processing_status === 'processing') {
      return {
        progress: book.progress || 0,
        currentPage: book.current_page || 0,
        totalPages: book.total_pages || '?'
      };
    }
    return null;
  };

  const getStatusChip = (book) => {
    if (book?.available) {
      return (
        <Chip
          icon={<CheckCircleIcon />}
          label="Available"
          color="success"
          size="small"
          sx={{ mb: 1 }}
        />
      );
    }
    if (book?.processing_status === 'processing') {
      const info = getProcessingInfo(book);
      return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <CircularProgress size={20} />
          <Typography variant="body2" color="text.secondary">
            Processing ({info?.currentPage || 0}/{info?.totalPages || '?'})
          </Typography>
        </Box>
      );
    }
    return (
      <Chip
        icon={<ErrorIcon />}
        label={book?.processing_status === 'failed' ? 'Processing failed' : 'Not available'}
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
          Digital Library
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
          {uploading ? 'Uploading...' : 'Upload PDF'}
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
        <Grid container spacing={3}>
          {books?.filter(book => book)?.map((book, index) => (
            <Grid item xs={12} sm={6} md={4} key={book?.id || index}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: book?.available ? 'translateY(-4px)' : 'none',
                    boxShadow: book?.available ? 4 : 1,
                  },
                  opacity: book?.available ? 1 : 0.7,
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography gutterBottom variant="h5" component="h2">
                    {book?.title || 'Untitled Book'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Author: {book?.author || 'Unknown'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Pages: {book?.pages || '?'}
                  </Typography>
                  {getStatusChip(book)}
                  {book?.processing_status === 'processing' && (
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
                    disabled={!book?.available}
                  >
                    Preview
                  </Button>
                  <Button
                    variant="contained"
                    size="medium"
                    color="primary"
                    startIcon={<MenuBookIcon />}
                    onClick={() => handleReadBook(book)}
                    disabled={!book?.available}
                  >
                    Read
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {!isLoading && books?.length === 0 && (
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Typography variant="h6" color="text.secondary">
            No books in the library
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
            Start by uploading a PDF
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
          bookTitle={selectedBook?.title}
        />
      )}
    </Container>
  );
};

export default HomePage;
