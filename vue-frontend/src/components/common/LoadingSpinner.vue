<template>
  <div class="loading-spinner" :class="{ 'inline': inline }">
    <div class="spinner"></div>
    <span v-if="text" class="spinner-text">{{ text }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  text?: string
  inline?: boolean
}>()
</script>

<style scoped>
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
}

.loading-spinner.inline {
  flex-direction: row;
  padding: 0;
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.spinner-text {
  color: var(--text-color-secondary);
  font-size: 0.9rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
