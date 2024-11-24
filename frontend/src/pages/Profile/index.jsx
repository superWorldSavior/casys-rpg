import React, { useState } from 'react';
import { Typography, Container, Button, Box, Alert, Snackbar } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

const ProfilePage = () => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');

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
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData?.message || `Upload failed: ${response.status}`);
      }

      const result = await response.json();
      setSuccessMessage(result.message || 'PDF uploaded successfully');
      event.target.value = '';
    } catch (error) {
      console.error('Error uploading PDF:', error);
      setError(error.message || 'Error uploading file');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Container>
      <Box sx={{ mb: 4 }}>
        <Typography 
          variant="h4" 
          gutterBottom
          sx={{ 
            fontWeight: 500,
            color: 'primary.main',
            mb: 3
          }}
        >
          Profil
        </Typography>

        <Box sx={{ mt: 4 }}>
          <Button
            variant="contained"
            color="primary"
            component="label"
            startIcon={<CloudUploadIcon />}
            disabled={uploading}
          >
            {uploading ? 'Uploading...' : 'Ajouter un livre'}
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

        {error && (
          <Alert 
            severity="error" 
            sx={{ mt: 3 }} 
            onClose={() => setError(null)}
          >
            {error}
          </Alert>
        )}
      </Box>
    </Container>
  );
};

export default ProfilePage;
