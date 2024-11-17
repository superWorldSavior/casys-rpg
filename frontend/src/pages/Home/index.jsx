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
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import PreviewIcon from '@mui/icons-material/Preview';
import ErrorIcon from '@mui/icons-material/Error';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import PDFPreview from '../../components/features/books/PDFPreview';

const HomePage = () => {
  const [books, setBooks] = useState([]); // Initialize as empty array
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
    fetchBooks(); // Initial fetch
    
    // Set up polling
    const interval = setInterval(fetchBooks, 5000);
    
    // Cleanup
    return () => clearInterval(interval);
  }, []);

  const fetchBooks = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await fetch('/api/books');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Validate the response structure
      if (!data || typeof data !== 'object') {
        throw new Error('Invalid API response format');
      }
      
      // Ensure books is an array, even if empty
      const booksData = Array.isArray(data.books) ? data.books : [];
      
      // Map and validate each book object
      const validatedBooks = booksData.map((book = {}) => ({
        id: book.id || book.filename || '',
        title: book.title || 'Untitled Book',
        author: book.author || 'Unknown',
        pages: book.total_pages || '?',
        filename: book.filename || '',
        status: book.status || 'unknown'
      }));
      
      setBooks(validatedBooks);
    } catch (error) {
      console.error('Error fetching books:', error);
      setError(error.message || 'Error connecting to server');
      setBooks([]); // Reset to empty array on error
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      setError('Please select a valid PDF file');
      return;
    }

    const formData = new FormData();
    formData.append('pdf_files', file);

    try {
      setUploading(true);
      setError(null);
      
      const response = await fetch('/api/books/upload', {
        method: 'POST',
        body: formData,
      });
      
      const result = await response.json();
      
      if (!response.ok || !result) {
        throw new Error(result?.message || 'Error uploading PDF');
      }

      // Ensure books array exists in response
      const newBooks = Array.isArray(result.books) ? result.books : [];
      
      // Map and validate new books
      const validatedNewBooks = newBooks.map((book = {}) => ({
        id: book.id || book.filename || '',
        title: book.title || 'Untitled Book',
        author: book.author || 'Unknown',
        pages: book.total_pages || '?',
        filename: book.filename || '',
        status: book.status || 'processing'
      }));

      // Update books state, ensuring it remains an array
      setBooks(prevBooks => [...(Array.isArray(prevBooks) ? prevBooks : []), ...validatedNewBooks]);
      setSuccessMessage(result.message || 'PDF uploaded successfully');
      event.target.value = ''; // Reset file input
    } catch (error) {
      console.error('Error uploading PDF:', error);
      setError(error.message || 'Error uploading file');
    } finally {
      setUploading(false);
    }
  };

  const handleReadBook = (book) => {
    if (book?.status !== 'completed') {
      setError('This book is not ready for reading yet');
      return;
    }
    navigate(`/reader/${book.filename}`);
  };

  const handlePreviewBook = (book) => {
    if (book?.status !== 'completed') {
      setError('This book is not ready for preview yet');
      return;
    }
    setSelectedBook(book);
    setPreviewOpen(true);
  };

  const getStatusChip = (book) => {
    if (!book) return null;

    const statusConfig = {
      completed: {
        icon: <CheckCircleIcon />,
        label: 'Ready to Read',
        color: 'success'
      },
      processing: {
        icon: <HourglassEmptyIcon />,
        label: 'Processing',
        color: 'warning'
      },
      failed: {
        icon: <ErrorIcon />,
        label: 'Failed',
        color: 'error'
      }
    };

    // Use the actual status from the book
    const config = statusConfig[book.status] || {
      icon: <HourglassEmptyIcon />,
      label: book.status || 'Unknown',
      color: 'default'
    };

    return (
      <Chip
        icon={config.icon}
        label={config.label}
        color={config.color}
        size="small"
        sx={{ mb: 1 }}
      />
    );
  };

  // Loading state
  if (isLoading && books.length === 0) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ width: '100%', mt: 4 }}>
          <LinearProgress />
        </Box>
      </Container>
    );
  }

  // Error state
  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert 
          severity="error" 
          sx={{ mb: 3 }} 
          onClose={() => setError(null)}
          action={
            <Button color="inherit" size="small" onClick={() => window.location.reload()}>
              Retry
            </Button>
          }
        >
          {error}
        </Alert>
      </Container>
    );
  }

  // Main content
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
          {uploading ? 'Uploading...' : 'Add PDF Book'}
          <input
            type="file"
            hidden
            accept=".pdf"
            onChange={handleFileUpload}
          />
        </Button>
      </Box>

      <Snackbar
        open={!!successMessage}
        autoHideDuration={6000}
        onClose={() => setSuccessMessage('')}
        message={successMessage}
      />

      {Array.isArray(books) && books.length === 0 && (
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Typography variant="h6" color="text.secondary">
            No books in library
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
            Start by uploading a PDF
          </Typography>
        </Box>
      )}

      {Array.isArray(books) && books.length > 0 && (
        <Grid container spacing={3}>
          {books.map((book, index) => (
            <Grid item xs={12} sm={6} md={4} key={`book-${book?.id || index}`}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: book?.status === 'completed' ? 'translateY(-4px)' : 'none',
                    boxShadow: book?.status === 'completed' ? 4 : 1,
                  },
                  opacity: book?.status === 'completed' ? 1 : 0.8,
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
                    disabled={book?.status !== 'completed'}
                  >
                    Preview
                  </Button>
                  <Button
                    variant="contained"
                    size="medium"
                    color="primary"
                    startIcon={<MenuBookIcon />}
                    onClick={() => handleReadBook(book)}
                    disabled={book?.status !== 'completed'}
                  >
                    Read
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
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
