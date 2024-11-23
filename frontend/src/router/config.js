import { Navigate } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import LoginPage from '../pages/Auth/LoginPage';
import { lazy } from 'react';

const HomePage = lazy(() => import('../pages/Home'));
const ReaderPage = lazy(() => import('../pages/Reader'));

const publicRoutes = [
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: <Navigate to="/login" replace />,
  },
];

const protectedRoutes = [
  {
    path: '/home',
    element: <MainLayout />,
    children: [
      {
        index: true,
        element: <HomePage />,
      },
      {
        path: 'reader/:bookId',
        element: <ReaderPage />,
      },
    ],
  },
];

export { publicRoutes, protectedRoutes };
