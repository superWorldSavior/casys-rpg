<template>
  <div class="min-h-screen bg-background font-sans antialiased">
    <RouterView v-slot="{ Component }">
      <Transition name="fade" mode="out-in">
        <component :is="Component" />
      </Transition>
    </RouterView>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { RouterView } from 'vue-router'
import { useMediaQuery } from '@vueuse/core'

const prefersDark = useMediaQuery('(prefers-color-scheme: dark)')

const updateTheme = (isDark: boolean) => {
  if (isDark) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

onMounted(() => {
  updateTheme(prefersDark.value)
})

watch(prefersDark, (newValue) => {
  updateTheme(newValue)
})
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
