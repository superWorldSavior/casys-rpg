import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useParams } from 'react-router-dom'
import { AppBar, Toolbar, Typography, Container, Button } from '@mui/material'
import HomePage from './components/HomePage'
import TextReader from './components/TextReader'

function App() {
  return (
    <Router>
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
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/reader/:bookId" element={<TextReader />} />
        </Routes>
      </Container>
    </Router>
  )
}

export default App