import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { User } from '@/types/auth';

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false);
  const currentUser = ref<User | null>(null);

  const login = () => {
    const user = {
      id: '1',
      name: 'Utilisateur',
      email: 'user@example.com'
    };
    
    isAuthenticated.value = true;
    currentUser.value = user;
  };

  const logout = () => {
    isAuthenticated.value = false;
    currentUser.value = null;
  };

  return {
    isAuthenticated,
    currentUser,
    login,
    logout
  };
});
