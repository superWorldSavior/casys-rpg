import { defineStore } from 'pinia';
import { ref } from 'vue';

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
    // Simulation d'une connexion réussie
    isAuthenticated.value = true;
    user.value = {
      id: '1',
      email: 'user@example.com',
      username: 'User'
    };
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
