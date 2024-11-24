import React from 'react';
import { Box, Typography, Container } from '@mui/material';

const LibraryPage = () => {
  return (
    <Container>
      <Box py={3}>
        <Typography 
          variant="h4"
          gutterBottom
          sx={{ 
            fontWeight: 500,
            color: 'primary.main',
            mb: 3
          }}
        >
          Bibliothèque
        </Typography>
        {/* Contenu de la bibliothèque à ajouter */}
      </Box>
    </Container>
  );
};

export default LibraryPage;
