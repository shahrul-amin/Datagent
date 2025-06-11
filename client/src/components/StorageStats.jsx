// Storage statistics component
import { useState, useEffect } from 'react';
import StorageService from '../services/StorageService.js';

export default function StorageStats({ isOpen, onClose }) {
  const [stats, setStats] = useState({
    totalChats: 0,
    totalSizeMB: '0',
    chatsWithSummary: 0,
    largestChatMB: '0'
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadStats();
    }
  }, [isOpen]);

  const loadStats = async () => {
    setLoading(true);
    try {
      const storageStats = await StorageService.getStorageStats();
      setStats(storageStats);
    } catch (error) {
      console.error('Failed to load storage stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClearHistory = async () => {
    if (window.confirm('Are you sure you want to clear all chat history? This action cannot be undone.')) {
      try {
        await StorageService.clearChatHistory();
        await loadStats();
        onClose();
        // Refresh the page to update the UI
        window.location.reload();
      } catch (error) {
        console.error('Failed to clear chat history:', error);
        alert('Failed to clear chat history. Please try again.');
      }
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6" 
           style={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-color)' }}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>
            Storage Statistics
          </h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg transition-all duration-200"
            style={{ backgroundColor: 'var(--bg-hover)' }}
          >
            <span className="material-symbols-rounded" style={{ color: 'var(--text-primary)' }}>
              close
            </span>
          </button>
        </div>

        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
            <p style={{ color: 'var(--text-secondary)' }}>Loading storage statistics...</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 rounded-lg" style={{ backgroundColor: 'var(--bg-primary)' }}>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Total Chats</p>
                <p className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
                  {stats.totalChats}
                </p>
              </div>
              <div className="p-3 rounded-lg" style={{ backgroundColor: 'var(--bg-primary)' }}>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Total Size</p>
                <p className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
                  {stats.totalSizeMB} MB
                </p>
              </div>
              <div className="p-3 rounded-lg" style={{ backgroundColor: 'var(--bg-primary)' }}>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>With Summary</p>
                <p className="text-2xl font-bold" style={{ color: 'var(--accent-blue)' }}>
                  {stats.chatsWithSummary}
                </p>
              </div>
              <div className="p-3 rounded-lg" style={{ backgroundColor: 'var(--bg-primary)' }}>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Largest Chat</p>
                <p className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
                  {stats.largestChatMB} MB
                </p>
              </div>
            </div>

            <div className="mt-6 p-4 rounded-lg" style={{ backgroundColor: 'var(--bg-primary)', borderColor: 'var(--border-color)' }}>
              <h3 className="font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                Smart Storage Management
              </h3>
              <p className="text-sm mb-3" style={{ color: 'var(--text-secondary)' }}>
                Chats are automatically summarized when they exceed 100MB to maintain performance. 
                {stats.chatsWithSummary > 0 && ` ${stats.chatsWithSummary} of your chats have been optimized.`}
              </p>
              <div className="flex gap-2">
                <div className="flex-1 p-2 rounded text-center text-xs" style={{ backgroundColor: 'var(--bg-hover)', color: 'var(--text-secondary)' }}>
                  IndexedDB Storage
                </div>
                <div className="flex-1 p-2 rounded text-center text-xs" style={{ backgroundColor: 'var(--bg-hover)', color: 'var(--text-secondary)' }}>
                  Auto Summarization
                </div>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={loadStats}
                className="flex-1 py-2 px-4 rounded-lg border transition-all duration-200"
                style={{ 
                  backgroundColor: 'var(--bg-primary)', 
                  borderColor: 'var(--border-color)',
                  color: 'var(--text-primary)'
                }}
              >
                Refresh
              </button>
              <button
                onClick={handleClearHistory}
                className="flex-1 py-2 px-4 rounded-lg border transition-all duration-200 hover:bg-red-500 hover:bg-opacity-20"
                style={{ 
                  backgroundColor: 'var(--bg-primary)', 
                  borderColor: '#ea4335',
                  color: '#ea4335'
                }}
              >
                Clear All
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
