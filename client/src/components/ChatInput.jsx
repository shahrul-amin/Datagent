// Clean ChatInput component
import { useState, useRef, useEffect } from 'react';
import FileUpload from './FileUpload';

export default function ChatInput({
  onSubmit,
  isProcessing,
  onStop,
  fileState,
  onFileChange,
  onClearFile,
  suggestedPrompt,
  onPromptChange
}) {
  const [input, setInput] = useState('');
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (suggestedPrompt) {
      setInput(suggestedPrompt);
      onPromptChange && onPromptChange('');
    }
  }, [suggestedPrompt, onPromptChange]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isProcessing) return;
    
    onSubmit(input, fileState);
    setInput('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (input.trim()) {
        handleSubmit(e);
      }
    }
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 py-4 backdrop-blur-md border-t" 
         style={{ 
           backgroundColor: 'rgba(19, 19, 20, 0.95)', 
           borderColor: 'var(--border-color)',
           boxShadow: '0 -4px 20px var(--shadow-light)'
         }}>
      <div className="container mx-auto max-w-4xl px-4">        
        {/* File Upload Area - Show above input when file is attached */}
        {fileState.hasFile() && (
          <div className="mb-3 flex justify-start">
            <FileUpload
              fileState={fileState}
              onFileChange={onFileChange}
              onCancelFile={onClearFile}
              inputRef={fileInputRef}
            />
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex items-end gap-3">
          {/* File Upload Button - Only show when no file is attached */}
          {!fileState.hasFile() && (
            <div className="flex-shrink-0">
              <FileUpload
                fileState={fileState}
                onFileChange={onFileChange}
                onCancelFile={onClearFile}
                inputRef={fileInputRef}
              />
            </div>
          )}

          <div className="flex-1 relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={fileState.hasFile() ? "Ask about your file..." : "Ask Datagent anything..."}
              rows="1"
              className="w-full px-6 py-4 rounded-3xl border transition-all duration-200 focus:outline-none resize-none overflow-y-auto"
              style={{
                backgroundColor: 'var(--bg-input)',
                borderColor: 'var(--border-color)',
                color: 'var(--text-primary)',
                fontSize: '16px',
                minHeight: '56px',
                maxHeight: '84px',
                paddingRight: '54px'
              }}
            />

            <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
              {isProcessing ? (
                <button
                  type="button"
                  onClick={onStop}
                  className="w-10 h-10 rounded-full flex items-center justify-center transition-all duration-200 hover:scale-110 shadow-lg"
                  style={{ backgroundColor: '#ea4335', color: 'white' }}
                >
                  <span className="material-symbols-rounded text-lg">stop</span>
                </button>
              ) : (
                input.trim() && (
                  <button
                    type="submit"
                    className="w-10 h-10 rounded-full flex items-center justify-center transition-all duration-200 hover:scale-110 shadow-lg"
                    style={{ backgroundColor: 'var(--accent-blue)', color: 'var(--bg-primary)' }}
                  >
                    <span className="material-symbols-rounded text-lg">arrow_upward</span>
                  </button>
                )
              )}
            </div>
          </div>
        </form>
        
        <p className="text-center mt-3 text-sm" style={{ color: 'var(--text-muted)' }}>
          Datagent can make mistakes, so double-check its responses. {fileState.hasFile() && 'File attached and ready to analyze.'}
        </p>
      </div>
    </div>
  );
}
