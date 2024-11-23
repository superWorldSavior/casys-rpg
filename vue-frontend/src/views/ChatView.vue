<template>
  <v-container fluid class="chat-view fill-height pa-0">
    <!-- Barre fixe en haut -->
    <v-app-bar elevation="1" class="top-bar">
      <v-btn
        icon="mdi-arrow-left"
        @click="$router.push('/library')"
      >
        <v-tooltip activator="parent">Retour à la bibliothèque</v-tooltip>
      </v-btn>
      <v-spacer></v-spacer>
      <v-btn
        icon="mdi-file-document"
        @click="toggleHistory"
      >
        <v-tooltip activator="parent">Feuille d'aventure</v-tooltip>
      </v-btn>
    </v-app-bar>

    <!-- Interface principale -->
    <div class="main-container">
      <chat-interface class="chat-interface" />
      
      <!-- Drawer pour la feuille d'aventure -->
      <v-navigation-drawer
        v-model="showHistory"
        location="right"
        temporary
        class="history-drawer"
      >
        <v-list>
          <v-list-item>
            <v-btn icon="mdi-close" @click="showHistory = false"></v-btn>
            <v-list-item-title>Feuille d'aventure</v-list-item-title>
          </v-list-item>
          <v-divider></v-divider>
          <v-list-item
            v-for="(message, index) in chatHistory"
            :key="index"
            :class="{ 'user-message': message.isUser }"
          >
            <v-list-item-title>
              {{ message.content }}
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </v-navigation-drawer>
    </div>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import ChatInterface from '@/components/ChatInterface.vue'
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()
const showHistory = ref(false)

const chatHistory = computed(() => chatStore.messages)

const toggleHistory = () => {
  showHistory.value = !showHistory.value
}
</script>

<style scoped>
.chat-view {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
}

.top-bar {
  position: sticky;
  top: 0;
  z-index: 100;
}

.main-container {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.chat-interface {
  height: 100%;
  width: 100%;
  overflow-y: auto;
  padding: 1rem;
}

.history-drawer {
  padding-top: 0;
  height: 100%;
}

.user-message {
  background-color: var(--v-primary-lighten-1);
  margin: 4px 0;
  border-radius: 8px;
}

/* Styles tactiles */
@media (max-width: 768px) {
  .history-drawer {
    width: 100% !important;
  }
}
</style>
