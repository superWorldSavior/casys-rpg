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

function TextDisplay({ textContent, currentSection, speed, theme }) {
  const [currentAnimation, setCurrentAnimation] = useState(0)
  const [revealedText, setRevealedText] = useState('')

  // Reset text and update animation when section changes
  useEffect(() => {
    if (currentSection >= 0) {
      setCurrentAnimation((prev) => (prev + 1) % ANIMATION_STYLES.length)
      setRevealedText('')
    }
  }, [currentSection])

  // Progressive text reveal effect with improved state updates
  useEffect(() => {
    if (currentSection >= 0 && textContent[currentSection]) {
      const text = textContent[currentSection]
      const revealSpeed = 11 - speed
      let currentChar = 0

      const revealInterval = setInterval(() => {
        if (currentChar < text.length) {
          setRevealedText(prev => text.substring(0, currentChar + 1))
          currentChar++
        } else {
          clearInterval(revealInterval)
        }
      }, revealSpeed * 30)

      return () => clearInterval(revealInterval)
    }
  }, [currentSection, textContent, speed])

  const textStyle = {
    fontFamily: theme.fontFamily,
    fontSize: theme.fontSize,
    color: theme.textColor,
    lineHeight: theme.lineHeight
  }

  return (
    <div id="text-display" className="mb-4">
      <div className="text-content markdown-content" style={textStyle}>
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
                h1: ({node, children, ...props}) => (
                  <h1 style={textStyle} className="text-4xl font-bold mb-4" {...props}>{children}</h1>
                ),
                h2: ({node, children, ...props}) => (
                  <h2 style={textStyle} className="text-2xl font-semibold mb-3" {...props}>{children}</h2>
                ),
                strong: ({node, children, ...props}) => (
                  <strong style={textStyle} className="font-bold" {...props}>{children}</strong>
                ),
                em: ({node, children, ...props}) => (
                  <em style={textStyle} className="italic" {...props}>{children}</em>
                ),
                p: ({node, children, ...props}) => (
                  <p style={textStyle} className="mb-3" {...props}>{children}</p>
                ),
                ul: ({node, children, ...props}) => (
                  <ul style={textStyle} className="list-disc pl-5 mb-3" {...props}>{children}</ul>
                ),
                ol: ({node, children, ...props}) => (
                  <ol style={textStyle} className="list-decimal pl-5 mb-3" {...props}>{children}</ol>
                ),
                li: ({node, children, ...props}) => (
                  <li style={textStyle} className="mb-2" {...props}>{children}</li>
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
