// Storage service for managing text content
export const storageService = {
  async saveChapter(key, content) {
    const response = await fetch('/api/content', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        sections: [content],
      }),
    });
    if (!response.ok) {
      throw new Error('Failed to save chapter');
    }
    return await response.json();
  },

  async getChapter(key) {
    const response = await fetch('/api/text');
    if (!response.ok) {
      throw new Error('Failed to get chapter');
    }
    const chapters = await response.json();
    const chapterIndex = parseInt(key.split('_')[1]) - 1;
    return chapters[chapterIndex];
  },

  async getAllChapters() {
    const response = await fetch('/api/text');
    if (!response.ok) {
      throw new Error('Failed to get chapters');
    }
    const chapters = await response.json();
    return chapters.map((_, index) => `chapter_${index + 1}`);
  }
};
