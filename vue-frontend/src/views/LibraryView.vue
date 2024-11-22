<template>
  <div class="library">
    <div class="library-header">
      <h1>Bibliothèque</h1>
      <router-link to="/library" class="favorites-link">
        Mes favoris
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M9 18l6-6-6-6"/>
        </svg>
      </router-link>
    </div>
    <div v-if="isLoading" class="loading">
      Chargement...
    </div>
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    <div v-else class="book-grid">
      <router-link 
        v-for="book in displayedBooks" 
        :key="book.id" 
        :to="{ name: 'book-detail', params: { id: book.id }}" 
        class="book-card"
      >
        <div class="book-cover-container">
          <img v-if="book.cover_image" :src="book.cover_image" :alt="book.title" class="book-cover">
          <div v-else class="book-cover-placeholder">
            <span>{{ book.title[0] }}</span>
          </div>
          <div class="book-info-overlay">
            <h3>{{ book.title }}</h3>
            <p>{{ book.author }}</p>
          </div>
        </div>
        <div class="progress-indicator" v-if="getBookProgress(book.id)">
          <div class="progress-bar">
            <div 
              class="progress-fill"
              :style="{ width: `${getBookProgress(book.id)}%` }"
            ></div>
          </div>
          <span class="progress-text">{{ getBookProgress(book.id) }}%</span>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useBooksStore } from '../stores/books';
import { useProgressStore } from '../stores/progress';

const booksStore = useBooksStore();
const progressStore = useProgressStore();
const { books, isLoading, error } = storeToRefs(booksStore);
const { toggleFavorite, isFavorite } = booksStore;
const getBookProgress = (bookId: string) => progressStore.getPercentage(bookId);

const showOnlyFavorites = ref(false);

const displayedBooks = computed(() => {
  return showOnlyFavorites.value
    ? books.value.filter(book => isFavorite(book.id))
    : books.value;
});

onMounted(async () => {
  await booksStore.fetchBooks();
});
</script>

<style scoped>
.library {
  padding: 1rem;
}

.library-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.favorites-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: var(--accent-color);
  font-weight: 600;
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  transition: all 0.2s ease;
}

.favorites-link:hover {
  background-color: var(--hover-background);
  transform: translateY(-1px);
}

.book-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  padding: 0.5rem 0;
}

@media (max-width: 480px) {
  .book-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 0.75rem;
    padding: 0.5rem;
    margin: 0;
  }

  .book-cover-container {
    aspect-ratio: 2/3;
    height: auto;
  }

  .book-info-overlay {
    padding: 0.75rem;
  }

  .book-info-overlay h3 {
    font-size: 0.9rem;
    margin-bottom: 0.15rem;
  }

  .book-info-overlay p {
    font-size: 0.75rem;
  }

  h1 {
    font-size: 1.5rem;
    text-align: left;
    margin: 0.5rem 0;
    padding-left: 0.5rem;
  }
}

.book-card {
  position: relative;
  height: 100%;
  transition: all 0.2s ease-in-out;
}

.book-card:hover {
  transform: translateY(-4px);
}

.book-cover-container {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.book-cover {
  width: 100%;
  height: 100%;
  aspect-ratio: 2/3;
  object-fit: cover;
}

.book-cover-placeholder {
  width: 100%;
  aspect-ratio: 2/3;
  background: var(--placeholder-background, #f0f0f0);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: var(--text-color-secondary, #666);
}

.book-info-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 1rem;
  background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
  color: white;
}

.book-info-overlay h3 {
  font-size: 1rem;
  margin: 0 0 0.25rem;
  font-weight: 600;
}

.book-info-overlay p {
  font-size: 0.875rem;
  margin: 0;
  opacity: 0.8;
}

.progress-indicator {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 0.5rem;
  background: rgba(0,0,0,0.5);
  border-bottom-left-radius: 12px;
  border-bottom-right-radius: 12px;
}

.progress-bar {
  height: 3px;
  background-color: rgba(255,255,255,0.3);
  border-radius: 1.5px;
  overflow: hidden;
  margin-bottom: 0.25rem;
}

.progress-fill {
  height: 100%;
  background-color: var(--accent-color);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.75rem;
  color: white;
  text-align: right;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.error {
  color: #dc3545;
  padding: 1rem;
  text-align: center;
  background-color: #f8d7da;
  border-radius: 4px;
  margin: 1rem 0;
}
</style>
