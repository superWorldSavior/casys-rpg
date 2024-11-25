import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Box,
  Typography,
  Button,
  Paper,
  Container,
  CircularProgress,
} from "@mui/material";
import BookIcon from "@mui/icons-material/Book";
import PreviewIcon from "@mui/icons-material/Preview";
import PDFPreview from "../../components/features/books/PDFPreview";

function BookDetailsPage() {
  const { bookId } = useParams();
  const navigate = useNavigate();
  const [book, setBook] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [previewOpen, setPreviewOpen] = useState(false);

  useEffect(() => {
    const fetchBookDetails = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/books/${bookId}`);
        if (!response.ok) {
          throw new Error(
            `Impossible de charger les détails du livre : ${response.statusText}`
          );
        }
        const bookData = await response.json();

        // Ajouter l'URL de la couverture si disponible
        const coverResponse = await fetch(`/api/books/${bookId}/cover`);
        if (coverResponse.ok) {
          bookData.cover_image = coverResponse.url;
        } else {
          bookData.cover_image = null;
        }

        setBook(bookData);
      } catch (err) {
        console.error("Error fetching book details:", err);
        setError(err.message);
        setBook(null);
      } finally {
        setLoading(false);
      }
    };

    fetchBookDetails();
  }, [bookId]);

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="80vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        minHeight="80vh"
        p={3}
      >
        <Typography color="error" variant="h6" gutterBottom>
          {error}
        </Typography>
        <Button
          variant="contained"
          onClick={() => navigate(-1)}
          sx={{ mt: 2 }}
        >
          Retour
        </Button>
      </Box>
    );
  }

  return (
    <Container maxWidth="md">
      <Paper
        elevation={0}
        sx={{
          p: 4,
          mt: 4,
          backgroundColor: "background.paper",
          borderRadius: 2,
        }}
      >
        <Box display="flex" flexDirection={{ xs: "column", md: "row" }} gap={4}>
          <Box
            flex="0 0 300px"
            height="400px"
            bgcolor="grey.100"
            borderRadius={1}
            display="flex"
            justifyContent="center"
            alignItems="center"
          >
            {book && book.cover_image ? (
              <Box
                component="img"
                src={book.cover_image}
                alt={book.title}
                sx={{
                  width: "100%",
                  height: "100%",
                  objectFit: "cover",
                  borderRadius: "8px",
                }}
              />
            ) : (
              <BookIcon
                sx={{
                  fontSize: 60,
                  color: "grey.400",
                }}
              />
            )}
          </Box>

          <Box flex="1">
            <Typography variant="h4" component="h1" gutterBottom>
              {book?.title || "Sans titre"}
            </Typography>
            <Typography variant="subtitle1" color="text.secondary" gutterBottom>
              {book?.author || "Auteur inconnu"}
            </Typography>

            {book?.publisher && (
              <Typography
                variant="subtitle2"
                color="text.secondary"
                gutterBottom
              >
                Édité par {book.publisher}
              </Typography>
            )}

            {book?.publication_date && (
              <Typography
                variant="subtitle2"
                color="text.secondary"
                gutterBottom
              >
                Date de publication:{" "}
                {new Date(book.publication_date).toLocaleDateString()}
              </Typography>
            )}

            {book?.language && (
              <Typography
                variant="subtitle2"
                color="text.secondary"
                gutterBottom
              >
                Langue: {book.language.toUpperCase()}
              </Typography>
            )}

            {book?.total_pages > 0 && (
              <Typography
                variant="subtitle2"
                color="text.secondary"
                gutterBottom
              >
                Nombre de pages: {book.total_pages}
              </Typography>
            )}

            <Typography variant="body1" paragraph sx={{ mt: 3, mb: 3 }}>
              {book?.description || "Aucune description disponible"}
            </Typography>

            <Box sx={{ display: "flex", gap: 2, mt: 3 }}>
              <Button
                variant="contained"
                size="large"
                onClick={() => navigate(`/reader/${bookId}`)}
                sx={{
                  backgroundColor: (theme) => theme.palette.primary.main,
                  color: "white",
                  "&:hover": {
                    backgroundColor: (theme) => theme.palette.primary.dark,
                  },
                }}
              >
                Commencer la lecture
              </Button>

              <Button
                variant="outlined"
                size="large"
                startIcon={<PreviewIcon />}
                onClick={() => setPreviewOpen(true)}
              >
                Aperçu
              </Button>

              <Button
                variant="outlined"
                size="large"
                onClick={() => navigate(-1)}
              >
                Retour
              </Button>
            </Box>
            {previewOpen && (
              <PDFPreview open={previewOpen} onClose={() => setPreviewOpen(false)} />
            )}
          </Box>
        </Box>
      </Paper>
    </Container>
  );
}

export default BookDetailsPage;
