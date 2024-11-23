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
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.chat-container {
  width: 100%;
  height: 100%;
}

.chat-interface {
  height: 100%;
  width: 100%;
  border-radius: 0;
  background-color: #f8f9fa;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
</style>
