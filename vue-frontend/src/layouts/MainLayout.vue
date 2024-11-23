<template>
  <v-app>
    <v-layout>
      <div class="app-layout">
      <template v-if="!isLoginPage && !isFullscreenPage">
        <!-- Desktop Header -->
        <header class="app-header">
          <div class="header-left">
            <router-link to="/" class="logo">casys rpg</router-link>
          </div>
          <div class="header-center">
            <button class="credits-button">
              Acheter des crédits
            </button>
          </div>
          <div class="header-right">
            <button class="search-button">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"/>
                <line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
            </button>
            
          </div>
        </header>
      </template>
      
      <v-main>
        <main class="app-main" :class="{ 'no-padding': isLoginPage }">
          <router-view></router-view>
        </main>
      </v-main>

      <template v-if="!isLoginPage && !isFullscreenPage">
        <!-- Mobile Bottom Navigation -->
        <v-bottom-navigation
          v-model="activeTab"
          grow
          class="mobile-nav"
        >
          <v-btn
            :to="{ path: '/' }"
            value="home"
          >
            <v-icon>mdi-home</v-icon>
            <span>Accueil</span>
          </v-btn>

          <v-btn
            :to="{ path: '/library' }"
            value="library"
          >
            <v-icon>mdi-book-open-variant</v-icon>
            <span>Bibliothèque</span>
          </v-btn>

          <v-btn
            :to="{ path: '/browse' }"
            value="browse"
          >
            <v-icon>mdi-magnify</v-icon>
            <span>Parcourir</span>
          </v-btn>

          <v-btn
            :to="{ path: '/profile' }"
            value="profile"
          >
            <v-icon>mdi-account</v-icon>
            <span>Profil</span>
          </v-btn>
        </v-bottom-navigation>
      </template>
    </div>
    </v-layout>
  </v-app>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useThemeStore } from '../stores/theme'

const route = useRoute()
const themeStore = useThemeStore()
const isLoginPage = computed(() => route.name === 'login')
const isFullscreenPage = computed(() => {
  const fullscreenRoutes = ['chat', 'reader']
  return fullscreenRoutes.includes(route.name as string)
})
const theme = computed(() => themeStore.theme)
const toggleTheme = () => themeStore.toggleTheme()

const activeTab = ref('home')

// Mettre à jour l'onglet actif en fonction de la route
watch(() => route.path, (newPath) => {
  if (newPath === '/') activeTab.value = 'home'
  else if (newPath.startsWith('/library')) activeTab.value = 'library'
  else if (newPath.startsWith('/browse')) activeTab.value = 'browse'
  else if (newPath.startsWith('/profile')) activeTab.value = 'profile'
}, { immediate: true })
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding-bottom: env(safe-area-inset-bottom);
}

.app-header {
  padding: 0.75rem 1rem;
  background-color: var(--header-background);
  border-bottom: 1px solid var(--border-color);
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.header-left, .header-center, .header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--accent-color);
  text-decoration: none;
  letter-spacing: -0.5px;
}

.credits-button {
  background-color: var(--accent-color);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.credits-button:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.search-button {
  background: none;
  border: none;
  padding: 0.5rem;
  color: var(--text-color);
  cursor: pointer;
  border-radius: 9999px;
  transition: all 0.2s ease;
}

.search-button:hover {
  background-color: var(--hover-background);
}

.nav-link {
  color: var(--text-color);
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  transition: all 0.2s ease-in-out;
}

.nav-link:hover {
  background-color: var(--hover-background);
}

.no-padding {
  padding: 0;
}

.app-main {
  flex: 1;
  padding: 1rem;
  padding-bottom: calc(4rem + env(safe-area-inset-bottom)); /* Space for mobile navigation */
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

/* Mobile Navigation */
.mobile-nav {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: rgb(var(--v-theme-surface));
  border-top: 1px solid rgba(var(--v-border-color), 0.12);
  padding: 0.5rem;
  z-index: 1000;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 -1px 8px rgba(0, 0, 0, 0.1);
}

:deep(.v-btn) {
    min-width: unset !important;
    border-radius: 12px !important;
    height: 56px !important;
    font-size: 0.75rem !important;
    transition: all 0.3s ease !important;
    position: relative !important;
    overflow: hidden !important;
    background: transparent !important;
  }

  :deep(.v-btn:hover) {
    background: linear-gradient(45deg, rgba(110, 17, 135, 0.1), rgba(168, 112, 183, 0.2)) !important;
    transform: translateY(-2px) !important;
  }

  :deep(.v-btn:active) {
    background-color: #A870B7 !important;
    transform: translateY(1px) !important;
  }

  :deep(.v-btn--active) {
    background: rgba(168, 112, 183, 0.15) !important;
    border: 1px solid rgba(168, 112, 183, 0.3) !important;
  }

  :deep(.v-btn .v-icon) {
    font-size: 24px !important;
    margin-bottom: 4px !important;
    transition: transform 0.3s ease !important;
  }

  :deep(.v-btn:hover .v-icon) {
    transform: scale(1.1) !important;
  }

  :deep(.v-btn .v-btn__content) {
    flex-direction: column !important;
    line-height: 1 !important;
    color: var(--v-theme-on-surface) !important;
  }

  :deep(.v-btn--active .v-btn__content) {
    color: #A870B7 !important;
  }

:deep(.v-bottom-navigation) {
  height: calc(56px + env(safe-area-inset-bottom)) !important;
  padding-bottom: env(safe-area-inset-bottom) !important;
  position: fixed !important;
  bottom: 0 !important;
  left: 0 !important;
  right: 0 !important;
  z-index: 1000 !important;
  border-top: 1px solid rgba(var(--v-border-color), 0.08) !important;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem 0.35rem;
  color: var(--text-color-secondary);
  text-decoration: none;
  flex: 1;
  transition: all 0.15s ease;
  position: relative;
  border-radius: 12px;
}

.nav-item::before {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 50%;
  width: 4px;
  height: 4px;
  background-color: var(--accent-color);
  border-radius: 50%;
  opacity: 0;
  transform: translateX(-50%) scale(0);
  transition: all 0.2s ease;
}

.nav-item svg {
  margin-bottom: 0.25rem;
  width: 24px;
  height: 24px;
  stroke-width: 1.5;
  transition: all 0.15s ease;
}

.nav-item span {
  font-size: 0.75rem;
  font-weight: 500;
  transition: all 0.15s ease;
  letter-spacing: -0.2px;
}

.nav-item.active {
  color: var(--accent-color);
}

.nav-item.active::before {
  opacity: 1;
  transform: translateX(-50%) scale(1);
}

.nav-item.active {
  color: var(--accent-color);
  background-color: var(--hover-background);
}

.nav-item.active svg {
  stroke-width: 2;
  transform: scale(1.1);
}

.nav-item.active span {
  font-weight: 700;
}

/* Media Queries */
@media (max-width: 768px) {
  .desktop-only {
    display: none;
  }

  .mobile-nav {
    display: flex;
    justify-content: space-around;
  }

  .app-main {
    padding-bottom: 5rem; /* Increased padding to account for navigation */
  }
}

@media (min-width: 769px) {
  .mobile-nav {
    display: none;
  }
}

/* Safe Area Support */
@supports(padding: max(0px)) {
  .mobile-nav {
    padding-bottom: max(0.5rem, env(safe-area-inset-bottom));
    height: max(3.5rem, calc(3.5rem + env(safe-area-inset-bottom)));
  }
}
</style>
