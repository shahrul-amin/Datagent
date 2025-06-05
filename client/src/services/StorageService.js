// Local storage service for chat persistence
import { Chat } from '../models/ChatModels.js';

class StorageService {
  constructor() {
    this.STORAGE_KEY = 'datagent-chat-history';
  }

  saveChatHistory(chatHistory) {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(chatHistory));
    } catch (error) {
      console.error('Failed to save chat history:', error);
    }
  }

  loadChatHistory() {
    try {
      const saved = localStorage.getItem(this.STORAGE_KEY);
      if (!saved) return [];
      
      const parsed = JSON.parse(saved);
      return parsed.map(chatData => {
        const chat = new Chat(chatData.title);
        chat.id = chatData.id;
        chat.messages = chatData.messages || [];
        chat.timestamp = chatData.timestamp;
        chat.lastUpdated = chatData.lastUpdated;
        return chat;
      });
    } catch (error) {
      console.error('Failed to load chat history:', error);
      return [];
    }
  }

  clearChatHistory() {
    try {
      localStorage.removeItem(this.STORAGE_KEY);
    } catch (error) {
      console.error('Failed to clear chat history:', error);
    }
  }
}

export default new StorageService();
