import { ref, computed } from 'vue';
import { authService } from '@/services/auth/authService';
import type { User } from '@/types/auth';

export function useAuth() {
  const currentUser = ref<User | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const isAuthenticated = computed(() => !!currentUser.value);

  async function login(email: string, password: string) {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await authService.login(email, password);
      currentUser.value = response.user;
      authService.setStoredToken(response.token);
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Une erreur est survenue';
      throw e;
    } finally {
      isLoading.value = false;
    }
  }

  async function logout() {
    isLoading.value = true;
    error.value = null;
    
    try {
      await authService.logout();
      currentUser.value = null;
      authService.removeStoredToken();
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Une erreur est survenue';
      throw e;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    currentUser,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout
  };
}
