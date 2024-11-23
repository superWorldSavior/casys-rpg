import { createBrowserRouter } from 'react-router-dom';
import LoginPage from '../pages/Auth/LoginPage';
import HomePage from '../pages/Home';
import ReaderPage from '../pages/Reader';
import BrowsePage from '../pages/Browse';
import ProfilePage from '../pages/Profile';
import Layout from '../layouts/MainLayout';
import { ProtectedRoute } from './ProtectedRoute';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: <LoginPage />
      },
      {
        path: 'login',
        element: <LoginPage />
      },
      {
        path: 'home',
        element: <ProtectedRoute><HomePage /></ProtectedRoute>
      },
      {
        path: 'library',
        element: <ProtectedRoute><HomePage /></ProtectedRoute>
      },
      {
        path: 'browse',
        element: <ProtectedRoute><BrowsePage /></ProtectedRoute>
      },
      {
        path: 'profile',
        element: <ProtectedRoute><ProfilePage /></ProtectedRoute>
      },
      {
        path: 'reader/:bookId',
        element: <ProtectedRoute><ReaderPage /></ProtectedRoute>
      },
      {
        path: '*',
        element: <div>404 - Page non trouvée</div>
      }
    ]
  }
], {
  future: {
    v7_startTransition: true
  }
});
