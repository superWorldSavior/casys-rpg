<template>
  <div class="library">
    <h1>Bibliothèque</h1>
    <div class="book-grid">
      <!-- Book list will be populated here -->
    </div>
  </div>
</template>

<script setup lang="ts">
// Library component logic will be added here
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
</style>
