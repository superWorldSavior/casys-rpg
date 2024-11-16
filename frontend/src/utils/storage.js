import Client from "@replit/database";

const db = new Client();

export const storageService = {
  async saveChapter(key, content) {
    return await db.set(key, content);
  },
  async getChapter(key) {
    return await db.get(key);
  },
  async getAllChapters() {
    return await db.list();
  }
};
