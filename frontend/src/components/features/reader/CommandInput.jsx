import React, { useState } from 'react';
import { TextField, Button, Box } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

function CommandInput({ onCommand }) {
  const [command, setCommand] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (command.trim()) {
      onCommand(command.trim().toLowerCase());
      setCommand('');
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2, display: 'flex', gap: 1 }}>
      <TextField
        fullWidth
        value={command}
        onChange={(e) => setCommand(e.target.value)}
        placeholder="Enter command (type 'help' for available commands)"
        size="small"
      />
      <Button type="submit" variant="contained" endIcon={<SendIcon />}>
        Send
      </Button>
    </Box>
  );
}

export default CommandInput;
