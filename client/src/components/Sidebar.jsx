// Chat history navigation sidebar
import { useState } from 'react';
import StorageStats from './StorageStats.jsx';

export default function Sidebar({ 
  isOpen, 
  onToggle, 
  chatHistory, 
  currentChatId, 
  onChatSelect, 
  onNewChat, 
  onDeleteChat 
}) {
  const [hoveredChatId, setHoveredChatId] = useState(null);
  const [showStorageStats, setShowStorageStats] = useState(false);

  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const chatDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    
    if (chatDate.getTime() === today.getTime()) {
      return 'Today';
    } else if (chatDate.getTime() === today.getTime() - 86400000) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString();
    }
  };
  return (
    <>
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onToggle}
        />
      )}
      
      <div className={`fixed left-0 top-0 h-full z-50 transition-all duration-300 ${
        isOpen ? 'w-80' : 'w-0'
      } overflow-hidden`}>
        <div className="w-80 h-full flex flex-col" style={{ backgroundColor: 'var(--bg-secondary)' }}>
          <div className="flex items-center justify-between p-4 border-b" style={{ borderColor: 'var(--border-color)' }}>
            <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
              Chat History
            </h2>
            <button
              onClick={onToggle}
              className="p-2 rounded-lg hover:bg-opacity-80 transition-all duration-200"
              style={{ backgroundColor: 'var(--bg-hover)' }}
            >
              <span className="material-symbols-rounded text-xl" style={{ color: 'var(--text-primary)' }}>
                close
              </span>
            </button>
          </div>          <div className="p-4 space-y-2">
            <button
              onClick={onNewChat}
              className="w-full flex items-center gap-3 p-3 rounded-lg border transition-all duration-200 hover:scale-105"
              style={{ 
                backgroundColor: 'var(--bg-primary)', 
                borderColor: 'var(--border-color)',
                color: 'var(--text-primary)'
              }}
            >
              <span className="material-symbols-rounded">add</span>
              <span>New Chat</span>
            </button>
            
            <button
              onClick={() => setShowStorageStats(true)}
              className="w-full flex items-center gap-3 p-3 rounded-lg border transition-all duration-200 hover:scale-105"
              style={{ 
                backgroundColor: 'var(--bg-primary)', 
                borderColor: 'var(--border-color)',
                color: 'var(--text-secondary)'
              }}
            >
              <span className="material-symbols-rounded">storage</span>
              <span>Storage Info</span>
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-2">
            {chatHistory.length === 0 ? (
              <div className="text-center py-8" style={{ color: 'var(--text-secondary)' }}>
                <p>No chat history yet</p>
                <p className="text-sm mt-2">Start a conversation to see it here</p>
              </div>
            ) : (
              <>
                {Object.entries(
                  chatHistory.reduce((groups, chat) => {
                    const date = formatDate(chat.timestamp);
                    if (!groups[date]) groups[date] = [];
                    groups[date].push(chat);
                    return groups;
                  }, {})
                ).map(([date, chats]) => (
                  <div key={date} className="mb-4">
                    <h3 className="text-sm font-medium mb-2 px-2" style={{ color: 'var(--text-secondary)' }}>
                      {date}
                    </h3>
                    {chats.map((chat) => (
                      <div
                        key={chat.id}
                        className={`group relative flex items-center p-3 rounded-lg cursor-pointer transition-all duration-200 hover:scale-105 ${
                          currentChatId === chat.id ? 'ring-2' : ''
                        }`}
                        style={{
                          backgroundColor: currentChatId === chat.id ? 'var(--bg-hover)' : 'transparent',
                          ringColor: currentChatId === chat.id ? 'var(--accent-blue)' : 'transparent'
                        }}
                        onClick={() => onChatSelect(chat.id)}
                        onMouseEnter={() => setHoveredChatId(chat.id)}
                        onMouseLeave={() => setHoveredChatId(null)}
                      >
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate" style={{ color: 'var(--text-primary)' }}>
                            {chat.getDisplayTitle()}
                          </p>
                          <p className="text-xs mt-1 truncate" style={{ color: 'var(--text-secondary)' }}>
                            {chat.messages?.length || 0} messages
                          </p>
                        </div>
                        
                        {(hoveredChatId === chat.id || currentChatId === chat.id) && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onDeleteChat(chat.id);
                            }}
                            className="ml-2 p-1 rounded hover:bg-red-500 hover:bg-opacity-20 transition-all duration-200"
                            title="Delete chat"
                          >
                            <span className="material-symbols-rounded text-sm" style={{ color: '#ea4335' }}>
                              delete
                            </span>
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                ))}
              </>            )}
          </div>
        </div>
      </div>

      <StorageStats 
        isOpen={showStorageStats} 
        onClose={() => setShowStorageStats(false)} 
      />
    </>
  );
}
