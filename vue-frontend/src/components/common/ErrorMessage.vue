<template>
  <div class="error-message" :class="{ 'inline': inline }">
    <v-icon icon="mdi-alert-circle" color="error" />
    <span class="message">{{ message }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  message: string
  inline?: boolean
}>()
</script>

<style scoped>
.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background-color: rgb(var(--v-theme-error), 0.1);
  border-radius: 8px;
  color: rgb(var(--v-theme-error));
}

.error-message.inline {
  padding: 0.5rem;
}

.message {
  font-size: 0.9rem;
}
</style>
