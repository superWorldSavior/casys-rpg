<template>
  <div class="book-detail" v-if="book">
    <div class="book-header">
      <button class="back-button" @click="$router.back()">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <button class="favorite-button" @click="toggleBookFavorite" :class="{ active: isFavorite }">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>
        </svg>
      </button>
    </div>

    <div class="book-cover-wrapper">
      <img v-if="book.cover_image" :src="book.cover_image" :alt="book.title" class="book-cover">
      <div v-else class="book-cover-placeholder">
        <span>{{ book.title[0] }}</span>
      </div>
    </div>

    <div class="book-info">
      <h1>{{ book.title }}</h1>
      <p class="author">{{ book.author }}</p>
      
      <div class="progress-section">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
        </div>
        <span class="progress-text">{{ progress }}% lu</span>
      </div>

      <p class="description" v-if="book.description">{{ book.description }}</p>
      <p class="description" v-else>Aucune description disponible.</p>

      <router-link :to="{ name: 'reader', params: { id: book.id }}" class="read-button">
        <span>Commencer la lecture</span>
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="5 3 19 12 5 21 5 3"/>
        </svg>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useBooksStore } from '../stores/books';
import { useProgressStore } from '../stores/progress';

const route = useRoute();
const booksStore = useBooksStore();
const progressStore = useProgressStore();

const book = ref(null);
const progress = ref(0);
const isFavorite = ref(false);

onMounted(async () => {
  const bookId = route.params.id;
  if (bookId) {
    book.value = await booksStore.getBook(bookId);
    progress.value = progressStore.getPercentage(bookId) || 0;
    isFavorite.value = booksStore.isFavorite(bookId);
  }
});

const toggleBookFavorite = () => {
  if (book.value) {
    booksStore.toggleFavorite(book.value.id);
    isFavorite.value = !isFavorite.value;
  }
};
</script>

<style scoped>
.book-detail {
  padding: 1rem;
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: minmax(200px, 300px) 1fr;
  gap: 2rem;
  align-items: start;
}

@media (max-width: 768px) {
  .book-detail {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}

.book-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.back-button,
.favorite-button {
  background: none;
  border: none;
  padding: 0.5rem;
  cursor: pointer;
  color: var(--text-color);
  border-radius: 50%;
  transition: all 0.2s ease;
}

.back-button:hover,
.favorite-button:hover {
  background-color: var(--hover-background);
  transform: scale(1.1);
}

.favorite-button.active {
  color: var(--accent-color);
}

.favorite-button.active svg {
  fill: currentColor;
}

.book-cover-wrapper {
  position: sticky;
  top: 1rem;
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

@media (max-width: 768px) {
  .book-cover-wrapper {
    position: relative;
    top: 0;
    max-width: 200px;
    margin: 0 auto;
  }
}

.book-cover,
.book-cover-placeholder {
  width: 100%;
  aspect-ratio: 2/3;
  object-fit: cover;
}

.book-cover-placeholder {
  background: var(--placeholder-background);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: var(--text-color-secondary);
}

.book-info {
  text-align: center;
}

h1 {
  font-size: 1.75rem;
  margin: 0 0 0.5rem;
  color: var(--text-color);
}

.author {
  font-size: 1.1rem;
  color: var(--text-color-secondary);
  margin-bottom: 1.5rem;
}

.progress-section {
  margin: 1.5rem 0;
}

.progress-bar {
  height: 4px;
  background-color: var(--hover-background);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background-color: var(--accent-color);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.9rem;
  color: var(--text-color-secondary);
}

.description {
  margin: 1.5rem 0;
  color: var(--text-color);
  line-height: 1.6;
  text-align: left;
}

.read-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background-color: var(--accent-color);
  color: white;
  padding: 1rem 2rem;
  border-radius: 9999px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.2s ease;
  margin-top: 1rem;
}

.read-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

@media (max-width: 480px) {
  .book-detail {
    padding: 0.75rem;
  }

  h1 {
    font-size: 1.5rem;
  }

  .book-cover-wrapper {
    max-width: 200px;
  }

  .read-button {
    width: 100%;
    justify-content: center;
  }
}
</style>
