import axios from 'axios';
import { AuthService } from './auth';

const API_URL = '/api';

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  withCredentials: true,
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = AuthService.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      AuthService.logout();
      window.location.href = '/login';
      return Promise.reject(error);
    }

    return Promise.reject({
      ...error,
      message: error.response?.data?.message || 'An unexpected error occurred'
    });
  }
);

export const LibraryService = {
  async getBooks() {
    try {
      const response = await api.get('/books');
      return response.data;
    } catch (error) {
      console.error('Error fetching books:', error);
      throw error;
    }
  },

  async getBook(bookId) {
    try {
      const response = await api.get(`/books/${bookId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching book:', error);
      throw error;
    }
  },

  async uploadBook(formData) {
    try {
      const response = await api.post('/books/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error uploading book:', error);
      throw error;
    }
  },
};

export default api;
