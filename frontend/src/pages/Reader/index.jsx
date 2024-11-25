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

  // États
  const [currentChapter, setCurrentChapter] = useState("");
  const [currentChapterIndex, setCurrentChapterIndex] = useState(0);
  const [totalChapters, setTotalChapters] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [theme, setTheme] = useState(() =>
    muiTheme.palette.mode === "dark" ? DARK_THEME : DEFAULT_THEME,
  );

  // Mettre à jour le thème en fonction du mode actuel
  useEffect(() => {
    setTheme(muiTheme.palette.mode === "dark" ? DARK_THEME : DEFAULT_THEME);
  }, [muiTheme.palette.mode]);

  // Charger un chapitre spécifique
  const fetchChapter = async (index) => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch(`/api/books/${bookId}/chapters/${index}`);
      if (!response.ok) {
        throw new Error("Erreur lors du chargement du chapitre.");
      }

      const data = await response.json();
      setCurrentChapter(data.chapter);
      setCurrentChapterIndex(data.index);
    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Charger le nombre total de chapitres et initialiser le premier chapitre
  useEffect(() => {
    const fetchTotalChapters = async () => {
      try {
        const response = await fetch(`/api/books/${bookId}/chapters`);
        if (!response.ok) {
          throw new Error("Erreur lors du chargement des chapitres.");
        }

        const data = await response.json();
        setTotalChapters(data.chapters.length);
        fetchChapter(0); // Charger le premier chapitre
      } catch (err) {
        console.error(err);
        setError(err.message);
      }
    };

    fetchTotalChapters();
  }, [bookId]);

  // Navigation entre les chapitres
  const goToNextChapter = () => {
    if (currentChapterIndex < totalChapters - 1) {
      fetchChapter(currentChapterIndex + 1);
      setScrollPosition(0); // Reset scroll position for new chapter
    }
  };

  const goToPreviousChapter = () => {
    if (currentChapterIndex > 0) {
      fetchChapter(currentChapterIndex - 1);
      setScrollPosition(0); // Reset scroll position for new chapter
    }
  };

  const [scrollPosition, setScrollPosition] = useState(0);

  const handleScroll = (event) => {
    const { scrollTop, scrollHeight, clientHeight } = event.target;
    const bottom = scrollHeight - scrollTop === clientHeight;
    
    if (bottom) {
      // At the bottom of the content
      setIsChapterEnd(true);
    } else {
      setIsChapterEnd(false);
    }
    
    setScrollPosition(scrollTop);
  };

  if (isLoading) {
    return (
      <Box
        sx={{
          height: "100vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          backgroundColor: theme.backgroundColor,
          color: theme.textColor,
        }}
      >
        <CircularProgress />
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
          padding: 2,
        }}
      >
        <Typography variant="h6">{error}</Typography>
        <Button
          onClick={() => fetchChapter(currentChapterIndex)}
          variant="contained"
          sx={{ marginTop: 2 }}
        >
          Réessayer
        </Button>
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
      {/* En-tête */}
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
          value={(currentChapterIndex / totalChapters) * 100}
          sx={{
            flexGrow: 1,
            "& .MuiLinearProgress-bar": { backgroundColor: theme.textColor },
          }}
        />
      </Box>

      {/* Table des matières */}
      <TableOfContents
        open={menuOpen}
        onClose={() => setMenuOpen(false)}
        chapters={Array(totalChapters).fill("")} // Placeholder chapters
        currentSection={currentChapterIndex}
        onChapterSelect={(index) => {
          fetchChapter(index);
          setMenuOpen(false);
        }}
      />

      {/* Contenu du lecteur */}
      <Box
        sx={{
          flexGrow: 1,
          position: "relative",
          overflow: "hidden",
        }}
      >
        <KindleReader 
        content={currentChapter || []} 
        initialSection={0}
        bookId={bookId}
        customTheme={theme}
        onProgressChange={(progress) => {
          // Sauvegarder la progression
          localStorage.setItem(`reading-progress-${bookId}`, progress.toString());
        }}
      />
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
            zIndex: 1000
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
              position: "absolute",
              right: 16,
              bottom: 16,
              opacity: 0.7,
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
