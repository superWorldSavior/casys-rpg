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
  </div>
</template>

<style scoped>
.chat-controls {
  padding: 0.5rem;
  border-top: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background-color: #f8f9fa;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.speed-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #666;
}

input[type="range"] {
  flex: 1;
  height: 2px;
  background-color: #ccc;
  -webkit-appearance: none;
  cursor: pointer;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 12px;
  height: 12px;
  background-color: var(--primary-color);
  border-radius: 50%;
  cursor: pointer;
}

input[type="range"]:focus {
  outline: none;
}
</style>
