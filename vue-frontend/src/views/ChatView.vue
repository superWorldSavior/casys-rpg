<template>
  <div class="chat-container">
    <!-- Barre de navigation simple -->
    <div class="chat-header">
      <v-btn icon="mdi-arrow-left" @click="$router.push('/library')" class="back-btn">
        <v-tooltip activator="parent">Retour</v-tooltip>
      </v-btn>
      <v-btn icon="mdi-file-document" @click="toggleHistory" class="adventure-btn">
        <v-tooltip activator="parent">Feuille d'aventure</v-tooltip>
      </v-btn>
    </div>

    <!-- Zone de chat -->
    <div class="chat-messages">
      <chat-interface />
    </div>

    <!-- Drawer pour la feuille d'aventure -->
    <v-navigation-drawer v-model="showHistory" location="right" temporary width="400">
      <v-toolbar>
        <v-toolbar-title>Feuille d'aventure</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn icon="mdi-close" @click="showHistory = false"></v-btn>
      </v-toolbar>
      <v-list>
        <v-list-item v-for="(message, index) in chatHistory" :key="index"
          :class="{ 'user-message': message.isUser }">
          {{ message.content }}
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import ChatInterface from '@/components/chat/ChatInterface.vue'
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()
const showHistory = ref(false)

const chatHistory = computed(() => chatStore.messages)

const toggleHistory = () => {
  showHistory.value = !showHistory.value
}
</script>

<style scoped>
.chat-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem;
  background: white;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
  z-index: 100;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.back-btn, .adventure-btn {
  margin: 0 0.5rem;
}

.user-message {
  background: var(--v-primary-lighten-1);
  border-radius: 8px;
  margin: 4px 0;
  padding: 8px;
}
</style>
