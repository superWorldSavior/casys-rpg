import React, { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { Dialog, DialogContent, IconButton, Box, Typography, Button } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import NavigateBeforeIcon from '@mui/icons-material/NavigateBefore';

// Set up PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

const PDFPreview = ({ open, onClose, pdfUrl, bookTitle }) => {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [error, setError] = useState(null);

  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
    setError(null);
  };

  const onDocumentLoadError = (error) => {
    setError('Erreur lors du chargement du PDF');
    console.error('Error loading PDF:', error);
  };

  const changePage = (offset) => {
    setPageNumber(prevPageNumber => {
      const newPageNumber = prevPageNumber + offset;
      return Math.min(Math.max(1, newPageNumber), numPages);
    });
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      TransitionProps={{
        timeout: 300,
      }}
      PaperProps={{
        sx: {
          height: '90vh',
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          transform: 'scale(1)',
          transition: 'transform 0.2s ease-in-out',
          '&:hover': {
            transform: 'scale(1.01)'
          }
        }
      }}
    >
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        p: 2,
        borderBottom: 1,
        borderColor: 'divider'
      }}>
        <Typography variant="h6">{bookTitle}</Typography>
        <IconButton onClick={onClose}>
          <CloseIcon />
        </IconButton>
      </Box>

      <DialogContent sx={{ 
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        overflow: 'hidden'
      }}>
        {error ? (
          <Typography color="error" sx={{ mt: 2 }}>{error}</Typography>
        ) : (
          <>
            <Document
              file={pdfUrl}
              onLoadSuccess={onDocumentLoadSuccess}
              onLoadError={onDocumentLoadError}
              loading={<Typography>Chargement du PDF...</Typography>}
            >
              <Page 
                pageNumber={pageNumber}
                width={window.innerWidth * 0.7}
                loading={<Typography>Chargement de la page...</Typography>}
              />
            </Document>

            <Box sx={{ 
              mt: 2,
              display: 'flex',
              alignItems: 'center',
              gap: 2
            }}>
              <Button
                startIcon={<NavigateBeforeIcon />}
                onClick={() => changePage(-1)}
                disabled={pageNumber <= 1}
                sx={{
                  transition: 'all 0.2s ease-in-out',
                  '&:not(:disabled):hover': {
                    transform: 'translateX(-2px)',
                    backgroundColor: 'primary.light'
                  },
                  '&:active': {
                    transform: 'translateX(-1px)'
                  }
                }}
              >
                Précédent
              </Button>
              <Typography>
                Page {pageNumber} sur {numPages}
              </Typography>
              <Button
                endIcon={<NavigateNextIcon />}
                onClick={() => changePage(1)}
                disabled={pageNumber >= numPages}
                sx={{
                  transition: 'all 0.2s ease-in-out',
                  '&:not(:disabled):hover': {
                    transform: 'translateX(2px)',
                    backgroundColor: 'primary.light'
                  },
                  '&:active': {
                    transform: 'translateX(1px)'
                  }
                }}
              >
                Suivant
              </Button>
            </Box>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default PDFPreview;
