<template>
  <div class="reader">
    <div class="progress-bar">
      <div 
        class="progress-fill"
        :style="{ width: `${currentPercentage}%` }"
      ></div>
      <span class="progress-text">{{ currentPercentage }}%</span>
    </div>
    <div class="content">
      <div v-if="isLoading" class="loading">
        Chargement...
      </div>
      <div v-else-if="error" class="error">
        {{ error }}
      </div>
      <div v-else class="section-content">
        <h2>{{ currentSection?.title || `Section ${currentSectionNumber}` }}</h2>
        <div v-html="currentSection?.content"></div>
      </div>
    </div>
    <div class="controls">
      <button 
        @click="previousSection" 
        :disabled="currentSectionNumber <= 1"
      >
        Section précédente
      </button>
      <span class="section-info">
        Section {{ currentSectionNumber }} / {{ totalSections }}
      </span>
      <button 
        @click="nextSection" 
        :disabled="currentSectionNumber >= totalSections"
      >
        Section suivante
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useProgressStore } from '../stores/progress';
import { apiClient, handleApiError } from '../utils/api';

interface Section {
  number: number;
  content: string;
  title?: string;
}

const route = useRoute();
const progressStore = useProgressStore();

const bookId = computed(() => route.params.id as string);
const isLoading = ref(false);
const error = ref<string | null>(null);
const sections = ref<Section[]>([]);
const currentSectionNumber = ref(1);

const currentSection = computed(() => 
  sections.value.find(s => s.number === currentSectionNumber.value)
);

const totalSections = computed(() => sections.value.length);

const currentPercentage = computed(() => 
  progressStore.getPercentage(bookId.value) || 0
);

async function loadBook() {
  if (!bookId.value) return;
  
  try {
    isLoading.value = true;
    const response = await apiClient.get(`/books/${bookId.value}/sections`);
    sections.value = response.data.sections;
    
    // Restore progress
    const savedProgress = progressStore.getProgress(bookId.value);
    if (savedProgress) {
      currentSectionNumber.value = savedProgress.currentSection;
    }
  } catch (err) {
    error.value = handleApiError(err);
  } finally {
    isLoading.value = false;
  }
}

function updateProgress() {
  if (!bookId.value || !totalSections.value) return;
  
  progressStore.updateProgress(
    bookId.value,
    currentSectionNumber.value,
    totalSections.value
  );
}

function nextSection() {
  if (currentSectionNumber.value < totalSections.value) {
    currentSectionNumber.value++;
    updateProgress();
  }
}

function previousSection() {
  if (currentSectionNumber.value > 1) {
    currentSectionNumber.value--;
    updateProgress();
  }
}

watch(currentSectionNumber, () => {
  updateProgress();
});

onMounted(() => {
  loadBook();
});
</script>

<style scoped>
.reader {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.progress-bar {
  height: 4px;
  background-color: #e9ecef;
  position: relative;
}

.progress-fill {
  height: 100%;
  background-color: var(--accent-color);
  transition: width 0.3s ease;
}

.progress-text {
  position: absolute;
  right: 8px;
  top: 8px;
  font-size: 0.8rem;
  color: var(--text-color);
}

.content {
  flex: 1;
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
  line-height: 1.6;
  overflow-y: auto;
}

.section-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.controls {
  padding: 1rem;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  background-color: #f8f9fa;
  border-top: 1px solid #e9ecef;
}

.section-info {
  color: var(--text-color);
  font-weight: 500;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: var(--text-color);
}

.error {
  color: #dc3545;
  padding: 1rem;
  text-align: center;
  background-color: #f8d7da;
  border-radius: 4px;
  margin: 1rem 0;
}

button {
  padding: 0.5rem 1rem;
  border: none;
  background-color: var(--accent-color);
  color: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

button:disabled {
  background-color: #e9ecef;
  cursor: not-allowed;
}

button:not(:disabled):hover {
  background-color: var(--secondary-color);
}
</style>
