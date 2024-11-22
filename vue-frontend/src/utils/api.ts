import axios, { AxiosError } from 'axios';
import { ref } from 'vue';

const API_BASE_URL = '/api';
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
    }
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
    response => response,
    error => {
        if (error.response?.status === 401) {
            // Redirect to login page if unauthorized
            window.location.href = '/';
        }
        return Promise.reject(error);
    }
);

export const useApiCall = <T>(
  apiFunction: () => Promise<T>,
  options = { retries: MAX_RETRIES, delay: RETRY_DELAY }
) => {
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const data = ref<T | null>(null);

  const execute = async () => {
    isLoading.value = true;
    error.value = null;
    let attempt = 0;

    while (attempt < options.retries) {
      try {
        const response = await apiFunction();
        data.value = response;
        return response;
      } catch (err) {
        attempt++;
        if (attempt === options.retries) {
          const axiosError = err as AxiosError;
          error.value = axiosError.message || 'Une erreur est survenue';
          throw err;
        }
        await new Promise(resolve => setTimeout(resolve, options.delay));
      } finally {
        isLoading.value = false;
      }
    }
  };

  return {
    execute,
    isLoading,
    error,
    data,
  };
};

export const handleApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    console.error('Erreur API:', error);
    if (error.response) {
      return error.response.data.message || 'Une erreur est survenue';
    }
    if (error.request) {
      return 'Impossible de contacter le serveur';
    }
    return error.message;
  }
  console.error('Erreur inattendue:', error);
  return 'Une erreur inattendue est survenue';
};
