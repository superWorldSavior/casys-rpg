<template>
  <v-container fluid class="chat-view fill-height pa-0">
    <!-- Boutons flottants -->
    <div class="floating-buttons">
      <v-btn
        icon="mdi-arrow-left"
        size="large"
        class="float-btn return-btn"
        @click="$router.push('/library')"
        v-touch="{
          left: () => $router.push('/library')
        }"
      >
        <v-tooltip activator="parent" location="right">
          Retour à la bibliothèque
        </v-tooltip>
      </v-btn>
      
      <v-btn
        icon="mdi-file-document"
        size="large"
        class="float-btn adventure-sheet-btn"
        @click="showHistory = !showHistory"
        v-touch="{
          tap: () => showHistory = !showHistory
        }"
      >
        <v-tooltip activator="parent" location="left">
          {{ showHistory ? 'Masquer la feuille d\'aventure' : 'Afficher la feuille d\'aventure' }}
        </v-tooltip>
      </v-btn>
    </div>

    <!-- Interface principale -->
    <div class="main-container" :class="{ 'with-history': showHistory }">
      <!-- Historique -->
      <v-navigation-drawer
        v-model="showHistory"
        location="right"
        temporary
        width="300"
        class="history-drawer"
        touchless
      >
        <v-list>
          <v-list-subheader>Historique des messages</v-list-subheader>
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

      <!-- Interface de chat -->
      <chat-interface />
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
</script>

<style scoped>
.chat-view {
  height: 100vh;
  width: 100vw;
  max-height: 100vh;
  max-width: 100vw;
  overflow: hidden;
  position: fixed;
  top: 0;
  left: 0;
  margin: 0;
  padding: 0;
  background-color: var(--v-background);
}

.floating-buttons {
  position: fixed;
  top: 1rem;
  left: 1rem;
  right: 1rem;
  z-index: 100;
  display: flex;
  justify-content: space-between;
}

.float-btn {
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  background-color: var(--v-surface-variant) !important;
}

.main-container {
  height: 100%;
  transition: all 0.3s ease;
}

.main-container.with-history {
  margin-right: 300px;
}

.history-drawer {
  padding-top: 64px;
  background-color: var(--v-surface-variant);
}

.user-message {
  background-color: var(--v-primary-lighten-1);
  margin: 4px 0;
  border-radius: 8px;
}

/* Styles tactiles */
@media (max-width: 768px) {
  .float-btn {
    transform: scale(1.2);
  }

  .main-container.with-history {
    margin-right: 0;
  }

  .history-drawer {
    width: 100% !important;
  }
}
</style>
