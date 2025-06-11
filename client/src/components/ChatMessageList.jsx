// ChatMessageList component - renders list of chat messages
import { useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';

export default function ChatMessageList({ messages }) {
  const messagesEndRef = useRef(null);
  const containerRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Auto-scroll when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Also scroll when the last message is being updated (for streaming responses)
  useEffect(() => {
    const lastMessage = messages[messages.length - 1];
    if (lastMessage && lastMessage.loading) {
      // For loading messages, scroll immediately without smooth behavior
      messagesEndRef.current?.scrollIntoView({ behavior: 'auto' });
    }
  }, [messages[messages.length - 1]?.text, messages[messages.length - 1]?.loading]);
  return (
    <div ref={containerRef} className="space-y-4">
      {messages.map((message, index) => (
        <ChatMessage 
          key={index} 
          {...message} 
          isSummary={message.isSummary || false}
        />
      ))}
      {/* Invisible element to scroll to */}
      <div ref={messagesEndRef} />
    </div>
  );
}
