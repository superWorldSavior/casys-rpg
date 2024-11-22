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
    try {
      isLoading.value = true;
      const response = await apiClient.get('/books');
      books.value = response.data.books.map((book: any) => ({
        ...book,
        cover_image: `/api/books/${book.filename}/cover`
      }));
    } catch (err) {
      console.error('Erreur fetchBooks:', err);
      error.value = handleApiError(err);
      books.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  return { books, isLoading, error, fetchBooks };
});
