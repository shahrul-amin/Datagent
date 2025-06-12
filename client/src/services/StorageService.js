// Storage service with IndexedDB and automatic cleanup
import { Chat } from '../models/ChatModels.js';
import ApiService from './ApiService.js';

class StorageService {
  constructor() {
    this.STORAGE_KEY = 'datagent-chat-history';
    this.DB_NAME = 'DatagentChatDB';
    this.DB_VERSION = 1;
    this.STORE_NAME = 'chatHistory';
    this.MAX_CHAT_SIZE_MB = 100;
    this.db = null;
    this.initDB();
  }

  // Initialize IndexedDB
  async initDB() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.DB_NAME, this.DB_VERSION);
        request.onerror = () => {
        reject(request.error);
      };
      
      request.onsuccess = () => {
        this.db = request.result;
        resolve(this.db);
      };
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        if (!db.objectStoreNames.contains(this.STORE_NAME)) {
          const store = db.createObjectStore(this.STORE_NAME, { keyPath: 'id' });
          store.createIndex('lastUpdated', 'lastUpdated', { unique: false });
        }
      };
    });
  }

  // Get chat storage size in MB
  getChatSizeMB(chat) {
    const chatString = JSON.stringify(chat);
    const sizeInBytes = new Blob([chatString]).size;
    return sizeInBytes / (1024 * 1024);
  }

  // Summarize old messages
  async summarizeOldMessages(chat) {
    try {
      if (!chat.messages || chat.messages.length < 10) return chat;

      // Take first 70% of messages for summarization
      const messagesToSummarize = chat.messages.slice(0, Math.floor(chat.messages.length * 0.7));
      const messagesToKeep = chat.messages.slice(Math.floor(chat.messages.length * 0.7));

      // Format messages for summarization
      const conversationText = messagesToSummarize.map(msg => 
        `${msg.type}: ${msg.text}`
      ).join('\n');

      // Call API to summarize
      const summaryResponse = await ApiService.sendTextMessage(
        `Please provide a concise summary of this conversation that captures the key points, decisions, and context. This summary will be used to maintain conversation continuity:\n\n${conversationText}`,
        []
      );

      // Create summary message
      const summaryMessage = {
        id: `summary-${Date.now()}`,
        type: 'assistant',
        text: `[CONVERSATION SUMMARY]: ${summaryResponse.response}`,
        timestamp: new Date().toISOString(),
        isSummary: true
      };      // Update chat with summary + recent messages
      chat.messages = [summaryMessage, ...messagesToKeep];
      chat.hasSummary = true;
        return chat;
    } catch (error) {
      // If summarization fails, just truncate old messages
      chat.messages = chat.messages.slice(-20);
      return chat;
    }
  }
  async checkAndCleanupChat(chat) {
    const sizeInMB = this.getChatSizeMB(chat);
    
    if (sizeInMB > this.MAX_CHAT_SIZE_MB) {
      return await this.summarizeOldMessages(chat);
    }
    
    return chat;
  }

  // Save chat history with cleanup
  async saveChatHistory(chatHistory) {
    try {
      // Ensure DB is initialized
      if (!this.db) {
        await this.initDB();
      }

      // Check and cleanup each chat if needed
      const cleanedHistory = await Promise.all(
        chatHistory.map(chat => this.checkAndCleanupChat(chat))
      );      // Try localStorage first for quick access
      try {
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(cleanedHistory));
      } catch (localStorageError) {
        localStorage.removeItem(this.STORAGE_KEY);
      }

      // Save to IndexedDB
      const transaction = this.db.transaction([this.STORE_NAME], 'readwrite');
      const store = transaction.objectStore(this.STORE_NAME);
      
      // Clear existing data
      await store.clear();
      
      // Save each chat
      for (const chat of cleanedHistory) {
        await store.add({
          id: chat.id,
          title: chat.title,
          messages: chat.messages,
          timestamp: chat.timestamp,
          lastUpdated: chat.lastUpdated,
          hasSummary: chat.hasSummary || false        });
      }
    } catch (error) {
      console.error('Failed to save chat history:', error);
      // Fallback to localStorage without cleanup
      try {
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(chatHistory.slice(-10))); // Keep only last 10 chats
      } catch (fallbackError) {
        console.error('All storage methods failed:', fallbackError);
      }
    }
  }

  // Load chat history
  async loadChatHistory() {
    try {
      // Try localStorage first
      const localData = localStorage.getItem(this.STORAGE_KEY);
      if (localData) {
        const parsed = JSON.parse(localData);
        return this.parseChats(parsed);
      }

      // Fallback to IndexedDB
      if (!this.db) {
        await this.initDB();
      }

      const transaction = this.db.transaction([this.STORE_NAME], 'readonly');
      const store = transaction.objectStore(this.STORE_NAME);
      const request = store.getAll();

      return new Promise((resolve) => {
        request.onsuccess = () => {
          const chats = this.parseChats(request.result);
          // Update localStorage with recent data
          try {
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(request.result));
          } catch (e) {
            // Ignore localStorage errors
          }
          resolve(chats);
        };        
        request.onerror = () => {
          resolve([]);
        };      });
    } catch (error) {
      return [];
    }
  }

  // Parse chat data into objects
  parseChats(chatData) {
    if (!Array.isArray(chatData)) return [];
    
    return chatData.map(data => {
      const chat = new Chat(data.title);
      chat.id = data.id;
      chat.messages = data.messages || [];
      chat.timestamp = data.timestamp;
      chat.lastUpdated = data.lastUpdated;
      chat.hasSummary = data.hasSummary || false;
      return chat;
    }).sort((a, b) => new Date(b.lastUpdated) - new Date(a.lastUpdated));
  }

  // Clear chat history
  async clearChatHistory() {
    try {
      localStorage.removeItem(this.STORAGE_KEY);
      
      if (!this.db) {
        await this.initDB();
      }
        const transaction = this.db.transaction([this.STORE_NAME], 'readwrite');
      const store = transaction.objectStore(this.STORE_NAME);      await store.clear();
    } catch (error) {
      // Silent error handling
    }
  }

  // Get storage statistics
  async getStorageStats() {
    try {
      if (!this.db) {
        await this.initDB();
      }

      const transaction = this.db.transaction([this.STORE_NAME], 'readonly');
      const store = transaction.objectStore(this.STORE_NAME);
      const request = store.getAll();

      return new Promise((resolve) => {
        request.onsuccess = () => {
          const chats = request.result;
          const totalSize = chats.reduce((acc, chat) => {
            return acc + this.getChatSizeMB(chat);
          }, 0);

          resolve({
            totalChats: chats.length,
            totalSizeMB: totalSize.toFixed(2),
            chatsWithSummary: chats.filter(c => c.hasSummary).length,
            largestChatMB: Math.max(...chats.map(c => this.getChatSizeMB(c))).toFixed(2)
          });
        };      });
    } catch (error) {
      return {
        totalChats: 0,
        totalSizeMB: '0',
        chatsWithSummary: 0,
        largestChatMB: '0'
      };
    }
  }
}

export default new StorageService();
