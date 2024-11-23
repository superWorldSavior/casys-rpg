<template>
  <div class="login-form">
    <form @submit.prevent="handleSubmit" class="form">
      <UIInput
        v-model="email"
        label="Email"
        type="email"
        required
        placeholder="Votre email"
        :error="error"
      />
      
      <UIInput
        v-model="password"
        label="Mot de passe"
        type="password"
        required
        placeholder="Votre mot de passe"
        :error="error"
      />

      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Connexion en cours...' : 'Se connecter' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuth } from '@/composables/auth/useAuth';
import { useRouter } from 'vue-router';
import UIInput from '@/components/ui/Input.vue';

const router = useRouter();
const { login, error, isLoading } = useAuth();

const email = ref('');
const password = ref('');

async function handleSubmit() {
  try {
    await login(email.value, password.value);
    router.push('/');
  } catch (e) {
    // L'erreur est déjà gérée dans le composable
    console.error('Erreur de connexion:', e);
  }
}
</script>

<style scoped>
.login-form {
  max-width: 400px;
  margin: 2rem auto;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  width: 100%;
  padding: 0.75rem;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  color: #ff0000;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}
</style>
