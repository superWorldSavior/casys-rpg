<template>
  <div class="library">
    <h1>Bibliothèque</h1>
    <div v-if="isLoading" class="loading">
      Chargement...
    </div>
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    <div v-else class="book-grid">
      <div v-for="book in books" :key="book.id" class="book-card">
        <img v-if="book.cover_image" :src="book.cover_image" :alt="book.title" class="book-cover">
        <div v-else class="book-cover-placeholder">
          <span>{{ book.title[0] }}</span>
        </div>
        <h3>{{ book.title }}</h3>
        <p>{{ book.author }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useBooksStore } from '../stores/books';

const booksStore = useBooksStore();
const { books, isLoading, error } = storeToRefs(booksStore);

onMounted(async () => {
  await booksStore.fetchBooks();
});
</script>

<style scoped>
.library {
  padding: 1rem;
}

.book-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  padding: 1rem 0;
}

.book-card {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.book-cover {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 4px;
}

.book-cover-placeholder {
  width: 100%;
  height: 200px;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: #666;
  border-radius: 4px;
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
