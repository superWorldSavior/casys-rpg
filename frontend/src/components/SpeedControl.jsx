import React from 'react'

function SpeedControl({ speed, setSpeed }) {
  return (
    <div className="speed-control mb-3">
      <label className="form-label">Speed:</label>
      <input
        type="range"
        className="form-range"
        min="1"
        max="10"
        value={speed}
        onChange={(e) => setSpeed(parseInt(e.target.value))}
      />
    </div>
  )
}

export default SpeedControl
