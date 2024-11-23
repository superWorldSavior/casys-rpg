// Storage service for managing chapters and user preferences
const storageService = {
  // Get all chapters from local storage
  getAllChapters: async () => {
    try {
      const keys = Object.keys(localStorage).filter(key => key.startsWith('book_'));
      return keys;
    } catch (error) {
      console.error('Error getting chapters:', error);
      return [];
    }
  },

  // Get a specific chapter from local storage
  getChapter: async (key) => {
    try {
      const content = localStorage.getItem(key);
      return content ? JSON.parse(content) : null;
    } catch (error) {
      console.error('Error getting chapter:', error);
      return null;
    }
  },

  // Save a chapter to local storage
  saveChapter: async (key, content) => {
    try {
      localStorage.setItem(key, JSON.stringify(content));
      return true;
    } catch (error) {
      console.error('Error saving chapter:', error);
      return false;
    }
  }
};

export { storageService };
