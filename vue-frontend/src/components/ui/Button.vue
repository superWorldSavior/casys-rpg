<template>
  <button
    :class="[
      'ui-button',
      variant,
      { 'is-loading': loading }
    ]"
    :disabled="disabled || loading"
    @click="$emit('click', $event)"
  >
    <span v-if="loading" class="loader"></span>
    <slot v-else></slot>
  </button>
</template>

<script setup lang="ts">
defineProps<{
  variant?: 'primary' | 'secondary' | 'danger'
  loading?: boolean
  disabled?: boolean
}>()

defineEmits<{
  (e: 'click', event: MouseEvent): void
}>()
</script>

<style scoped>
.ui-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 0.375rem;
  transition: all 0.2s;
  cursor: pointer;
  min-width: 100px;
  border: none;
}

.primary {
  background-color: #1a73e8;
  color: white;
}

.primary:hover:not(:disabled) {
  background-color: #1557b0;
}

.secondary {
  background-color: #f1f3f4;
  color: #3c4043;
}

.secondary:hover:not(:disabled) {
  background-color: #e8eaed;
}

.danger {
  background-color: #dc3545;
  color: white;
}

.danger:hover:not(:disabled) {
  background-color: #c82333;
}

.ui-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.is-loading {
  position: relative;
  color: transparent;
}

.loader {
  width: 16px;
  height: 16px;
  border: 2px solid #ffffff;
  border-bottom-color: transparent;
  border-radius: 50%;
  display: inline-block;
  animation: rotation 1s linear infinite;
}

@keyframes rotation {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
