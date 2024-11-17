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
  Tooltip,
  CircularProgress,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import PreviewIcon from '@mui/icons-material/Preview';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import PDFPreview from './PDFPreview';
import PDFUploadDialog from './PDFUploadDialog';

const MAX_CONCURRENT_PROCESSING = 3;

const HomePage = () => {
  const [books, setBooks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [previewOpen, setPreviewOpen] = useState(false);
  const [selectedBook, setSelectedBook] = useState(null);
  const [processingBooks, setProcessingBooks] = useState(new Set());
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const navigate = useNavigate();

  useEffect(() => {
    fetchBooks();
    const interval = setInterval(() => {
      if (books.some(book => ['queued', 'processing'].includes(book.processing_status))) {
        fetchBooks();
      }
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchBooks = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/books');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setBooks(data);
      
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
      setError(`Error connecting to server: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (uploadedFiles) => {
    try {
      setBooks(prevBooks => [...prevBooks, ...uploadedFiles]);
      setSuccessMessage(`${uploadedFiles.length} file(s) uploaded successfully`);
      await fetchBooks(); // Refresh book list to get latest status
    } catch (error) {
      console.error('Error processing uploaded files:', {
        message: error.message,
        stack: error.stack,
        type: error.name
      });
      setError(`Error processing files: ${error.message}`);
    }
  };

  const handleReadBook = (bookId) => {
    navigate(`/chat/${bookId}`);
  };

  const handlePreviewBook = (book) => {
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
    if (book.processing_status === 'failed') {
      return (
        <Alert 
          severity="error" 
          sx={{ mb: 1 }}
          variant="outlined"
        >
          Processing failed
        </Alert>
      );
    }
    if (book.processing_status === 'processing') {
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
    if (book.processing_status === 'queued') {
      const queuePosition = books.filter(b => 
        b.processing_status === 'queued' && 
        b.upload_time < book.upload_time
      ).length + 1;
      
      return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <HourglassEmptyIcon fontSize="small" />
          <Typography variant="body2" color="text.secondary">
            Queued (Position #{queuePosition})
          </Typography>
        </Box>
      );
    }
    return null;
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
          onClick={() => setUploadDialogOpen(true)}
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
        >
          Upload PDFs
        </Button>

        {processingBooks.size > 0 && (
          <Typography variant="body2" sx={{ mt: 1, color: 'text.secondary' }}>
            {processingBooks.size}/{MAX_CONCURRENT_PROCESSING} processing in progress
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
                    transform: 'translateY(-4px)',
                    boxShadow: 4,
                  }
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography gutterBottom variant="h5" component="h2">
                    {book.title || 'Untitled Book'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Author: {book.author || 'Unknown'}
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
                    disabled={book.processing_status !== 'completed'}
                    sx={{
                      fontWeight: 'medium',
                      '&:hover': {
                        backgroundColor: theme.palette.primary.light,
                        color: theme.palette.primary.contrastText,
                      }
                    }}
                  >
                    Preview
                  </Button>
                  <Button
                    variant="contained"
                    size="medium"
                    color="primary"
                    startIcon={<MenuBookIcon />}
                    onClick={() => handleReadBook(book.id)}
                    disabled={book.processing_status !== 'completed'}
                    sx={{
                      fontWeight: 'medium',
                      '&:hover': {
                        backgroundColor: theme.palette.primary.dark,
                      }
                    }}
                  >
                    Read
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
            No books in the library
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
            Start by uploading a PDF
          </Typography>
        </Box>
      )}

      <PDFUploadDialog
        open={uploadDialogOpen}
        onClose={() => setUploadDialogOpen(false)}
        onUpload={handleFileUpload}
      />

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
