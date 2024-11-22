<template>
  <div class="min-h-screen bg-background">
    <main class="container mx-auto px-4 py-6 space-y-8">
      <header class="space-y-2">
        <h1 class="text-3xl font-bold tracking-tight md:text-4xl">Solo RPG AI Narrator</h1>
        <p class="text-muted-foreground">Your personal AI-powered storytelling companion</p>
      </header>

      <div class="grid gap-6 sm:grid-cols-1 md:grid-cols-2">
        <section class="p-6 bg-card text-card-foreground rounded-lg shadow-sm space-y-4">
          <h2 class="text-2xl font-semibold">Recent Adventures</h2>
          <div class="space-y-4">
            <div v-for="(adventure, index) in recentAdventures" :key="index" 
                 class="p-4 border rounded-md hover:bg-accent/50 transition-colors">
              <h3 class="font-medium">{{ adventure.title }}</h3>
              <p class="text-sm text-muted-foreground">Last played: {{ adventure.lastPlayed }}</p>
              <div class="mt-3 flex gap-2">
                <Button size="sm" variant="secondary">Continue</Button>
                <Button size="sm" variant="ghost">View Details</Button>
              </div>
            </div>
          </div>
        </section>

        <section class="p-6 bg-card text-card-foreground rounded-lg shadow-sm space-y-4">
          <h2 class="text-2xl font-semibold">Start New Adventure</h2>
          <div class="space-y-4">
            <div class="space-y-2">
              <label class="text-sm font-medium">Adventure Type</label>
              <select class="w-full p-2 border rounded-md bg-background">
                <option>Fantasy Quest</option>
                <option>Sci-Fi Exploration</option>
                <option>Mystery Investigation</option>
              </select>
            </div>
            <Button class="w-full">Create New Adventure</Button>
          </div>
        </section>
      </div>

      <section class="p-6 bg-card text-card-foreground rounded-lg shadow-sm space-y-4">
        <h2 class="text-2xl font-semibold">Quick Actions</h2>
        <div class="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
          <Button variant="outline" class="h-24 flex flex-col items-center justify-center gap-2">
            <span class="text-lg">📚</span>
            <span class="text-sm">Library</span>
          </Button>
          <Button variant="outline" class="h-24 flex flex-col items-center justify-center gap-2">
            <span class="text-lg">⚔️</span>
            <span class="text-sm">Characters</span>
          </Button>
          <Button variant="outline" class="h-24 flex flex-col items-center justify-center gap-2">
            <span class="text-lg">🎲</span>
            <span class="text-sm">Dice Roll</span>
          </Button>
          <Button variant="outline" class="h-24 flex flex-col items-center justify-center gap-2">
            <span class="text-lg">⚙️</span>
            <span class="text-sm">Settings</span>
          </Button>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import Button from '../components/ui/button/button.vue'

const recentAdventures = [
  {
    title: "The Crystal Caverns",
    lastPlayed: "2 hours ago"
  },
  {
    title: "Space Station Omega",
    lastPlayed: "Yesterday"
  }
]
</script>
