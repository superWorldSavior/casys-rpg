import React from 'react'

function TextDisplay({ textContent, currentSection }) {
  return (
    <div id="text-display" className="mb-4">
      <div className="text-content">
        {textContent.map((text, index) => (
          <p
            key={index}
            className={`text-section ${index === currentSection ? 'active' : ''}`}
            style={{ display: index === currentSection ? 'block' : 'none' }}
          >
            {text}
          </p>
        ))}
      </div>
    </div>
  )
}

export default TextDisplay
