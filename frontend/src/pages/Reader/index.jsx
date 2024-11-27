import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Box,
  LinearProgress,
  IconButton,
  useTheme,
  CircularProgress,
  Typography,
  Button,
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import KindleReader from "../../components/features/reader/KindleReader";
import CommandInput from "../../components/features/reader/CommandInput";
import TableOfContents from "../../components/features/reader/TableOfContents";

const DEFAULT_THEME = {
  fontFamily: '"Bookerly", "Georgia", serif',
  fontSize: "1.2rem",
  textColor: "#2c2c2c",
  backgroundColor: "#F6F3E9",
  lineHeight: "1.8",
};

const DARK_THEME = {
  ...DEFAULT_THEME,
  textColor: "#e1e1e1",
  backgroundColor: "#131516",
};

function ReaderPage() {
  const { bookId } = useParams();
  const navigate = useNavigate();
  const muiTheme = useTheme();

  const [currentChapter, setCurrentChapter] = useState('');
  const [currentChapterIndex, setCurrentChapterIndex] = useState(0);
  const [totalChapters, setTotalChapters] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [theme, setTheme] = useState(() =>
    muiTheme.palette.mode === "dark" ? DARK_THEME : DEFAULT_THEME,
  );

  useEffect(() => {
    setTheme(muiTheme.palette.mode === "dark" ? DARK_THEME : DEFAULT_THEME);
  }, [muiTheme.palette.mode]);

  const saveReadingProgress = (index, position = 0) => {
    if (!bookId) return;

    try {
      localStorage.setItem(`reader-progress-${bookId}`, JSON.stringify({
        chapterIndex: index,
        timestamp: Date.now(),
        total: totalChapters,
        bookId,
        lastPosition: position
      }));
    } catch (storageErr) {
      console.warn("Erreur lors de la sauvegarde de la progression:", storageErr);
    }
  };

  const fetchChapter = async (index) => {
    if (!bookId) {
      setError("Identifiant du livre manquant");
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Clean up book ID and ensure .pdf extension
      const cleanBookId = bookId.endsWith('.pdf') ? bookId : `${bookId}.pdf`;
      const apiUrl = `/api/books/${cleanBookId}/chapters/${index}`;
      
      const response = await fetch(apiUrl, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'include'
      });

      if (!response.ok) {
        let errorMessage;
        try {
          const errorData = await response.json();
          if (response.status === 404) {
            errorMessage = "Ce chapitre n'est pas disponible. Le livre n'a peut-être pas été correctement traité.";
          } else if (response.status === 500) {
            errorMessage = "Une erreur est survenue lors de la lecture du chapitre. Veuillez réessayer.";
            console.error('Server error details:', errorData);
          } else {
            errorMessage = errorData.error || errorData.message || `Erreur serveur: ${response.status}`;
          }
        } catch (parseError) {
          console.error('Error parsing error response:', parseError);
          errorMessage = `Erreur serveur: ${response.status} ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      
      if (!data || !data.chapter) {
        throw new Error('Le contenu du chapitre est manquant ou invalide');
      }

      if (typeof data.chapter !== 'string' || data.chapter.trim().length === 0) {
        throw new Error('Le contenu du chapitre est vide ou dans un format invalide');
      }

      setCurrentChapter(data.chapter);
      setCurrentChapterIndex(data.index);
      setTotalChapters(data.total);
      setError(null);
      
      // Save reading progress
      saveReadingProgress(data.index);

    } catch (err) {
      console.error("Erreur fetchChapter:", err);
      setError(err.message || "Une erreur est survenue lors du chargement du chapitre. Veuillez réessayer.");
      setCurrentChapter('');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    let isMounted = true;

    const initializeReader = async () => {
      if (!bookId) {
        if (isMounted) {
          setError("Identifiant du livre manquant");
          setIsLoading(false);
        }
        return;
      }

      try {
        if (isMounted) {
          setIsLoading(true);
          setError(null);
        }

        // Try to load saved progress
        let startChapter = 0;
        try {
          const savedProgress = localStorage.getItem(`reader-progress-${bookId}`);
          if (savedProgress) {
            const progress = JSON.parse(savedProgress);
            if (progress && typeof progress.chapterIndex === 'number' && progress.chapterIndex >= 0) {
              startChapter = progress.chapterIndex;
            }
          }
        } catch (storageErr) {
          console.warn("Erreur lors de la récupération de la progression:", storageErr);
          // Non-blocking error - continue with default chapter
        }

        if (isMounted) {
          await fetchChapter(startChapter);
        }
      } catch (err) {
        if (isMounted) {
          console.error("Erreur d'initialisation:", err);
          setError(err.message || "Impossible d'initialiser le lecteur. Veuillez rafraîchir la page ou réessayer plus tard.");
          setCurrentChapter('');
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    initializeReader();

    return () => {
      isMounted = false;
    };
  }, [bookId]);

  const goToNextChapter = async () => {
    if (currentChapterIndex < totalChapters - 1) {
      try {
        await fetchChapter(currentChapterIndex + 1);
      } catch (err) {
        setError("Erreur lors du chargement du chapitre suivant. Veuillez réessayer.");
      }
    }
  };

  const goToPreviousChapter = async () => {
    if (currentChapterIndex > 0) {
      try {
        await fetchChapter(currentChapterIndex - 1);
      } catch (err) {
        setError("Erreur lors du chargement du chapitre précédent. Veuillez réessayer.");
      }
    }
  };

  if (isLoading) {
    return (
      <Box
        sx={{
          height: "100vh",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          gap: 2,
          backgroundColor: theme.backgroundColor,
          color: theme.textColor,
        }}
      >
        <CircularProgress />
        <Typography variant="body1" sx={{ textAlign: 'center' }}>
          Chargement du chapitre...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box
        sx={{
          height: "100vh",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          backgroundColor: theme.backgroundColor,
          color: theme.textColor,
          padding: 3,
          maxWidth: "600px",
          mx: "auto",
        }}
      >
        <Typography variant="h6" sx={{ mb: 3, textAlign: 'center', color: 'error.main' }}>
          {error}
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            onClick={() => navigate('/library')}
            variant="outlined"
            sx={{ minWidth: '120px' }}
          >
            Bibliothèque
          </Button>
          <Button
            onClick={() => fetchChapter(currentChapterIndex)}
            variant="contained"
            sx={{ minWidth: '120px' }}
          >
            Réessayer
          </Button>
        </Box>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        height: "100vh",
        width: "100vw",
        overflow: "hidden",
        bgcolor: theme.backgroundColor,
        color: theme.textColor,
        position: "relative",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <Box
        component="header"
        sx={{
          position: "sticky",
          top: 0,
          left: 0,
          right: 0,
          zIndex: 1000,
          bgcolor: `${theme.backgroundColor}CC`,
          borderBottom: 1,
          borderColor: "divider",
          px: 2,
          py: 1,
          display: "flex",
          alignItems: "center",
          gap: 2,
          backdropFilter: "blur(8px)",
        }}
      >
        <IconButton
          onClick={() => setMenuOpen(true)}
          sx={{ color: theme.textColor }}
        >
          <MenuIcon />
        </IconButton>
        <LinearProgress
          variant="determinate"
          value={(currentChapterIndex / (totalChapters || 1)) * 100}
          sx={{
            flexGrow: 1,
            "& .MuiLinearProgress-bar": { backgroundColor: theme.textColor },
          }}
        />
      </Box>

      <TableOfContents
        open={menuOpen}
        onClose={() => setMenuOpen(false)}
        chapters={Array(totalChapters).fill("")}
        currentSection={currentChapterIndex}
        onChapterSelect={(index) => {
          fetchChapter(index);
          setMenuOpen(false);
        }}
      />

      <Box sx={{ flexGrow: 1, position: "relative", overflow: "hidden" }}>
        {currentChapter && (
          <KindleReader
            content={currentChapter}
            bookId={bookId}
            customTheme={theme}
            onProgressChange={(progress) => {
              try {
                saveReadingProgress(currentChapterIndex, progress);
              } catch (err) {
                console.warn('Failed to save reading progress:', err);
              }
            }}
            onNextChapter={goToNextChapter}
            onPreviousChapter={goToPreviousChapter}
          />
        )}
        <Box
          sx={{
            position: "fixed",
            bottom: 0,
            left: 0,
            right: 0,
            p: 2,
            bgcolor: theme.backgroundColor,
            borderTop: 1,
            borderColor: "divider",
            zIndex: 1000,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <CommandInput
            onCommand={(command) => {
              switch (command.toLowerCase()) {
                case "next":
                  goToNextChapter();
                  break;
                case "prev":
                  goToPreviousChapter();
                  break;
                default:
                  break;
              }
            }}
          />
          <Typography
            variant="caption"
            sx={{
              opacity: 0.7,
              ml: 2,
            }}
          >
            {currentChapterIndex + 1} / {totalChapters}
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}

export default ReaderPage;
