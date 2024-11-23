<template>
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

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
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

@media (max-width: 768px) {
  .mobile-nav {
    display: flex;
    justify-content: space-around;
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
