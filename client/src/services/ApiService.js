// API service for backend communication
import axios from 'axios';

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: 'http://localhost:5000',
      timeout: 100000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Add response interceptor for better error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error);
        if (error.response) {
          console.error('Error response:', error.response.data);
          console.error('Error status:', error.response.status);
        } else if (error.request) {
          console.error('Error request:', error.request);
        } else {
          console.error('Error message:', error.message);
        }
        return Promise.reject(error);
      }
    );
  }
  async sendTextMessage(message, history) {
    // Format the history correctly for the API
    const formattedHistory = history?.map(msg => ({
      role: msg.type,
      content: msg.text
    }));
    
    const response = await this.client.post('/chat', {
      message,
      history: formattedHistory
    });
    return response.data;
  }  async sendFileMessage(file, message, history) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('message', message);
    
    // Format the history correctly for the API
    const formattedHistory = history?.map(msg => ({
      role: msg.type,
      content: msg.text
    }));
    
    formData.append('history', JSON.stringify(formattedHistory));
    
    // Use longer timeout for file uploads (2 minutes)
    const response = await this.client.post('/chat', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000 // 2 minutes for file processing
    });
    return response.data;
  } async sendSequentialAnalysis(file, message, history, sessionId = 'default') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('message', message);
    formData.append('workflow_type', 'sequential');
    formData.append('session_id', sessionId);
    
    // Format the history correctly for the API
    const formattedHistory = history?.map(msg => ({
      role: msg.type,
      content: msg.text
    }));
    
    formData.append('history', JSON.stringify(formattedHistory || []));
    
    const response = await this.client.post('/chat', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  }

  async getChatContext(sessionId) {
    const response = await this.client.get(`/chat/context/${sessionId}`);
    return response.data;
  }

  async clearChatContext(sessionId) {
    const response = await this.client.delete(`/chat/context/${sessionId}`);
    return response.data;
  }
}

export default new ApiService();
