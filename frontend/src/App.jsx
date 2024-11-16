import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { AppBar, Toolbar, Typography, Container, Button } from '@mui/material'
import HomePage from './components/HomePage'

// These will be moved to a separate route later
// import TextReader from './components/TextReader'
// import TextDisplay from './components/TextDisplay'
// import NavigationControls from './components/NavigationControls'
// import CommandInput from './components/CommandInput'
// import SpeedControl from './components/SpeedControl'
// import ThemeControl from './components/ThemeControl'
// import { storageService } from './utils/storage'

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
          {/* Reader button commented out until reader functionality is implemented
          <Button color="inherit" component={Link} to="/reader">
            Lecteur
          </Button>
          */}
        </Toolbar>
      </AppBar>

      <Container sx={{ mt: 4 }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          {/* Reader route temporarily commented out
          <Route path="/reader" element={<TextReader />} />
          */}
        </Routes>
      </Container>
    </Router>
  )
}

export default App