import React from 'react';
import { useParams } from 'react-router-dom';
import { Box, Typography, Container } from '@mui/material';

const Chat = () => {
  const { bookId } = useParams();

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Chat Interface
        </Typography>
        <Typography variant="body1">
          Book ID: {bookId}
        </Typography>
      </Box>
    </Container>
  );
};

export default Chat;
