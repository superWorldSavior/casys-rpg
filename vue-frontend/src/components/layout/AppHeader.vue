<template>
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

<script setup lang="ts">
// Pas de logique pour l'instant
</script>

<style scoped>
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

@media (max-width: 768px) {
  .app-header {
    padding: 0.5rem;
  }
  
  .credits-button {
    font-size: 0.9rem;
    padding: 0.4rem 0.8rem;
  }
}
</style>
