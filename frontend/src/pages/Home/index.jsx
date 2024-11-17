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
  Alert,
  CardActions,
  Snackbar,
  useTheme,
  useMediaQuery,
  Chip,
  Stack,
  Tooltip,
  CardMedia,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import PreviewIcon from '@mui/icons-material/Preview';
import ImageIcon from '@mui/icons-material/Image';
import ArticleIcon from '@mui/icons-material/Article';
import PDFPreview from '../../components/features/books/PDFPreview';
import ErrorBoundary from '../../components/common/ErrorBoundary';
import SkeletonLoader from '../../components/common/SkeletonLoader';

// BookGrid Component
const BookGrid = ({ books, onReadBook, onPreviewBook, theme }) => (
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
          }}
        >
          {book.cover_image && (
            <CardMedia
              component="img"
              height="200"
              image={book.cover_image}
              alt={`Cover for ${book.title}`}
              sx={{ objectFit: 'contain', p: 1 }}
            />
          )}
          <CardContent sx={{ flexGrow: 1 }}>
            <Typography gutterBottom variant="h5" component="h2">
              {book?.title || 'Untitled Book'}
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Author: {book?.author || 'Unknown'}
            </Typography>
            <BookStatus book={book} />
            <BookProgress book={book} />
            {book.error_message && (
              <Typography variant="body2" color="error" sx={{ mt: 1 }}>
                Error: {book.error_message}
              </Typography>
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
              onClick={() => onPreviewBook(book)}
              disabled={book?.status !== 'completed'}
            >
              Preview
            </Button>
            <Button
              variant="contained"
              size="medium"
              color="primary"
              startIcon={<MenuBookIcon />}
              onClick={() => onReadBook(book)}
              disabled={book?.status !== 'completed'}
            >
              Read
            </Button>
          </CardActions>
        </Card>
      </Grid>
    ))}
  </Grid>
);

// BookStatus Component
const BookStatus = ({ book }) => (
  book && (
    <Tooltip title={`Status: ${book.status}`}>
      <Chip
        label={book.status}
        color={book.status === 'completed' ? 'success' : 'default'}
        size="small"
        sx={{ mb: 1 }}
      />
    </Tooltip>
  )
);

// BookProgress Component
const BookProgress = ({ book }) => (
  book && (
    <Stack direction="row" spacing={1} sx={{ mb: 1 }}>
      <Tooltip title="Pages">
        <Chip
          icon={<ArticleIcon />}
          label={`${book.current_page || 0}/${book.total_pages || 0} pages`}
          size="small"
          variant="outlined"
        />
      </Tooltip>
      <Tooltip title="Images">
        <Chip
          icon={<ImageIcon />}
          label={`${book.processed_images || 0} images`}
          size="small"
          variant="outlined"
        />
      </Tooltip>
      {book.processed_sections > 0 && (
        <Tooltip title="Sections">
          <Chip
            label={`${book.processed_sections} sections`}
            size="small"
            variant="outlined"
          />
        </Tooltip>
      )}
    </Stack>
  )
);

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
    fetchBooks(); // Initial fetch
    
    // Set up polling
    const interval = setInterval(fetchBooks, 5000);
    
    // Cleanup
    return () => clearInterval(interval);
  }, []);

  const fetchBooks = async () => {
    try {
      setError(null);
      
      const response = await fetch('/api/books');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (!data || typeof data !== 'object') {
        throw new Error('Invalid API response format');
      }
      
      const booksData = Array.isArray(data.books) ? data.books : [];
      
      // Validate and initialize book data with all available metadata
      const validatedBooks = booksData.map((book = {}) => ({
        id: book.id || book.filename || '',
        title: book.title || 'Untitled Book',
        author: book.author || 'Unknown',
        filename: book.filename || '',
        uploadDate: book.uploadDate,
        status: book.status || 'unknown',
        current_page: book.current_page || 0,
        total_pages: book.total_pages || 0,
        processed_sections: book.processed_sections || 0,
        processed_images: book.processed_images || 0,
        error_message: book.error_message || null,
        cover_image: book.cover_image || null,
        ...book
      }));
      
      setBooks(validatedBooks);
    } catch (error) {
      console.error('Error fetching books:', error);
      setError(error.message || 'Error connecting to server');
      setBooks([]);
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

      setSuccessMessage(result.message || 'PDF uploaded successfully');
      event.target.value = '';
      fetchBooks(); // Refresh the book list
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
        
        <ErrorBoundary fallbackMessage="Error in file upload component">
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
        </ErrorBoundary>
      </Box>

      <Snackbar
        open={!!successMessage}
        autoHideDuration={6000}
        onClose={() => setSuccessMessage('')}
        message={successMessage}
      />

      {error && (
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
      )}

      {isLoading ? (
        <ErrorBoundary fallbackMessage="Error displaying skeleton loader">
          <SkeletonLoader count={6} />
        </ErrorBoundary>
      ) : (
        <>
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
            <ErrorBoundary fallbackMessage="Error displaying book grid">
              <BookGrid 
                books={books}
                onReadBook={handleReadBook}
                onPreviewBook={handlePreviewBook}
                theme={theme}
              />
            </ErrorBoundary>
          )}
        </>
      )}

      {selectedBook && (
        <ErrorBoundary fallbackMessage="Error displaying PDF preview">
          <PDFPreview
            open={previewOpen}
            onClose={() => {
              setPreviewOpen(false);
              setSelectedBook(null);
            }}
            pdfUrl={`/api/books/${selectedBook.filename}`}
            bookTitle={selectedBook.title}
          />
        </ErrorBoundary>
      )}
    </Container>
  );
};

export default HomePage;
