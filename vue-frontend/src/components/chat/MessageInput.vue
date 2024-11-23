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
  padding: 1rem;
  border-top: 1px solid #e0e0e0;
}

.input-form {
  display: flex;
  gap: 0.5rem;
}

input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 0.25rem;
  font-family: inherit;
}

button {
  padding: 0.5rem 1rem;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
