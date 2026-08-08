import React from 'react'

function NavigationControls({
  currentSection,
  setCurrentSection,
  totalSections,
  isPaused,
  setIsPaused
}) {
  return (
    <div className="controls mb-3">
      <div className="d-flex justify-content-between align-items-center">
        <button
          className="btn btn-secondary"
          onClick={() => setCurrentSection(prev => prev - 1)}
          disabled={currentSection <= 0}
        >
          <i className="feather-arrow-left"></i> Previous
        </button>
        <button
          className="btn btn-secondary ms-2"
          onClick={() => setIsPaused(prev => !prev)}
        >
          {isPaused ? 'Resume' : 'Pause'}
        </button>
        <button
          className="btn btn-secondary"
          onClick={() => setCurrentSection(prev => prev + 1)}
          disabled={currentSection >= totalSections - 1}
        >
          Next <i className="feather-arrow-right"></i>
        </button>
      </div>
    </div>
  )
}

export default NavigationControls
