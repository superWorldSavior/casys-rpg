import { defineStore } from 'pinia';
import { ref } from 'vue';

const API_URL = 'https://34cf92a7-5a78-490c-81f5-13bbd10ad94d-00-1d3jqfgfypu5.pike.replit.dev';

interface User {
  id: string;
  email: string;
  username: string;
}

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false);
  const user = ref<User | null>(null);
  const error = ref<string | null>(null);

  function login() {
    try {
      isAuthenticated.value = true;
      user.value = {
        id: '1',
        email: 'user@example.com',
        username: 'User'
      };
      // La redirection sera gérée par le composant
    } catch (err) {
      error.value = 'Erreur lors de la connexion';
      console.error('Erreur login:', err);
    }
  }

  function logout() {
    isAuthenticated.value = false;
    user.value = null;
  }

  return {
    isAuthenticated,
    user,
    error,
    login,
    logout
  };
});
