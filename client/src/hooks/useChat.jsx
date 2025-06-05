// hooks/useChat.js
import { useState, useRef, useEffect } from 'react';

export default function useChat() {
  const [chats, setChats] = useState([]);
  const [isResponding, setIsResponding] = useState(false);
  const [fileState, setFileState] = useState({ file: null, preview: null });
  const abortController = useRef(null);
  const typingInterval = useRef(null);

  const API_KEY = import.meta.env.VITE_GEMINI_API_KEY;
  const API_URL = 'http://127.0.0.1:5000/query/text'; //`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent`;

  // Clear intervals on unmount
  useEffect(() => {
    return () => {
      if (typingInterval.current) clearInterval(typingInterval.current);
    };
  }, []);

  const handleSubmit = async (message, file) => {
    if (!message.trim() || isResponding) return;

    // Add user message
    const userMessage = {
      type: 'user',
      text: message,
      file: file.preview ? { preview: file.preview, name: file.file.name } : null
    };

    setChats(prev => [...prev, userMessage]);

    // Add temporary bot message
    setChats(prev => [...prev, { type: 'bot', text: '', loading: true }]);
    setIsResponding(true);
    abortController.current = new AbortController();

    try {
      // Format conversation history for API
      const history = chats.map(chat => ({
        role: chat.type === 'user' ? 'user' : 'model',
        parts: [
          { text: chat.text },
          ...(chat.file ? [{
            inline_data: {
              mime_type: chat.file.type,
              data: chat.file.preview.split(',')[1]
            }
          }] : [])
        ]
      }));
  
      // Add new user message to history
      const newHistory = [
        ...history,
        {
          role: 'user',
          parts: [
            { text: message },
            ...(file.file ? [{
              inline_data: {
                mime_type: file.file.type,
                data: file.preview.split(',')[1]
              }
            }] : [])
          ]
        }
      ];
  
      const requestBody = {
        contents: newHistory,
        generationConfig: {
          maxOutputTokens: 2048 // Helps maintain context
        }
      };

      const response = await fetch(`${API_URL}`, {
        method: 'GET',
        headers: { 
          // 'Content-Type': 'application/json',
                    'question': message,
                    'debug': 'False'
                },
        //body: JSON.stringify(requestBody),
        signal: abortController.current.signal
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }

      const data = await response.json();
      if (!data?.candidates?.[0]?.content?.parts?.[0]?.text) {
        throw new Error('No valid response from API');
      }
    
      const responseText = data.candidates[0].content.parts[0].text;
    
      // Update state
      setChats(prev => [
        ...prev.slice(0, -1),
        { 
          type: 'bot', 
          text: responseText || "Sorry, I couldn't process that", 
          loading: false,
          meta: {
            timestamp: new Date().toISOString(),
            model: 'gemini-2.0-flash'
          }
        }
      ]);

    } catch (error) {
      clearInterval(typingInterval.current);
      setChats(prev => [
        ...prev.slice(0, -1),
        { type: 'bot', text: error.message, loading: false, error: true }
      ]);
    } finally {
      setIsResponding(false);
      abortController.current = null;
      setFileState({ file: null, preview: null });
    }
  };

  const stopResponse = () => {
    if (abortController.current) {
      abortController.current.abort();
      clearInterval(typingInterval.current);
      setIsResponding(false);
    }
  };

  const deleteChats = () => {
    setChats([]);
    setIsResponding(false);
  };

  const handleFile = (file) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      setFileState({
        file,
        preview: e.target.result,
        name: file.name,
        type: file.type
      });
    };
    reader.readAsDataURL(file);
  };

  const cancelFile = () => {
    setFileState({ file: null, preview: null });
  };

  return {
    chats,
    isResponding,
    handleSubmit,
    stopResponse,
    deleteChats,
    fileState,
    handleFile,
    cancelFile
  };
}