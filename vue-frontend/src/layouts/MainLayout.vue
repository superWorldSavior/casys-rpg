<template>
  <div class="app-layout">
    <template v-if="!isLoginPage">
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
          <button class="theme-toggle desktop-only" @click="toggleTheme">
            {{ theme === 'light' ? '🌙' : '☀️' }}
          </button>
        </div>
      </header>
    </template>
    
    <main class="app-main" :class="{ 'no-padding': isLoginPage }">
      <router-view></router-view>
    </main>

    <template v-if="!isLoginPage">
      <!-- Mobile Bottom Navigation -->
      <nav class="mobile-nav">
        <router-link to="/" class="nav-item" active-class="active">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          </svg>
          <span>Accueil</span>
        </router-link>
        <router-link to="/library" class="nav-item" active-class="active">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>
          </svg>
          <span>Bibliothèque</span>
        </router-link>
        <router-link to="/browse" class="nav-item" active-class="active">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <span>Parcourir</span>
        </router-link>
        <router-link to="/profile" class="nav-item" active-class="active">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
          <span>Profil</span>
        </router-link>
        
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
  padding: 0.75rem 1rem;
  background-color: var(--header-background);
  border-bottom: 1px solid var(--border-color);
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
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
  color: var(--text-color-secondary);
  text-decoration: none;
  flex: 1;
  transition: all 0.2s ease;
}

.nav-item svg {
  margin-bottom: 0.25rem;
  width: 24px;
  height: 24px;
  stroke-width: 1.5;
}

.nav-item span {
  font-size: 0.75rem;
  font-weight: 500;
}

.nav-item.active {
  color: var(--accent-color);
}

.nav-item.active svg {
  stroke-width: 2;
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
