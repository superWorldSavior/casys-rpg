<script setup lang="ts">
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()

const handleSpeedChange = (event: Event) => {
  const value = (event.target as HTMLInputElement).value
  chatStore.setVitesseLecture(parseInt(value))
}
</script>

<template>
  <div class="chat-controls">
    <div class="speed-control">
      <label for="speed">Vitesse de lecture:</label>
      <input
        id="speed"
        type="range"
        min="10"
        max="200"
        step="10"
        :value="chatStore.vitesseLecture"
        @input="handleSpeedChange"
      />
      <span>{{ chatStore.vitesseLecture }}ms</span>
    </div>
    <button @click="chatStore.effacerHistorique">
      Effacer l'historique
    </button>
  </div>
</template>

<style scoped>
.chat-controls {
  padding: 1rem;
  border-top: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.speed-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

input[type="range"] {
  flex: 1;
}

button {
  padding: 0.5rem;
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
}

button:hover {
  background-color: #d32f2f;
}
</style>
