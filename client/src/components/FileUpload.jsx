// File upload component
import { useState } from 'react';

export default function FileUpload({ fileState, onFileChange, onCancelFile, inputRef }) {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    onFileChange(file);
  };

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!e.currentTarget.contains(e.relatedTarget)) {
      setIsDragOver(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      onFileChange(files[0]);
    }
  };

  const getFileIcon = (type) => {
    if (type.startsWith('image/')) return 'image';
    if (type.includes('pdf')) return 'picture_as_pdf';
    if (type.includes('csv') || type.includes('excel') || type.includes('sheet')) return 'table_chart';
    if (type.includes('text')) return 'description';
    return 'insert_drive_file';
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusColor = () => {
    switch (fileState.status) {
      case 'ready': return '#22c55e';
      case 'uploading': return 'var(--accent-blue)';
      case 'error': return '#ef4444';
      default: return 'var(--border-color)';
    }
  };

  const getStatusIcon = () => {
    switch (fileState.status) {
      case 'ready': return 'check_circle';
      case 'uploading': return null; // Will show spinner
      case 'error': return 'error';
      default: return null;
    }
  };

  const getStatusText = () => {
    switch (fileState.status) {
      case 'ready': return 'Ready';
      case 'uploading': return 'Processing...';
      case 'error': return fileState.error || 'Error';
      default: return '';
    }
  };

  return (
    <div className="relative">
      <input
        type="file"
        ref={inputRef}
        onChange={handleFileChange}
        accept="image/*,.pdf,.txt,.csv,.xlsx,.xls"
        className="hidden"
      />
      
      {fileState.hasFile() ? (
        <div className="flex items-center gap-2 max-w-xs">
          {/* File Card */}
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg border transition-all duration-200" 
               style={{ 
                 backgroundColor: fileState.status === 'ready' ? 'rgba(34, 197, 94, 0.1)' : 
                                 fileState.status === 'error' ? 'rgba(239, 68, 68, 0.1)' : 'var(--bg-secondary)',
                 borderColor: getStatusColor()
               }}>
            
            {/* File Icon */}
            <div className="flex-shrink-0">
              {fileState.preview && fileState.preview.startsWith('data:image/') ? (
                <img
                  src={fileState.preview}
                  alt="Preview"
                  className="w-8 h-8 rounded object-cover"
                />
              ) : (
                <div className="w-8 h-8 flex items-center justify-center rounded" 
                     style={{ backgroundColor: 'var(--accent-blue)', color: 'white' }}>
                  <span className="material-symbols-rounded text-sm">
                    {getFileIcon(fileState.type)}
                  </span>
                </div>
              )}
            </div>

            {/* File Info */}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate" style={{ color: 'var(--text-primary)' }}>
                {fileState.name}
              </p>
              <div className="flex items-center gap-2">
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                  {formatFileSize(fileState.size)}
                </p>
                {fileState.status !== 'idle' && (
                  <div className="flex items-center gap-1">
                    {fileState.isUploading() ? (
                      <div className="animate-spin w-3 h-3 border border-current border-t-transparent rounded-full" 
                           style={{ color: 'var(--accent-blue)' }}></div>
                    ) : (
                      <span className="material-symbols-rounded text-xs" style={{ color: getStatusColor() }}>
                        {getStatusIcon()}
                      </span>
                    )}
                    <span className="text-xs" style={{ color: getStatusColor() }}>
                      {getStatusText()}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Remove Button */}
            <button
              type="button"
              onClick={onCancelFile}
              className="flex-shrink-0 p-1 rounded-full transition-all duration-200 hover:scale-110"
              style={{ color: 'var(--text-muted)' }}
            >
              <span className="material-symbols-rounded text-sm">close</span>
            </button>
          </div>
        </div>      ) : (
        <div
          className={`relative transition-all duration-200 ${isDragOver ? 'scale-105' : ''}`}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <button
            type="button"
            onClick={() => inputRef.current.click()}
            className={`w-14 h-14 rounded-full flex items-center justify-center transition-all duration-200 hover:scale-105 border ${
              isDragOver ? 'scale-110' : ''
            }`}
            style={{ 
              backgroundColor: isDragOver ? 'rgba(var(--accent-blue-rgb), 0.1)' : 'var(--bg-input)',
              borderColor: isDragOver ? 'var(--accent-blue)' : 'var(--border-color)',
              color: isDragOver ? 'var(--accent-blue)' : 'var(--text-secondary)'
            }}
            title="Attach file (drag & drop or click)"
          >
            <span className="material-symbols-rounded text-lg">
              {isDragOver ? 'upload' : 'attach_file'}
            </span>
          </button>
        </div>
      )}
    </div>
  );
}