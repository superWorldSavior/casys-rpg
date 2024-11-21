"""React Router configuration."""
import { createBrowserRouter } from 'react-router-dom';
import App from '../App';

// Enable future flags
const routerOptions = {
  future: {
    v7_startTransition: true,
    v7_relativeSplatPath: true,
    v7_fetcherPersist: true,
    v7_normalizeFormMethod: true,
    v7_partialHydration: true,
    v7_skipActionErrorRevalidation: true
  },
};

export const router = createBrowserRouter([
  {
    path: "*",
    Component: App,
  }
], routerOptions);
