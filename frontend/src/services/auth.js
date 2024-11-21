import axios from 'axios';

const API_URL = '/api';

export const AuthService = {
  async login(email, password) {
    const response = await axios.post(`${API_URL}/auth/login`, { email, password });
    if (response.data.token) {
      localStorage.setItem('user', JSON.stringify(response.data));
    }
    return response.data;
  },

  async register(username, email, password) {
    const response = await axios.post(`${API_URL}/auth/register`, {
      username,
      email,
      password,
    });
    if (response.data.token) {
      localStorage.setItem('user', JSON.stringify(response.data));
    }
    return response.data;
  },

  async googleLogin() {
    window.location.href = `${API_URL}/google_login`;
  },

  logout() {
    localStorage.removeItem('user');
  },

  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  getToken() {
    const user = this.getCurrentUser();
    return user?.token;
  },

  isAuthenticated() {
    return !!this.getCurrentUser();
  }
};

export const setupAxiosInterceptors = () => {
  axios.interceptors.request.use(
    (config) => {
      const token = AuthService.getToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  axios.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        AuthService.logout();
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );
};
