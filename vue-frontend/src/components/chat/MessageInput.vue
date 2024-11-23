<script setup lang="ts">
import { ref } from 'vue'
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()
const messageInput = ref('')

const handleSubmit = async () => {
  if (!messageInput.value.trim()) return
  
  try {
    await chatStore.envoyerMessageAI(messageInput.value)
    messageInput.value = ''
  } catch (error) {
    console.error('Erreur lors de l\'envoi du message:', error)
  }
}
</script>

<template>
  <div class="message-input-container">
    <form @submit.prevent="handleSubmit" class="input-form">
      <input
        v-model="messageInput"
        type="text"
        placeholder="Tapez votre message..."
        :disabled="chatStore.estEnChargement"
      />
      <button
        type="submit"
        :disabled="chatStore.estEnChargement || !messageInput.trim()"
      >
        Envoyer
      </button>
    </form>
  </div>
</template>

<style scoped>
.message-input-container {
  padding: 0.5rem;
  border-top: 1px solid #e0e0e0;
  background-color: #f8f9fa;
}

.input-form {
  display: flex;
  gap: 0.5rem;
}

input {
  flex: 1;
  padding: 0.5rem;
  border: none;
  border-bottom: 1px solid #ccc;
  font-family: 'Courier New', monospace;
  background-color: transparent;
}

input:focus {
  outline: none;
  border-bottom-color: var(--primary-color);
}

button {
  padding: 0.25rem 0.75rem;
  background-color: transparent;
  color: var(--primary-color);
  border: 1px solid var(--primary-color);
  cursor: pointer;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

button:hover:not(:disabled) {
  background-color: var(--primary-color);
  color: white;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
