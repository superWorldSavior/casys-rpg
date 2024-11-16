import React, { useState, useEffect } from 'react'
import TextDisplay from './components/TextDisplay'
import NavigationControls from './components/NavigationControls'
import CommandInput from './components/CommandInput'
import SpeedControl from './components/SpeedControl'

function App() {
  const [currentSection, setCurrentSection] = useState(-1)
  const [isPaused, setIsPaused] = useState(true)
  const [speed, setSpeed] = useState(5)
  const [textContent, setTextContent] = useState([])

  useEffect(() => {
    fetch('/api/text')
      .then(response => response.json())
      .then(data => {
        setTextContent(data)
      })
      .catch(error => {
        console.error('Error fetching text content:', error)
      })
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
