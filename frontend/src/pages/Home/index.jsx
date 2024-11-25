import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Container,
  Grid,
  Card,
  Typography,
  Button,
  Box,
  Alert,
  CardActions,
  Snackbar,
  useTheme,
  useMediaQuery,
  Chip,
  Stack,
  Tooltip,
  CardMedia,
} from "@mui/material";
import PreviewIcon from "@mui/icons-material/Preview";
import ImageIcon from "@mui/icons-material/Image";
import ArticleIcon from "@mui/icons-material/Article";
import PDFPreview from "../../components/features/books/PDFPreview";
import ErrorBoundary from "../../components/common/ErrorBoundary";
import SkeletonLoader from "../../components/common/SkeletonLoader";

// BookStatus Component
const BookStatus = ({ book }) => {
  if (!book) return null;

  return (
    <Tooltip title={`Status: ${book.status}`}>
      <Chip
        label={book.status}
        color={book.status === "completed" ? "success" : "default"}
        size="small"
        sx={{ mb: 1 }}
      />
    </Tooltip>
  );
};

// BookProgress Component
const BookProgress = ({ book }) =>
  book && (
    <Stack direction="row" spacing={1} sx={{ mb: 1 }}>
      <Tooltip title="Pages">
        <Chip
          icon={<ArticleIcon />}
          label={`${book.current_page || 0}/${book.total_pages || 0} pages`}
          size="small"
          variant="outlined"
        />
      </Tooltip>
      <Tooltip title="Images">
        <Chip
          icon={<ImageIcon />}
          label={`${book.processed_images || 0} images`}
          size="small"
          variant="outlined"
        />
      </Tooltip>
      {book.processed_sections > 0 && (
        <Tooltip title="Sections">
          <Chip
            label={`${book.processed_sections} sections`}
            size="small"
            variant="outlined"
          />
        </Tooltip>
      )}
    </Stack>
  );

const BookGrid = ({ books, onReadBook, onPreviewBook, theme }) => {
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  return (
    <Box
      sx={{
        width: "100%",
        pb: 2,
        overflowX: isMobile ? "auto" : "hidden",
        WebkitOverflowScrolling: "touch",
        "& .MuiGrid-container": {
          width: isMobile ? "auto" : "100%",
          flexWrap: isMobile ? "nowrap" : "wrap",
          px: isMobile ? 2 : 0,
        },
      }}
    >
      <Grid container spacing={2}>
        {books.map((book, index) => (
          <Grid
            item
            xs={8}
            sm={6}
            md={4}
            lg={3}
            key={`book-${book?.id || index}`}
            sx={{
              flexShrink: 0,
              width: isMobile ? "calc(150% - 16px)" : "auto",
            }}
          >
            <Card
              sx={{
                height: "100%",
                position: "relative",
                cursor: book?.status === "completed" ? "pointer" : "default",
                transition: "transform 0.2s, box-shadow 0.2s",
                "&:hover": {
                  transform:
                    book?.status === "completed" ? "translateY(-4px)" : "none",
                  boxShadow: book?.status === "completed" ? 6 : 1,
                },
              }}
              onClick={() => book?.status === "completed" && onReadBook(book)}
            >
              <Box sx={{ position: "relative", pt: "140%" }}>
                <CardMedia
                  component="img"
                  image={`/api/books/${book.id}/cover`} // Utilisation de la bonne route API pour obtenir l'image de couverture
                  alt={`Couverture de ${book.title}`}
                  sx={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    width: "100%",
                    height: "100%",
                    objectFit: "cover",
                  }}
                />
                <Box
                  sx={{
                    position: "absolute",
                    bottom: 0,
                    left: 0,
                    right: 0,
                    background:
                      "linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0) 100%)",
                    p: 2,
                    color: "white",
                  }}
                >
                  <Typography
                    variant="h6"
                    sx={{
                      fontWeight: 500,
                      textShadow: "1px 1px 2px rgba(0,0,0,0.5)",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {book?.title || "Sans titre"}
                  </Typography>
                </Box>
              </Box>
              {/* Le bouton aperçu a été retiré conformément aux spécifications */}
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

const HomePage = () => {
  const [books, setBooks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState("");
  const [previewOpen, setPreviewOpen] = useState(false);
  const [selectedBook, setSelectedBook] = useState(null);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const navigate = useNavigate();

  useEffect(() => {
    fetchBooks(); // Initial fetch

    // Set up polling
    const interval = setInterval(fetchBooks, 5000);

    // Cleanup
    return () => clearInterval(interval);
  }, []);

  const fetchBooks = async () => {
    try {
      setError(null);
      setIsLoading(true);

      const response = await fetch("/api/books");

      // Gestion silencieuse des erreurs 404 (pas de livres)
      if (response.status === 404) {
        setBooks([]);
        return;
      }

      // Gestion des erreurs HTTP
      if (!response.ok) {
        const errorText = await response.text();
        // Log uniquement les erreurs serveur
        if (response.status >= 500) {
          console.error(`Server error (${response.status}):`, errorText);
        }
        throw new Error(
          `Impossible de charger la bibliothèque (${response.status})`,
        );
      }

      let data;
      try {
        data = await response.json();
      } catch (parseError) {
        console.error("Invalid JSON response:", parseError);
        throw new Error("Format de réponse invalide");
      }

      // Validation de la structure de données
      if (!data || typeof data !== "object") {
        throw new Error("Structure de données invalide");
      }

      const booksData = Array.isArray(data.books) ? data.books : [];
      
      // Validation et initialisation des données des livres
      const validatedBooks = booksData.map((book = {}) => {
        // Vérification des champs requis
        if (!book.id && !book.filename) {
          console.warn("Book missing required identifier:", book);
          return null;
        }

        return {
          id: book.id || book.filename,
          title: book.title || "Sans titre",
          author: book.author || "Auteur inconnu",
          filename: book.filename || "",
          uploadDate: book.uploadDate || new Date().toISOString(),
          status: book.status || "pending",
          current_page: parseInt(book.current_page, 10) || 0,
          total_pages: parseInt(book.total_pages, 10) || 0,
          processed_sections: parseInt(book.processed_sections, 10) || 0,
          processed_images: parseInt(book.processed_images, 10) || 0,
          error_message: book.error_message || null,
          ...book,
        };
      }).filter(Boolean); // Filtrer les entrées invalides

      setBooks(validatedBooks);
    } catch (error) {
      // Log uniquement les erreurs inattendues
      if (!(error instanceof TypeError || error instanceof SyntaxError)) {
        console.error("Unexpected error fetching books:", error);
      }
      setError(error.message);
      setBooks([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (file.type !== "application/pdf") {
      setError("Please select a valid PDF file");
      return;
    }

    const formData = new FormData();
    formData.append("pdf_files", file);

    try {
      setUploading(true);
      setError(null);

      const response = await fetch("/api/books/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData?.message || `Upload failed: ${response.status}`,
        );
      }

      const result = await response.json();
      setSuccessMessage(result.message || "PDF uploaded successfully");
      event.target.value = "";
      fetchBooks(); // Refresh the book list
    } catch (error) {
      console.error("Error uploading PDF:", error);
      setError(error.message || "Error uploading file");
    } finally {
      setUploading(false);
    }
  };

  const handleReadBook = (book) => {
    if (book?.status !== "completed") {
      setError("This book is not ready for reading yet");
      return;
    }
    navigate(`/books/${book.id}`);  // Redirection vers la page de détails
  };

  const handlePreviewBook = (book) => {
    if (book?.status !== "completed") {
      setError("This book is not ready for preview yet");
      return;
    }
    setSelectedBook(book);
    setPreviewOpen(true);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box
        sx={{
          mb: 4,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: 2,
          p: 2,
          borderRadius: 2,
          bgcolor: "background.paper",
        }}
      >
        <Box>
          <Typography
            variant={isMobile ? "h5" : "h4"}
            sx={{
              fontWeight: 500,
              color: "primary.main",
              mb: 2,
            }}
          >
            Bibliothèque
          </Typography>
        </Box>

        <Box
          sx={{
            display: "flex",
            gap: 2,
            flexWrap: "wrap",
          }}
        >
          {/* Le bouton "Ajouter un livre" a été déplacé vers la page profil */}
        </Box>
      </Box>

      <Snackbar
        open={!!successMessage}
        autoHideDuration={6000}
        onClose={() => setSuccessMessage("")}
        message={successMessage}
      />

      {error && (
        <Alert
          severity="error"
          sx={{ mb: 3 }}
          onClose={() => setError(null)}
          action={
            <Button color="inherit" size="small" onClick={fetchBooks}>
              Retry
            </Button>
          }
        >
          {error}
        </Alert>
      )}

      {isLoading ? (
        <ErrorBoundary fallbackMessage="Error displaying skeleton loader">
          <SkeletonLoader count={6} />
        </ErrorBoundary>
      ) : (
        <>
          {Array.isArray(books) && books.length === 0 && (
            <Box
              sx={{
                textAlign: "center",
                mt: 4,
                p: 4,
                backgroundColor: "background.paper",
                borderRadius: 2,
                border: 1,
                borderColor: "divider",
              }}
            >
              <Typography variant="h6" color="text.secondary">
                No books in library
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
                Start by uploading a PDF
              </Typography>
            </Box>
          )}

          {Array.isArray(books) && books.length > 0 && (
            <ErrorBoundary fallbackMessage="Error displaying book grid">
              <BookGrid
                books={books}
                onReadBook={handleReadBook}
                onPreviewBook={handlePreviewBook}
                theme={theme}
              />
            </ErrorBoundary>
          )}
        </>
      )}

      {selectedBook && (
        <ErrorBoundary fallbackMessage="Error displaying PDF preview">
          <PDFPreview
            open={previewOpen}
            onClose={() => {
              setPreviewOpen(false);
              setSelectedBook(null);
            }}
            pdfUrl={`/api/books/${selectedBook.filename}`}
            bookTitle={selectedBook.title}
          />
        </ErrorBoundary>
      )}
    </Container>
  );
};

export default HomePage;
