// Chat ViewModel - handles all chat business logic
import { useState, useRef, useEffect } from 'react';
import { Chat, ChatMessage, FileState } from '../models/ChatModels.js';
import ApiService from '../services/ApiService.js';
import StorageService from '../services/StorageService.js';

export function useChatViewModel() {  const [chatHistory, setChatHistory] = useState([]);
  const [currentChat, setCurrentChat] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [fileState, setFileState] = useState(new FileState());
  const abortController = useRef(null);  // Load chat history on mount
  useEffect(() => {
    const loadHistory = async () => {
      try {
        const history = await StorageService.loadChatHistory();
        // Ensure all chats are proper Chat instances
        const validChats = history.map(chat => {
          if (chat instanceof Chat) {
            return chat;
          } else {
            // Recreate as Chat instance if it's a plain object
            const newChat = new Chat(chat.title);
            newChat.id = chat.id;
            newChat.messages = chat.messages || [];
            newChat.timestamp = chat.timestamp;
            newChat.lastUpdated = chat.lastUpdated;
            newChat.hasSummary = chat.hasSummary || false;
            return newChat;
          }
        });
        setChatHistory(validChats);
        if (validChats.length > 0) {
          setCurrentChat(validChats[0]);
        }
      } catch (error) {
        console.error('Failed to load chat history:', error);
        setChatHistory([]);
      }
    };
    
    loadHistory();
  }, []);
  // Save chat history when it changes
  useEffect(() => {
    if (chatHistory.length > 0) {
      // Use async save without blocking UI
      StorageService.saveChatHistory(chatHistory).catch(error => {
        console.error('Failed to save chat history:', error);
        // Could show user notification here
      });
    }
  }, [chatHistory]);
  // Update current chat in history
  useEffect(() => {
    if (currentChat) {
      setChatHistory(prev => 
        prev.map(chat => {
          if (chat.id === currentChat.id) {
            // Ensure it's a proper Chat instance
            if (currentChat instanceof Chat) {
              return currentChat;
            } else {
              const newChat = new Chat(currentChat.title);
              Object.assign(newChat, currentChat);
              return newChat;
            }
          }
          return chat;
        }).sort((a, b) => b.lastUpdated - a.lastUpdated)
      );
    }
  }, [currentChat]);

  const createNewChat = () => {
    const newChat = new Chat();
    setChatHistory(prev => [newChat, ...prev]);
    setCurrentChat(newChat);
    setIsProcessing(false);
  };

  const selectChat = (chatId) => {
    const chat = chatHistory.find(c => c.id === chatId);
    if (chat) {
      setCurrentChat(chat);
      setIsProcessing(false);
    }
  };

  const deleteChat = (chatId) => {
    setChatHistory(prev => {
      const updated = prev.filter(chat => chat.id !== chatId);
      
      if (currentChat?.id === chatId) {
        setCurrentChat(updated.length > 0 ? updated[0] : null);
      }
      
      return updated;
    });
  };
  const sendMessage = async (message, file) => {
    if (!message.trim() || isProcessing) return;

    // Create new chat if none exists
    if (!currentChat) {
      const newChat = new Chat();
      newChat.title = message.length > 30 ? message.substring(0, 30) + '...' : message;
      setChatHistory(prev => [newChat, ...prev]);
      setCurrentChat(newChat);
    }

    const activeChat = currentChat || new Chat();

    // Add user message
    const userMessage = new ChatMessage('user', message, file.hasFile() ? {
      preview: file.preview,
      name: file.name,
      type: file.type
    } : null);
    
    activeChat.addMessage(userMessage);

    // Clear file state immediately after adding the user message
    setFileState(new FileState());    // Add loading bot message
    const botMessage = new ChatMessage('bot', 'Thinking...', null, true);activeChat.addMessage(botMessage);
    
    // Ensure currentChat is a proper Chat instance
    const updatedChat = activeChat instanceof Chat ? activeChat : new Chat(activeChat.title);
    if (!(activeChat instanceof Chat)) {
      Object.assign(updatedChat, activeChat);
    }
    setCurrentChat(updatedChat);
    setIsProcessing(true);

    abortController.current = new AbortController();

    try {
      let response;
      
      if (file.hasFile()) {
        response = await ApiService.sendFileMessage(file.file, message, activeChat.messages);
      } else {
        response = await ApiService.sendTextMessage(message, activeChat.messages);
      }      // Update bot message with response
      activeChat.updateLastMessage({
        text: response.message,
        loading: false,
        meta: response.metadata
      });

    } catch (error) {
      let errorMessage = 'An error occurred';
      
      if (error.name === 'AbortError') {
        errorMessage = 'Response cancelled';
      } else if (error.response?.data?.error) {
        errorMessage = error.response.data.error;
      } else if (error.message) {
        errorMessage = error.message;
      }

      activeChat.updateLastMessage({
        text: errorMessage,
        loading: false,
        error: true
      });    } finally {
      setIsProcessing(false);
      abortController.current = null;
      // File state is already cleared when message is sent
      
      // Ensure currentChat is a proper Chat instance
      const updatedChat = activeChat instanceof Chat ? activeChat : new Chat(activeChat.title);
      if (!(activeChat instanceof Chat)) {
        Object.assign(updatedChat, activeChat);
      }
      setCurrentChat(updatedChat);
    }
  };

  const stopProcessing = () => {
    if (abortController.current) {
      abortController.current.abort();
      setIsProcessing(false);
    }
  };  const handleFile = (file) => {
    // Create new FileState and set uploading status immediately
    const newFileState = new FileState();
    newFileState.setStatus('uploading');
    setFileState(newFileState);
    
    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      const errorFileState = new FileState();
      errorFileState.setStatus('error', 'File size must be less than 10MB');
      setFileState(errorFileState);
      return;
    }

    // Validate file type
    const allowedTypes = [
      'image/jpeg', 'image/png', 'image/gif', 'image/webp',
      'application/pdf',
      'text/plain', 'text/csv',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ];
    
    if (!allowedTypes.includes(file.type)) {
      const errorFileState = new FileState();
      errorFileState.setStatus('error', 'Unsupported file type');
      setFileState(errorFileState);
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const readyFileState = new FileState();
      readyFileState.setFile(file, e.target.result);
      setFileState(readyFileState);
    };
    reader.onerror = () => {
      const errorFileState = new FileState();
      errorFileState.setStatus('error', 'Failed to read file');
      setFileState(errorFileState);
    };
    reader.readAsDataURL(file);
  };
  const clearFile = () => {
    setFileState(new FileState());
  };

  return {
    // State
    chatHistory,
    currentChat,
    isProcessing,
    fileState,
    
    // Actions
    createNewChat,
    selectChat,
    deleteChat,
    sendMessage,
    stopProcessing,
    handleFile,
    clearFile
  };
}
