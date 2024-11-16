import React from 'react'
import { 
  createBrowserRouter,
  RouterProvider,
  createRoutesFromElements,
  Route,
  Link
} from 'react-router-dom'
import { AppBar, Toolbar, Typography, Container, Button } from '@mui/material'
import HomePage from './components/HomePage'
import Chat from './components/Chat'

// Layout component for consistent UI across routes
const Layout = ({ children }) => (
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
      {children}
    </Container>
  </>
)

// Create router with future flags enabled
const router = createBrowserRouter(
  createRoutesFromElements(
    <Route
      path="/"
      element={<Layout />}
    >
      <Route index element={<HomePage />} />
      <Route path="chat/:bookId" element={<Chat />} />
      <Route path="*" element={<div>Page not found</div>} />
    </Route>
  ),
  {
    future: {
      v7_startTransition: true,
      v7_relativeSplatPath: true
    }
  }
)

function App() {
  return <RouterProvider router={router} />
}

export default App
