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
    });    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
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
  }

  // Streaming version for typing effect
  async sendTextMessageStream(message, history, onChunk, abortSignal) {
    // Format the history correctly for the API
    const formattedHistory = history?.map(msg => ({
      role: msg.type,
      content: msg.text
    }));

    const eventSource = new EventSource(
      `http://localhost:5000/chat/stream`,
      { withCredentials: false }
    );

    // Send the message data via POST to initiate streaming
    try {
      const response = await fetch('http://localhost:5000/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          history: formattedHistory
        }),
        signal: abortSignal
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Read the stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      try {
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) break;
          
          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');
            for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                if (data.chunk) {
                  onChunk(data.chunk);
                } else if (data.type === 'complete') {
                  return;
                } else if (data.error || data.type === 'error') {
                  throw new Error(data.error || 'Stream error');
                }
              } catch (parseError) {
                console.warn('Failed to parse SSE data:', line);
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }    } catch (error) {
      if (error.name === 'AbortError') {
        throw error;
      }
      throw error;
    }
  }
}

export default new ApiService();
