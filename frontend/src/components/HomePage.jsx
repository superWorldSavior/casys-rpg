import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  IconButton,
  Input,
  Alert,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import MenuBookIcon from '@mui/icons-material/MenuBook';

const HomePage = () => {
  const [books, setBooks] = useState([]);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);

  // Fetch books when component mounts
  useEffect(() => {
    const fetchBooks = async () => {
      try {
        const response = await fetch('/api/books');
        if (response.ok) {
          const data = await response.json();
          setBooks(data);
        } else {
          setError('Error fetching books');
        }
      } catch (error) {
        console.error('Error fetching books:', error);
        setError('Error connecting to server');
      }
    };

    fetchBooks();
  }, []);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      const formData = new FormData();
      formData.append('pdf', file);

      try {
        setError(null);
        const response = await fetch('/api/upload-pdf', {
          method: 'POST',
          body: formData,
        });
        
        if (response.ok) {
          const result = await response.json();
          setBooks([...books, result.metadata]);
        } else {
          const errorData = await response.json();
          setError(errorData.error || 'Error uploading PDF');
        }
      } catch (error) {
        console.error('Error uploading PDF:', error);
        setError('Error uploading file');
      }
    } else {
      setError('Please select a valid PDF file');
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Bibliothèque Numérique
        </Typography>
        <Button
          variant="contained"
          component="label"
          startIcon={<CloudUploadIcon />}
          sx={{ mt: 2 }}
        >
          Ajouter un livre PDF
          <input
            type="file"
            hidden
            accept=".pdf"
            onChange={handleFileUpload}
          />
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {books.map((book, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography gutterBottom variant="h5" component="h2">
                  {book.title || 'Livre sans titre'}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Auteur: {book.author || 'Inconnu'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Pages: {book.pages}
                </Typography>
                <IconButton color="primary" sx={{ mt: 2 }}>
                  <MenuBookIcon />
                </IconButton>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default HomePage;
