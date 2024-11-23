<script setup lang="ts">
import type { Message } from '@/stores/chat'

const props = defineProps<{
  message: Message
}>()
</script>

<template>
  <div :class="['message', { 'user-message': message.estUtilisateur }]">
    <p class="message-content">{{ message.contenu }}</p>
    <small class="message-timestamp">
      {{ new Date(message.timestamp).toLocaleTimeString() }}
    </small>
  </div>
</template>

<style scoped>
.message {
  padding: 0.5rem 1rem;
  margin: 0;
  border-radius: 0;
  background: none;
  max-width: 100%;
  box-shadow: none;
}

.user-message {
  margin-left: 0;
  background: none;
  font-style: italic;
  color: #666;
}

.message-content {
  font-family: 'Courier New', monospace;
  line-height: 1.6;
  font-size: 1.1rem;
  white-space: pre-wrap;
  margin: 0;
}

.message-timestamp {
  display: none;
}
</style>
