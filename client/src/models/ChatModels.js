// Chat data models

export class ChatMessage {
  constructor(type, text, file = null, loading = false, error = false, meta = null) {
    this.type = type; // 'user' | 'bot'
    this.text = text || ''; // Ensure text is always a string
    this.file = file;
    this.loading = loading;
    this.error = error;
    this.meta = meta;
    this.timestamp = Date.now();
  }
}

export class Chat {
  constructor(title = null) {
    this.id = `chat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.title = title;
    this.messages = [];
    this.timestamp = Date.now();
    this.lastUpdated = Date.now();
    this.hasSummary = false; // Track if chat has been summarized
  }

  addMessage(message) {
    this.messages.push(message);
    this.lastUpdated = Date.now();
  }

  updateLastMessage(updates) {
    if (this.messages.length > 0) {
      Object.assign(this.messages[this.messages.length - 1], updates);
      this.lastUpdated = Date.now();
    }
  }

  getDisplayTitle() {
    if (this.title) return this.title;
    const firstMessage = this.messages[0]?.text || '';
    return firstMessage.length > 30 
      ? firstMessage.substring(0, 30) + '...' 
      : firstMessage || 'New Chat';
  }

  // Get size in bytes for storage management
  getSizeInBytes() {
    return new Blob([JSON.stringify(this)]).size;
  }

  // Get size in MB for storage management
  getSizeInMB() {
    return this.getSizeInBytes() / (1024 * 1024);
  }

  // Check if chat is large enough to warrant summarization
  needsSummarization(maxSizeMB = 100) {
    return this.getSizeInMB() > maxSizeMB;
  }
}

export class FileState {
  constructor() {
    this.file = null;
    this.preview = null;
    this.name = '';
    this.type = '';
    this.size = 0;
    this.status = 'idle'; // 'idle', 'uploading', 'ready', 'error'
    this.error = null;
  }

  setFile(file, preview) {
    this.file = file;
    this.preview = preview;
    this.name = file?.name || '';
    this.type = file?.type || '';
    this.size = file?.size || 0;
    this.status = 'ready';
    this.error = null;
  }

  setStatus(status, error = null) {
    this.status = status;
    this.error = error;
  }

  clear() {
    this.file = null;
    this.preview = null;
    this.name = '';
    this.type = '';
    this.size = 0;
    this.status = 'idle';
    this.error = null;
  }

  hasFile() {
    return this.file !== null;
  }

  isReady() {
    return this.hasFile() && this.status === 'ready';
  }

  isUploading() {
    return this.status === 'uploading';
  }

  hasError() {
    return this.status === 'error';
  }
}
