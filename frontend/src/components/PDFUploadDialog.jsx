import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  List,
  ListItem,
  LinearProgress,
  Alert,
  IconButton,
  styled,
  CircularProgress
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import DeleteIcon from '@mui/icons-material/Delete';

const DropZone = styled(Box)(({ theme, isDragActive }) => ({
  border: `2px dashed ${isDragActive ? theme.palette.primary.main : theme.palette.grey[400]}`,
  borderRadius: theme.shape.borderRadius,
  padding: theme.spacing(4),
  textAlign: 'center',
  cursor: 'pointer',
  backgroundColor: isDragActive ? theme.palette.action.hover : theme.palette.background.paper,
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
  }
}));

const FileItem = styled(ListItem)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'stretch',
  padding: theme.spacing(1),
  gap: theme.spacing(1),
  border: `1px solid ${theme.palette.divider}`,
  borderRadius: theme.shape.borderRadius,
  marginBottom: theme.spacing(1),
}));

const FileHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  width: '100%',
}));

const PDFUploadDialog = ({ open, onClose, onUpload }) => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState({});
  const [errors, setErrors] = useState({});
  const [isUploading, setIsUploading] = useState(false);

  const onDrop = useCallback((acceptedFiles) => {
    const pdfFiles = acceptedFiles.filter(file => file.type === 'application/pdf');
    
    if (pdfFiles.length !== acceptedFiles.length) {
      setErrors(prev => ({
        ...prev,
        format: 'Some files were rejected. Only PDF files are allowed.'
      }));
    }
    
    setSelectedFiles(prev => {
      const newFiles = pdfFiles.filter(file => 
        !prev.some(existing => existing.name === file.name)
      );
      return [...prev, ...newFiles];
    });
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: true
  });

  const removeFile = (fileName) => {
    setSelectedFiles(prev => prev.filter(file => file.name !== fileName));
    setUploadProgress(prev => {
      const newProgress = { ...prev };
      delete newProgress[fileName];
      return newProgress;
    });
    setErrors(prev => {
      const newErrors = { ...prev };
      delete newErrors[fileName];
      return newErrors;
    });
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0 || isUploading) return;

    setIsUploading(true);
    setErrors({});

    const formData = new FormData();
    selectedFiles.forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();

      if (!response.ok) {
        let errorMessage = 'Upload failed';
        
        switch (response.status) {
          case 400:
            errorMessage = data.error || 'Invalid request. Please check your files.';
            break;
          case 413:
            errorMessage = 'Files are too large. Please try smaller files.';
            break;
          case 415:
            errorMessage = 'Unsupported file type. Only PDF files are allowed.';
            break;
          case 500:
            errorMessage = 'Server error. Please try again later.';
            break;
          default:
            errorMessage = data.error || 'Failed to upload files. Please try again.';
        }
        
        throw new Error(errorMessage);
      }

      if (data.errors && data.errors.length > 0) {
        // Handle partial success
        data.errors.forEach(error => {
          setErrors(prev => ({
            ...prev,
            [error.filename]: error.error
          }));
        });
      }
      
      if (data.files && data.files.length > 0) {
        onUpload(data.files);
        handleClose();
      } else {
        throw new Error('No files were successfully processed');
      }
    } catch (error) {
      setErrors(prev => ({
        ...prev,
        general: error.message || 'Failed to upload files. Please try again.'
      }));
    } finally {
      setIsUploading(false);
    }
  };

  const handleClose = () => {
    if (!isUploading) {
      setSelectedFiles([]);
      setUploadProgress({});
      setErrors({});
      onClose();
    }
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleClose} 
      maxWidth="md" 
      fullWidth
      PaperProps={{
        sx: { minHeight: '60vh' }
      }}
    >
      <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        Upload PDF Files
        <IconButton onClick={handleClose} disabled={isUploading}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogContent>
        <DropZone {...getRootProps()} isDragActive={isDragActive}>
          <input {...getInputProps()} />
          <Typography variant="body1">
            {isDragActive
              ? 'Drop the PDF files here...'
              : 'Drag and drop multiple PDF files here, or click to select files'}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            All files will be processed in batch
          </Typography>
        </DropZone>

        {errors.format && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {errors.format}
          </Alert>
        )}

        {errors.general && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {errors.general}
          </Alert>
        )}

        {selectedFiles.length > 0 && (
          <List sx={{ mt: 2 }}>
            {selectedFiles.map((file) => (
              <FileItem key={file.name}>
                <FileHeader>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {isUploading && <CircularProgress size={16} />}
                    <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                      {file.name}
                    </Typography>
                  </Box>
                  <IconButton 
                    size="small" 
                    onClick={() => removeFile(file.name)}
                    disabled={isUploading}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </FileHeader>
                {errors[file.name] && (
                  <Alert severity="error" sx={{ width: '100%' }}>
                    {errors[file.name]}
                  </Alert>
                )}
              </FileItem>
            ))}
          </List>
        )}
      </DialogContent>
      <DialogActions sx={{ p: 2, gap: 1 }}>
        <Typography variant="caption" color="text.secondary">
          {selectedFiles.length} file(s) selected
        </Typography>
        <Box sx={{ flex: 1 }} />
        <Button 
          onClick={handleClose}
          disabled={isUploading}
        >
          Cancel
        </Button>
        <Button
          onClick={handleUpload}
          disabled={selectedFiles.length === 0 || isUploading}
          variant="contained"
        >
          {isUploading ? `Uploading ${selectedFiles.length} files...` : 'Upload All'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default PDFUploadDialog;
