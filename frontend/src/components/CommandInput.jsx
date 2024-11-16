import React, { useState } from 'react'

function CommandInput({ onCommand }) {
  const [command, setCommand] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (command.trim()) {
      onCommand(command.toLowerCase().trim())
      setCommand('')
    }
  }

  return (
    <div className="command-input">
      <div className="input-group">
        <span className="input-group-text">&gt;</span>
        <input
          type="text"
          className="form-control"
          placeholder="Type 'commencer' to begin..."
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              handleSubmit(e)
            }
          }}
        />
        <button className="btn btn-primary" onClick={handleSubmit}>
          Enter
        </button>
      </div>
    </div>
  )
}

export default CommandInput
