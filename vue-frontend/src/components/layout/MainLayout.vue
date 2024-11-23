<template>
  <v-app>
    <v-layout>
      <div class="app-layout">
        <template v-if="!isLoginPage && !isFullscreenPage">
          <AppHeader />
        </template>
        
        <v-main>
          <main class="app-main" :class="{ 'no-padding': isLoginPage }">
            <router-view></router-view>
          </main>
        </v-main>

        <template v-if="!isLoginPage && !isFullscreenPage">
          <MobileNavigation />
        </template>
      </div>
    </v-layout>
  </v-app>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { AppHeader, MobileNavigation } from '@/components/layout'

const route = useRoute()
const themeStore = useThemeStore()

const isLoginPage = computed(() => route.name === 'login')
const isFullscreenPage = computed(() => {
  const fullscreenRoutes = ['chat', 'reader']
  return fullscreenRoutes.includes(route.name as string)
})
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding-bottom: env(safe-area-inset-bottom);
}

.no-padding {
  padding: 0;
}

.app-main {
  flex: 1;
  padding: 1rem;
  padding-bottom: calc(4rem + env(safe-area-inset-bottom));
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

@media (max-width: 768px) {
  .app-main {
    padding-bottom: 5rem;
  }
}
</style>
