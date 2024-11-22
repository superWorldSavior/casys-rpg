<template>
  <div class="app-layout">
    <template v-if="!isLoginPage">
      <!-- Desktop Header -->
      <header class="app-header desktop-only">
        <nav class="navigation">
          <router-link to="/library" class="nav-link">Bibliothèque</router-link>
          <router-link to="/reader" class="nav-link">Lecteur</router-link>
          <button class="theme-toggle" @click="toggleTheme">
            {{ theme === 'light' ? '🌙' : '☀️' }}
          </button>
        </nav>
      </header>
    </template>
    
    <main class="app-main" :class="{ 'no-padding': isLoginPage }">
      <router-view></router-view>
    </main>

    <template v-if="!isLoginPage">
      <!-- Mobile Bottom Navigation -->
      <nav class="mobile-nav">
        <router-link to="/library" class="nav-item" active-class="active">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>
          </svg>
          <span>Bibliothèque</span>
        </router-link>
        <router-link to="/reader" class="nav-item" active-class="active">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
          </svg>
          <span>Lecteur</span>
        </router-link>
        <button class="nav-item theme-toggle" @click="toggleTheme">
          <svg v-if="theme === 'light'" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="4"/>
            <path d="M12 2v2"/>
            <path d="M12 20v2"/>
            <path d="m4.93 4.93 1.41 1.41"/>
            <path d="m17.66 17.66 1.41 1.41"/>
            <path d="M2 12h2"/>
            <path d="M20 12h2"/>
            <path d="m6.34 17.66-1.41 1.41"/>
            <path d="m19.07 4.93-1.41 1.41"/>
          </svg>
          <span>{{ theme === 'light' ? 'Sombre' : 'Clair' }}</span>
        </button>
      </nav>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useThemeStore } from '../stores/theme'

const route = useRoute()
const themeStore = useThemeStore()
const isLoginPage = computed(() => route.name === 'login')
const theme = computed(() => themeStore.theme)
const toggleTheme = () => themeStore.toggleTheme()
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding-bottom: env(safe-area-inset-bottom);
}

.app-header {
  padding: 1rem;
  background-color: var(--header-background);
  border-bottom: 1px solid var(--border-color);
}

.navigation {
  display: flex;
  gap: 1rem;
  justify-content: center;
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
  padding-bottom: 4rem; /* Space for mobile navigation */
}

/* Mobile Navigation */
.mobile-nav {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: var(--header-background);
  border-top: 1px solid var(--border-color);
  padding: 0.5rem;
  z-index: 1000;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem;
  color: var(--text-color);
  text-decoration: none;
  flex: 1;
  transition: all 0.2s ease;
}

.nav-item svg {
  margin-bottom: 0.25rem;
}

.nav-item span {
  font-size: 0.75rem;
}

.nav-item.active {
  color: var(--accent-color);
}

.theme-toggle {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-color);
  padding: 0.5rem;
}

.theme-toggle:hover {
  transform: scale(1.1);
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
