import React, { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeRaw from 'rehype-raw'

const ANIMATION_STYLES = [
  'fade-in',
  'slide-right',
  'slide-up',
  'zoom-in',
  'typewriter',
  'bounce-in',
  'rotate-in',
  'flip-in',
  'swing-in',
  'scale-in',
  'blur-in',
  'slide-down',
  'slide-left'
]

function TextDisplay({ textContent, currentSection, speed }) {
  const [currentAnimation, setCurrentAnimation] = useState(0)
  const [revealedText, setRevealedText] = useState('')
  const [isRevealing, setIsRevealing] = useState(false)

  useEffect(() => {
    if (currentSection >= 0) {
      setCurrentAnimation((prev) => (prev + 1) % ANIMATION_STYLES.length)
      // Reset text reveal when section changes
      setRevealedText('')
      setIsRevealing(true)
    }
  }, [currentSection])

  useEffect(() => {
    if (isRevealing && currentSection >= 0 && textContent[currentSection]) {
      const text = textContent[currentSection]
      const revealSpeed = 11 - speed // Invert speed (1-10) for delay calculation
      let currentChar = 0

      const revealInterval = setInterval(() => {
        if (currentChar < text.length) {
          setRevealedText(text.slice(0, currentChar + 1))
          currentChar++
        } else {
          setIsRevealing(false)
          clearInterval(revealInterval)
        }
      }, revealSpeed * 30) // Adjust base speed (30ms) by user speed setting

      return () => clearInterval(revealInterval)
    }
  }, [isRevealing, currentSection, textContent, speed])

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
            <ReactMarkdown 
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeRaw]}
            >
              {index === currentSection && isRevealing ? revealedText : text}
            </ReactMarkdown>
          </div>
        ))}
      </div>
    </div>
  )
}

export default TextDisplay
