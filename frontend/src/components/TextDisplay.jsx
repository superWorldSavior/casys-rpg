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
          setRevealedText(text.substring(0, currentChar + 1))
          currentChar++
        } else {
          setIsRevealing(false)
          clearInterval(revealInterval)
        }
      }, revealSpeed * 30)

      return () => clearInterval(revealInterval)
    }
  }, [isRevealing, currentSection, textContent, speed])

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
                h1: ({node, ...props}) => <h1 className="mb-4" {...props}/>,
                h2: ({node, ...props}) => <h2 className="mb-3" {...props}/>,
                strong: ({node, ...props}) => <strong className="fw-bold" {...props}/>,
                em: ({node, ...props}) => <em className="fst-italic" {...props}/>,
                p: ({node, ...props}) => <p className="mb-3" {...props}/>,
                ul: ({node, ...props}) => <ul className="list-unstyled mb-3" {...props}/>,
                ol: ({node, ...props}) => <ol className="mb-3" {...props}/>,
                li: ({node, ...props}) => <li className="mb-2" {...props}/>
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
