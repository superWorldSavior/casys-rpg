import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { apiClient, handleApiError } from '../utils/api';

interface Book {
  id: string;
  title: string;
  author: string;
  cover_image?: string;
  isFavorite?: boolean;
  description?: string;
  status?: string;
  progress?: number;
}

export const useBooksStore = defineStore('books', () => {
  const books = ref<Book[]>([]);
  const currentBook = ref<Book | null>(null);
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

  async function getBook(bookId: string) {
    try {
      isLoading.value = true;
      const response = await apiClient.get(`/books/${bookId}`);
      currentBook.value = {
        ...response.data,
        cover_image: `/api/books/${response.data.filename}/cover`,
        isFavorite: favorites.value.has(response.data.id)
      };
      return currentBook.value;
    } catch (err) {
      console.error('Erreur getBook:', err);
      error.value = handleApiError(err);
      return null;
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
    if (currentBook.value?.id === bookId) {
      currentBook.value.isFavorite = favorites.value.has(bookId);
    }

    // Save to localStorage
    localStorage.setItem('bookFavorites', JSON.stringify([...favorites.value]));
  }

  // Setup WebSocket connection for real-time updates
  let ws: WebSocket | null = null;

  function setupWebSocket() {
    if (ws) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/ws/books`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'book_updated') {
        // Update book in the store
        const index = books.value.findIndex(b => b.id === data.book.id);
        if (index !== -1) {
          books.value[index] = {
            ...data.book,
            cover_image: `/api/books/${data.book.filename}/cover`,
            isFavorite: favorites.value.has(data.book.id)
          };
        }
        // Update currentBook if it's the same book
        if (currentBook.value?.id === data.book.id) {
          currentBook.value = {
            ...data.book,
            cover_image: `/api/books/${data.book.filename}/cover`,
            isFavorite: favorites.value.has(data.book.id)
          };
        }
      }
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed. Retrying in 5s...');
      ws = null;
      setTimeout(setupWebSocket, 5000);
    };
  }

  // Initialize WebSocket connection
  setupWebSocket();

  return { 
    books,
    currentBook,
    isLoading, 
    error, 
    fetchBooks,
    getBook,
    toggleFavorite, 
    favoriteBooks,
    isFavorite: (id: string) => favorites.value.has(id)
  };
});
