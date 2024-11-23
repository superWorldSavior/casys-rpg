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
  padding: 0.75rem;
  margin: 0.25rem 0;
  border-radius: 0.5rem;
  background-color: #f0f0f0;
  max-width: 80%;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.user-message {
  margin-left: auto;
  background-color: #e3f2fd;
}

.message-content {
  margin: 0;
  white-space: pre-wrap;
}

.message-timestamp {
  display: block;
  color: #666;
  font-size: 0.8rem;
  margin-top: 0.25rem;
}
</style>
