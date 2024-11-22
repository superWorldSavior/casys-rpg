<template>
  <div class="redirect">
    Redirection vers la page d'accueil...
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

onMounted(() => {
  router.push({ name: 'library' })
})
</script>

<style scoped>
.redirect {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  font-size: 1.2rem;
  color: var(--text-color);
}
</style>
