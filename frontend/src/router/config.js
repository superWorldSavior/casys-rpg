"""React Router configuration."""
import { createBrowserRouter } from 'react-router-dom';

// Enable v7_startTransition flag
const routerOptions = {
  future: {
    v7_startTransition: true,
  },
};

export const router = createBrowserRouter(
  [
    // Your routes here
  ],
  routerOptions
);
