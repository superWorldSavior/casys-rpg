<template>
  <v-container fluid class="chat-view fill-height pa-0">
    <v-row no-gutters class="fill-height">
      <v-col cols="12" class="d-flex flex-column">
        <chat-interface />
      </v-col>
    </v-row>
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
}
</style>
