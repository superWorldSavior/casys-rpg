import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider, createRoutesFromElements, Route } from 'react-router-dom'
import App from './App'
import './index.css'

const router = createBrowserRouter(
  createRoutesFromElements(
    <Route path="*" element={<App />} />
  )
)

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider 
      router={router} 
      future={{ 
        v7_startTransition: true,
        v7_relativeSplatPath: true,
        v7_fetcherPersist: true,
        v7_normalizeFormMethod: true
      }} 
    />
  </React.StrictMode>
)
