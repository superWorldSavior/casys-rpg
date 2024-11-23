import React from 'react';
import { Box, Typography, Container } from '@mui/material';

const LibraryPage = () => {
  return (
    <Container>
      <Box py={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          Bibliothèque
        </Typography>
        {/* Contenu de la bibliothèque à ajouter */}
      </Box>
    </Container>
  );
};

export default LibraryPage;
