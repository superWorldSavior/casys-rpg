<template>
  <v-card class="chat-interface" :elevation="2">
    <MessageList />
    <ChatControls />
    <MessageInput />
  </v-card>
</template>

<script setup lang="ts">
import MessageList from './MessageList.vue'
import MessageInput from './MessageInput.vue'
import ChatControls from './ChatControls.vue'
</script>

<style scoped>
.chat-interface {
  height: 100%;
  display: flex;
  flex-direction: column;
  width: 100%;
}
</style>
