import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

interface ReadingProgress {
  bookId: string;
  currentSection: number;
  totalSections: number;
  lastRead: Date;
}

export const useProgressStore = defineStore('progress', () => {
  const progress = ref<Map<string, ReadingProgress>>(new Map());

  // Initialize from localStorage
  const storedProgress = localStorage.getItem('readingProgress');
  if (storedProgress) {
    progress.value = new Map(Object.entries(JSON.parse(storedProgress)));
  }

  const getProgress = (bookId: string) => {
    return progress.value.get(bookId);
  };

  const updateProgress = (bookId: string, currentSection: number, totalSections: number) => {
    progress.value.set(bookId, {
      bookId,
      currentSection,
      totalSections,
      lastRead: new Date()
    });
    
    // Save to localStorage
    const progressObject = Object.fromEntries(progress.value);
    localStorage.setItem('readingProgress', JSON.stringify(progressObject));
  };

  const getPercentage = (bookId: string) => {
    const bookProgress = progress.value.get(bookId);
    if (!bookProgress) return 0;
    return Math.round((bookProgress.currentSection / bookProgress.totalSections) * 100);
  };

  return {
    progress,
    getProgress,
    updateProgress,
    getPercentage
  };
});
