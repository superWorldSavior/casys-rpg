import React, { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'

const ANIMATION_STYLES = [
  'fade-in',
  'slide-right',
  'slide-up',
  'zoom-in',
  'typewriter',
  'bounce-in',
  'rotate-in',
  'flip-in',
  'swing-in'
]

function TextDisplay({ textContent, currentSection }) {
  const [currentAnimation, setCurrentAnimation] = useState(0)

  useEffect(() => {
    if (currentSection >= 0) {
      setCurrentAnimation((prev) => (prev + 1) % ANIMATION_STYLES.length)
    }
  }, [currentSection])

  return (
    <div id="text-display" className="mb-4">
      <div className="text-content">
        {textContent.map((text, index) => (
          <div
            key={index}
            className={`text-section ${
              index === currentSection
                ? `active ${ANIMATION_STYLES[currentAnimation]}`
                : ''
            }`}
            style={{ display: index === currentSection ? 'block' : 'none' }}
          >
            <ReactMarkdown>{text}</ReactMarkdown>
          </div>
        ))}
      </div>
    </div>
  )
}

export default TextDisplay
