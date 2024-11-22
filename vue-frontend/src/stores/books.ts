import { defineStore } from 'pinia';
import { ref } from 'vue';
import { apiClient, handleApiError } from '../utils/api';

interface Book {
  id: string;
  title: string;
  author: string;
  cover_image?: string;
}

export const useBooksStore = defineStore('books', () => {
  const books = ref<Book[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  async function fetchBooks() {
    isLoading.value = true;
    try {
      const response = await apiClient.get('/books');
      books.value = response.data.books;
    } catch (err) {
      error.value = handleApiError(err);
    } finally {
      isLoading.value = false;
    }
  }

  return { books, isLoading, error, fetchBooks };
});
