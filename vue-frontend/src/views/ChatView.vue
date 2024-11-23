<template>
  <v-container fluid class="chat-view fill-height pa-0">
    <!-- Bouton flottant de retour -->
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

    <!-- Interface de chat -->
    <chat-interface />
  </v-container>
</template>

<script setup lang="ts">
import ChatInterface from '@/components/ChatInterface.vue'
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
</style>
