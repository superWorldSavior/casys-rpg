import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { AppBar, Toolbar, Typography, Container, Button } from '@mui/material'
import HomePage from './components/HomePage'
import TextReader from './components/TextReader'
import TextDisplay from './components/TextDisplay'
import NavigationControls from './components/NavigationControls'
import CommandInput from './components/CommandInput'
import SpeedControl from './components/SpeedControl'
import ThemeControl from './components/ThemeControl'
import { storageService } from './utils/storage'

const DEFAULT_THEME = {
  fontFamily: 'var(--bs-body-font-family)',
  fontSize: '1rem',
  textColor: '#ffffff',
  lineHeight: '1.6'
};

function App() {
  const [currentSection, setCurrentSection] = useState(-1)
  const [isPaused, setIsPaused] = useState(true)
  const [speed, setSpeed] = useState(5)
  const [textContent, setTextContent] = useState([])
  const [theme, setTheme] = useState(DEFAULT_THEME)

  useEffect(() => {
    const fetchContent = async () => {
      try {
        // First try to get content from Replit DB
        const chapters = await storageService.getAllChapters()
        if (chapters && chapters.length > 0) {
          const content = await Promise.all(
            chapters.map(key => storageService.getChapter(key))
          )
          setTextContent(content)
        } else {
          // Fallback to API if no content in DB
          const response = await fetch('/api/text')
          const data = await response.json()
          // Store fetched content in Replit DB
          await Promise.all(
            data.map((content, index) =>
              storageService.saveChapter(`chapter_${index + 1}`, content)
            )
          )
          setTextContent(data)
        }

        // Load saved theme if exists
        const savedTheme = await storageService.getChapter('user_theme')
        if (savedTheme) {
          setTheme(savedTheme)
        }
      } catch (error) {
        console.error('Error fetching content:', error)
      }
    }

    fetchContent()
  }, [])

  // Save theme changes to storage
  useEffect(() => {
    storageService.saveChapter('user_theme', theme)
  }, [theme])

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
          <Button color="inherit" component={Link} to="/reader">
            Lecteur
          </Button>
        </Toolbar>
      </AppBar>

      <Container sx={{ mt: 4 }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/reader" element={
            <TextReader
              textContent={textContent}
              currentSection={currentSection}
              speed={speed}
              theme={theme}
              isPaused={isPaused}
              setIsPaused={setIsPaused}
              setCurrentSection={setCurrentSection}
            />
          } />
        </Routes>
      </Container>
    </Router>
  )
}

export default App