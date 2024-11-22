import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { apiClient, handleApiError } from '../utils/api';

interface Book {
  id: string;
  title: string;
  author: string;
  cover_image?: string;
  isFavorite?: boolean;
}

export const useBooksStore = defineStore('books', () => {
  const books = ref<Book[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const favorites = ref<Set<string>>(new Set());

  // Load favorites from localStorage on store initialization
  try {
    const savedFavorites = localStorage.getItem('bookFavorites');
    if (savedFavorites) {
      favorites.value = new Set(JSON.parse(savedFavorites));
    }
  } catch (err) {
    console.error('Error loading favorites:', err);
  }

  const favoriteBooks = computed(() => {
    return books.value.filter(book => favorites.value.has(book.id));
  });

  async function fetchBooks() {
    try {
      isLoading.value = true;
      const response = await apiClient.get('/books');
      books.value = response.data.books.map((book: any) => ({
        ...book,
        cover_image: `/api/books/${book.filename}/cover`,
        isFavorite: favorites.value.has(book.id)
      }));
    } catch (err) {
      console.error('Erreur fetchBooks:', err);
      error.value = handleApiError(err);
      books.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  function toggleFavorite(bookId: string) {
    if (favorites.value.has(bookId)) {
      favorites.value.delete(bookId);
    } else {
      favorites.value.add(bookId);
    }
    
    // Update the isFavorite property of the book
    const book = books.value.find(b => b.id === bookId);
    if (book) {
      book.isFavorite = favorites.value.has(bookId);
    }

    // Save to localStorage
    localStorage.setItem('bookFavorites', JSON.stringify([...favorites.value]));
  }

  return { 
    books, 
    isLoading, 
    error, 
    fetchBooks, 
    toggleFavorite, 
    favoriteBooks,
    isFavorite: (id: string) => favorites.value.has(id)
  };
});
