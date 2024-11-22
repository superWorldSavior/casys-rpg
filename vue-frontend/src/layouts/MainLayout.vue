<template>
  <div class="app-layout">
    <template v-if="!isLoginPage">
      <header class="app-header">
        <nav class="navigation">
          <router-link to="/library" class="nav-link">Bibliothèque</router-link>
          <router-link to="/reader" class="nav-link">Lecteur</router-link>
        </nav>
      </header>
    </template>
    
    <main class="app-main" :class="{ 'no-padding': isLoginPage }">
      <router-view></router-view>
    </main>

    <template v-if="!isLoginPage">
      <footer class="app-footer">
        <div class="controls">
          <!-- Bottom controls will be added here -->
        </div>
      </footer>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isLoginPage = computed(() => route.name === 'login')
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  padding: 1rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.navigation {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.nav-link {
  color: #6c757d;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  transition: all 0.2s ease-in-out;
}

.nav-link:hover {
  background-color: #e9ecef;
}

.no-padding {
  padding: 0;
}

.app-main {
  flex: 1;
  padding: 1rem;
}

.app-footer {
  padding: 1rem;
  background-color: #f8f9fa;
  border-top: 1px solid #e9ecef;
}

.controls {
  display: flex;
  justify-content: center;
  gap: 1rem;
}
</style>
