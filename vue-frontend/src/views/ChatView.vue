<template>
  <v-container fluid class="chat-view fill-height pa-0">
    <!-- Boutons flottants -->
    <v-btn
      icon="mdi-arrow-left"
      size="large"
      class="float-btn return-btn"
      @click="$router.push('/library')"
    >
      <v-tooltip activator="parent" location="right">
        Retour à la bibliothèque
      </v-tooltip>
    </v-btn>
    
    <v-btn
      :icon="isPinned ? 'mdi-pin-off' : 'mdi-pin'"
      size="large"
      class="float-btn pin-btn"
      @click="togglePin"
    >
      <v-tooltip activator="parent" location="left">
        {{ isPinned ? 'Détacher' : 'Épingler' }}
      </v-tooltip>
    </v-btn>

    <v-row no-gutters class="fill-height">
      <v-col :cols="isPinned ? 8 : 12" class="d-flex flex-column transition-width">
        <chat-interface />
      </v-col>
      
      <v-col v-if="isPinned" cols="4" class="book-preview">
        <!-- Zone de prévisualisation du livre -->
        <v-card class="fill-height">
          <v-card-title>Prévisualisation</v-card-title>
          <v-card-text>
            Contenu du livre en cours de lecture...
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ChatInterface from '@/components/ChatInterface.vue'

const isPinned = ref(false)

const togglePin = () => {
  isPinned.value = !isPinned.value
}
</script>

<style scoped>
.chat-view {
  height: 100%;
  max-height: 100vh;
  overflow: hidden;
  position: relative;
}

.float-btn {
  position: fixed !important;
  z-index: 100;
}

.return-btn {
  top: 1rem;
  left: 1rem;
}

.pin-btn {
  top: 1rem;
  right: 1rem;
}

.transition-width {
  transition: width 0.3s ease;
}

.book-preview {
  border-left: 1px solid rgba(0, 0, 0, 0.12);
  background-color: var(--v-surface-variant);
}
</style>
