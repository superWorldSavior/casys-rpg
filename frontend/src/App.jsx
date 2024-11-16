import React, { useState, useEffect } from 'react'
import TextDisplay from './components/TextDisplay'
import NavigationControls from './components/NavigationControls'
import CommandInput from './components/CommandInput'
import SpeedControl from './components/SpeedControl'
import { storageService } from './utils/storage'

function App() {
  const [currentSection, setCurrentSection] = useState(-1)
  const [isPaused, setIsPaused] = useState(true)
  const [speed, setSpeed] = useState(5)
  const [textContent, setTextContent] = useState([])

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
      } catch (error) {
        console.error('Error fetching text content:', error)
      }
    }

    fetchContent()
  }, [])

  return (
    <div className="container py-4">
      <div className="row justify-content-center">
        <div className="col-md-8">
          <div className="card">
            <div className="card-body">
              <TextDisplay
                textContent={textContent}
                currentSection={currentSection}
                speed={speed}
              />
              <NavigationControls
                currentSection={currentSection}
                setCurrentSection={setCurrentSection}
                totalSections={textContent.length}
                isPaused={isPaused}
                setIsPaused={setIsPaused}
              />
              <SpeedControl speed={speed} setSpeed={setSpeed} />
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
    </div>
  )
}

export default App
