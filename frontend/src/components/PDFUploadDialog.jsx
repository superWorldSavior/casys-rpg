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
  styled
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
    console.log("Files dropped:", acceptedFiles);
    const pdfFiles = acceptedFiles.filter(file => file.type === 'application/pdf');
    console.log("PDF files:", pdfFiles);
    
    if (pdfFiles.length !== acceptedFiles.length) {
      console.warn("Some files were rejected due to invalid type");
      setErrors(prev => ({
        ...prev,
        format: 'Some files were rejected. Only PDF files are allowed.'
      }));
    }
    
    setSelectedFiles(prev => {
      const newFiles = pdfFiles.filter(file => 
        !prev.some(existing => existing.name === file.name)
      );
      console.log("New files to be added:", newFiles);
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
    console.log("Removing file:", fileName);
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

    console.log("Starting upload process");
    console.log("Selected files:", selectedFiles);
    
    setIsUploading(true);
    setErrors({});

    const formData = new FormData();
    selectedFiles.forEach(file => {
      console.log(`Adding file to FormData: ${file.name}`);
      formData.append('pdfs', file);
    });

    console.log('FormData contents:', Array.from(formData.entries()));

    try {
      console.log('Request method:', 'POST');
      console.log('Request URL:', '/api/upload-pdfs');
      console.log('Request headers:', {
        // No custom headers needed as FormData sets the correct Content-Type
      });
      
      const response = await fetch('/api/upload-pdfs', {
        method: 'POST',
        body: formData,
      });

      console.log("Response received:", response.status);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Upload failed with status ${response.status}`);
      }

      const result = await response.json();
      console.log("Upload successful:", result);
      onUpload(result.files);
      handleClose();
    } catch (error) {
      console.error("Upload error:", {
        message: error.message,
        stack: error.stack,
        type: error.name
      });
      setErrors(prev => ({
        ...prev,
        general: error.message || 'Failed to upload files'
      }));
    } finally {
      setIsUploading(false);
    }
  };

  const handleClose = () => {
    if (!isUploading) {
      console.log("Closing upload dialog");
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
              : 'Drag and drop PDF files here, or click to select files'}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            You can select multiple files at once
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
                  <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                    {file.name}
                  </Typography>
                  <IconButton 
                    size="small" 
                    onClick={() => removeFile(file.name)}
                    disabled={isUploading}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </FileHeader>
                <Box sx={{ width: '100%', position: 'relative' }}>
                  <LinearProgress
                    variant="determinate"
                    value={uploadProgress[file.name] || 0}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                  <Typography
                    variant="caption"
                    sx={{
                      position: 'absolute',
                      right: 0,
                      top: -18,
                    }}
                  >
                    {uploadProgress[file.name] || 0}%
                  </Typography>
                </Box>
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
          {isUploading ? 'Uploading...' : 'Upload'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default PDFUploadDialog;