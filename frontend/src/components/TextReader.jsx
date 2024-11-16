import React, { useState, useEffect } from 'react'
import TextDisplay from './TextDisplay'
import NavigationControls from './NavigationControls'
import CommandInput from './CommandInput'
import SpeedControl from './SpeedControl'
import ThemeControl from './ThemeControl'
import { storageService } from '../utils/storage'

const DEFAULT_THEME = {
  fontFamily: 'var(--bs-body-font-family)',
  fontSize: '1rem',
  textColor: '#ffffff',
  lineHeight: '1.6'
};

function TextReader() {
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
    <div className="row justify-content-center">
      <div className="col-md-8">
        <div className="card">
          <div className="card-body">
            <TextDisplay
              textContent={textContent}
              currentSection={currentSection}
              speed={speed}
              theme={theme}
            />
            <NavigationControls
              currentSection={currentSection}
              setCurrentSection={setCurrentSection}
              totalSections={textContent.length}
              isPaused={isPaused}
              setIsPaused={setIsPaused}
            />
            <SpeedControl speed={speed} setSpeed={setSpeed} />
            <ThemeControl theme={theme} onThemeChange={setTheme} />
            <CommandInput
              onCommand={(command) => {
                switch (command) {
                  case 'commencer':
                    setCurrentSection(0)
                    setIsPaused(false)
                    break
                  case 'pause':
                    setIsPaused(true)
                    break
                  case 'resume':
                    setIsPaused(false)
                    break
                  case 'skip':
                    if (currentSection < textContent.length - 1) {
                      setCurrentSection(prev => prev + 1)
                    }
                    break
                  case 'help':
                    alert(`Available commands:
- commencer: Start reading
- pause: Pause reading
- resume: Resume reading
- skip: Skip to next section
- help: Show this help message`)
                    break
                }
              }}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default TextReader
