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

  // Reset text and update animation when section changes
  useEffect(() => {
    if (currentSection >= 0) {
      setCurrentAnimation((prev) => (prev + 1) % ANIMATION_STYLES.length)
      setRevealedText('')
    }
  }, [currentSection])

  // Progressive text reveal effect
  useEffect(() => {
    if (currentSection >= 0 && textContent[currentSection]) {
      const text = textContent[currentSection]
      const revealSpeed = 11 - speed
      let currentChar = 0

      const revealInterval = setInterval(() => {
        if (currentChar < text.length) {
          setRevealedText(text.substring(0, currentChar + 1))
          currentChar++
        } else {
          clearInterval(revealInterval)
        }
      }, revealSpeed * 30)

      return () => clearInterval(revealInterval)
    }
  }, [currentSection, textContent, speed])

  return (
    <div id="text-display" className="mb-4">
      <div className="text-content markdown-content">
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
              components={{
                h1: ({node, ...props}) => (
                  <h1 className="text-4xl font-bold mb-4 text-emphasis" {...props}/>
                ),
                h2: ({node, ...props}) => (
                  <h2 className="text-2xl font-semibold mb-3 text-emphasis" {...props}/>
                ),
                strong: ({node, ...props}) => (
                  <strong className="font-bold text-emphasis" {...props}/>
                ),
                em: ({node, ...props}) => (
                  <em className="italic text-emphasis" {...props}/>
                ),
                p: ({node, ...props}) => (
                  <p className="mb-3 text-body" {...props}/>
                ),
                ul: ({node, ...props}) => (
                  <ul className="list-disc pl-5 mb-3" {...props}/>
                ),
                ol: ({node, ...props}) => (
                  <ol className="list-decimal pl-5 mb-3" {...props}/>
                ),
                li: ({node, ...props}) => (
                  <li className="mb-2" {...props}/>
                )
              }}
            >
              {index === currentSection ? revealedText : text}
            </ReactMarkdown>
          </div>
        ))}
      </div>
    </div>
  )
}

export default TextDisplay
