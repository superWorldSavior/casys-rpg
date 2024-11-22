<template>
  <div class="library">
    <h1>casys rpg</h1>
    <div class="filters">
      <button 
        :class="{ active: showOnlyFavorites }"
        @click="showOnlyFavorites = !showOnlyFavorites"
      >
        {{ showOnlyFavorites ? 'Tous les livres' : 'Favoris' }}
      </button>
    </div>
    <div v-if="isLoading" class="loading">
      Chargement...
    </div>
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    <div v-else class="book-grid">
      <div v-for="book in displayedBooks" :key="book.id" class="book-card">
        <div class="book-info">
          <h3>{{ book.title }}</h3>
          <p>{{ book.author }}</p>
        </div>
        <div class="book-card-header">
          <img v-if="book.cover_image" :src="book.cover_image" :alt="book.title" class="book-cover">
          <div v-else class="book-cover-placeholder">
            <span>{{ book.title[0] }}</span>
          </div>
          <button 
            class="favorite-btn"
            :class="{ 'is-favorite': isFavorite(book.id) }"
            @click="toggleFavorite(book.id)"
            :title="isFavorite(book.id) ? 'Retirer des favoris' : 'Ajouter aux favoris'"
          >
            <svg viewBox="0 0 24 24" width="24" height="24">
              <path :fill="isFavorite(book.id) ? '#FFD700' : '#ccc'" d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
            </svg>
          </button>
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
      </div>
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
  padding: 0.5rem;
}

.book-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  padding: 0.5rem 0;
}

@media (max-width: 480px) {
  .book-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 0.5rem;
    padding: 0.25rem;
    margin: 0 -0.25rem;
  }

  h1 {
    font-size: 1.5rem;
    text-align: left;
    margin: 0.5rem 0;
    padding-left: 0.5rem;
  }
}

.book-card {
  background: var(--card-background, white);
  border-radius: 12px;
  padding: 0.75rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: all 0.2s ease-in-out;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.book-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.book-card-header {
  position: relative;
}

.favorite-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.favorite-btn:hover {
  transform: scale(1.1);
}

.favorite-btn.is-favorite svg path {
  fill: #FFD700;
}

.book-info {
  margin-top: 1rem;
}

.progress-indicator {
  margin-top: 0.5rem;
}

.progress-bar {
  height: 4px;
  background-color: #e9ecef;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 0.25rem;
}

.progress-fill {
  height: 100%;
  background-color: var(--accent-color);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.8rem;
  color: var(--text-color);
}

.filters {
  margin-bottom: 1rem;
}

.filters button {
  padding: 0.5rem 1rem;
  border: 2px solid var(--accent-color);
  background: transparent;
  color: var(--accent-color);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filters button.active {
  background: var(--accent-color);
  color: white;
}

.book-cover {
  width: 100%;
  aspect-ratio: 2/3;
  object-fit: cover;
  border-radius: 8px;
  background-color: var(--placeholder-background, #f0f0f0);
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
  border-radius: 8px;
}

@media (max-width: 480px) {
  .book-info h3 {
    font-size: 0.9rem;
    margin: 0.5rem 0 0.25rem;
  }
  
  .book-info p {
    font-size: 0.8rem;
    margin: 0;
  }
  
  .progress-text {
    font-size: 0.7rem;
  }
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
