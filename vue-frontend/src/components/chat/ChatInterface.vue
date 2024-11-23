<template>
  <div class="chat-wrapper">
    <div class="chat-container">
      <v-card class="chat-interface" :elevation="2">
        <MessageList />
        <ChatControls />
        <MessageInput />
      </v-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import MessageList from './MessageList.vue'
import MessageInput from './MessageInput.vue'
import ChatControls from './ChatControls.vue'
</script>

<style scoped>
.chat-wrapper {
  position: relative;
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.chat-container {
  width: 100%;
  max-width: 800px;
  height: calc(100vh - 2rem);
  position: relative;
}

.chat-interface {
  height: 100%;
  display: flex;
  flex-direction: column;
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}
</style>
