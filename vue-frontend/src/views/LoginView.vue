<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="title">RPG AI Narrator</h1>
      <p class="welcome-text">Bienvenue dans votre compagnon de jeu de rôle</p>
      <LoginForm />
    </div>
  </div>
</template>

<script setup lang="ts">
import LoginForm from '@/components/features/auth/LoginForm.vue'
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f6f8;
}

.login-card {
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
  width: 100%;
  max-width: 400px;
  margin: 1rem;
}

.title {
  color: #1a73e8;
  font-size: 2rem;
  margin-bottom: 1rem;
}

.welcome-text {
  color: #5f6368;
  margin-bottom: 2rem;
  font-size: 1.1rem;
}

.login-btn {
  width: 100%;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 4px;
  background-color: #1a73e8;
  color: white;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.login-btn:hover {
  background-color: #1557b0;
}
</style>
