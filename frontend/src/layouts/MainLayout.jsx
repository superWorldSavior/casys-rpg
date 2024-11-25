import React, { Suspense } from "react";
import { Link, Outlet, useLocation } from "react-router-dom";
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Button,
  Box,
  CircularProgress,
} from "@mui/material";
import MenuBookIcon from "@mui/icons-material/MenuBook";
import BottomNav from "../components/navigation/BottomNav.jsx";

const MainLayout = () => {
  const location = useLocation();
  const isReaderRoute = location.pathname.includes('/reader/');
  
  // Ne pas afficher l'AppBar en mode lecture
  if (isReaderRoute) {
    return (
      <>
        <Container
          maxWidth={false}
          disableGutters
          sx={{
            p: 0,
            m: 0,
            height: '100vh',
            width: '100vw',
            overflow: 'hidden'
          }}
        >
          <Outlet />
        </Container>
      </>
    );
  }

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Box display="flex" alignItems="center" sx={{ flexGrow: 1 }}>
            <MenuBookIcon sx={{ mr: 1, color: "primary.main" }} />
            <Typography
              variant="h6"
              component={Link}
              to="/"
              sx={{
                textDecoration: "none",
                color: "text.primary",
                fontWeight: 600,
                "&:hover": {
                  color: "primary.main",
                },
              }}
            >
              Casys.AI
            </Typography>
          </Box>
          <Button
            color="primary"
            component={Link}
            to="/credits"
            sx={{
              fontWeight: 500,
              mr: 2,
              "&:hover": {
                backgroundColor: "primary.light",
              },
            }}
          >
            Acheter des crédits
          </Button>
          <Button
            color="primary"
            component={Link}
            to="/library"
            sx={{
              fontWeight: 500,
              display: { xs: "none", sm: "block" },
              "&:hover": {
                backgroundColor: "primary.light",
              },
            }}
          >
            Bibliothèque
          </Button>
        </Toolbar>
      </AppBar>
      <Container
        maxWidth={isReaderRoute ? false : "xl"}
        disableGutters={isReaderRoute}
        sx={{
          mt: isReaderRoute ? 0 : 4,
          minHeight: "calc(100vh - 64px)",
          backgroundColor: "background.default",
          py: isReaderRoute ? 0 : 3,
          pb: isReaderRoute ? 0 : { xs: 9, sm: 3 },
          overflowX: "hidden",
          ...(isReaderRoute && {
            p: 0,
            maxWidth: '100%',
            width: '100vw',
            height: '100vh'
          })
        }}
      >
        <Suspense
          fallback={
            <Box
              display="flex"
              justifyContent="center"
              alignItems="center"
              minHeight="200px"
            >
              <CircularProgress />
            </Box>
          }
        >
          <Outlet />
        </Suspense>
      </Container>
      {!isReaderRoute && <BottomNav />}
    </>
  );
};

export default MainLayout;
