// Main chat view
import { useState } from 'react';
import ChatHeader from '../components/Header';
import ChatMessageList from '../components/ChatMessageList';
import ChatInput from '../components/ChatInput';
import ChatSidebar from '../components/Sidebar';
import { useChatViewModel } from '../viewmodels/ChatViewModel';

export default function ChatView() {  const {
    chatHistory,
    currentChat,
    isProcessing,
    fileState,
    createNewChat,
    selectChat,
    deleteChat,
    sendMessage,
    stopProcessing,
    handleFile,
    clearFile
  } = useChatViewModel();

  const [showSidebar, setShowSidebar] = useState(false);
  const [suggestedPrompt, setSuggestedPrompt] = useState('');

  const hasMessages = currentChat?.messages.length > 0;

  const handleSuggestionClick = (suggestion) => {
    setSuggestedPrompt(suggestion);
  };

  const handleSubmit = (message, file) => {
    sendMessage(message, file);
    setSuggestedPrompt('');
  };

  const handleNewChat = () => {
    createNewChat();
    setShowSidebar(false);
  };

  const handleChatSelect = (chatId) => {
    selectChat(chatId);
    setShowSidebar(false);
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--bg-primary)' }}>
      <ChatSidebar
        isOpen={showSidebar}
        onToggle={() => setShowSidebar(!showSidebar)}
        chatHistory={chatHistory}
        currentChatId={currentChat?.id}
        onChatSelect={handleChatSelect}
        onNewChat={handleNewChat}
        onDeleteChat={deleteChat}
      />      <div className={`transition-all duration-300 ${showSidebar ? 'lg:ml-80' : 'ml-0'}`}>
        {/* Fixed Header */}
        <div className="fixed top-0 right-0 left-0 z-40 flex items-center justify-between text-[22px] font-medium p-5 backdrop-blur-md border-b transition-all duration-300" 
             style={{ 
               backgroundColor: 'rgba(19, 19, 20, 0.95)', 
               borderColor: 'var(--border-color)',
               color: 'var(--text-primary)',
               marginLeft: showSidebar ? '20rem' : '0'
             }}>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowSidebar(!showSidebar)}
              className="p-2 rounded-lg hover:bg-opacity-80 transition-all duration-200"
              style={{ backgroundColor: 'var(--bg-secondary)' }}
            >
              <span className="material-symbols-rounded text-xl" style={{ color: 'var(--text-primary)' }}>
                {showSidebar ? 'menu_open' : 'menu'}
              </span>
            </button>
            <p className="font-semibold">Datagent</p>
          </div>
          <img 
            src="./user_icon.png" 
            alt="profile" 
            className='w-10 h-10 rounded-full ring-2 ring-opacity-20 hover:ring-opacity-40 transition-all duration-200' 
            style={{ ringColor: 'var(--accent-blue)' }}
          />
        </div>

        {/* Content with top padding to account for fixed header */}
        <div className="pt-20"></div>

        <div className="container mx-auto max-w-4xl px-4">
          {!hasMessages && (
            <ChatHeader onSuggestionClick={handleSuggestionClick} />
          )}

          <div className="pb-40">
            {currentChat && (
              <ChatMessageList messages={currentChat.messages} />
            )}
          </div>          <ChatInput
            onSubmit={handleSubmit}
            isProcessing={isProcessing}
            onStop={stopProcessing}
            fileState={fileState}
            onFileChange={handleFile}
            onClearFile={clearFile}
            suggestedPrompt={suggestedPrompt}
            onPromptChange={setSuggestedPrompt}
          />
        </div>
      </div>
    </div>
  );
}
