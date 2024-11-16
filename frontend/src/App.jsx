import React from 'react'
import { 
  createBrowserRouter,
  RouterProvider,
  createRoutesFromElements,
  Route,
  Link,
  Outlet
} from 'react-router-dom'
import { AppBar, Toolbar, Typography, Container, Button } from '@mui/material'
import HomePage from './components/HomePage'
import TextReader from './components/TextReader'

// Layout component for consistent UI across routes
const Layout = () => (
  <>
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Lecteur de Texte
        </Typography>
        <Button color="inherit" component={Link} to="/">
          Accueil
        </Button>
      </Toolbar>
    </AppBar>
    <Container sx={{ mt: 4 }}>
      <Outlet />
    </Container>
  </>
)

// Create router with all future flags enabled
const router = createBrowserRouter(
  createRoutesFromElements(
    <Route path="/" element={<Layout />}>
      <Route index element={<HomePage />} />
      <Route path="chat/:bookId" element={<TextReader />} />
      <Route path="*" element={
        <div style={{ textAlign: 'center', marginTop: '2rem' }}>
          Page non trouvée
        </div>
      } />
    </Route>
  ),
  {
    future: {
      v7_startTransition: true,
      v7_normalizeFormMethod: true,
      v7_fetcherPersist: true,
      v7_partialHydration: true,
      v7_relativeSplatPath: true,
      v7_skipActionErrorRevalidation: true
    }
  }
)

function App() {
  return <RouterProvider router={router} />
}

export default App
