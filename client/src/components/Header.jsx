// Welcome header with suggestion cards
export default function Header({ onSuggestionClick }) {
  const suggestions = [
    { text: "📊 Analyze my data", icon: "analytics" },
    { text: "📈 Create visualizations", icon: "trending_up" }, 
    { text: "🤖 Give insight", icon: "smart_toy" }
  ];

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] px-4">
      <div className="text-center mb-12">
        <h1 className="text-6xl font-bold mb-4" style={{ 
          background: 'linear-gradient(45deg, var(--accent-gradient-start), var(--accent-gradient-end))',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
          fontFamily: 'Google Sans, -apple-system, BlinkMacSystemFont, sans-serif'
        }}>
          Hello, Researcher
        </h1>
        <h4 className="text-2xl font-normal" style={{ color: 'var(--text-secondary)' }}>
          What can I help you analyze today?
        </h4>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl w-full">
        {suggestions.map((suggestion, index) => (
          <div 
            key={index}
            className="group relative overflow-hidden rounded-2xl p-6 cursor-pointer transition-all duration-300 hover:scale-105 hover:shadow-2xl border" 
            style={{ 
              backgroundColor: 'var(--bg-secondary)', 
              borderColor: 'var(--border-color)',
              boxShadow: '0 4px 20px var(--shadow-light)'
            }}
            onClick={() => onSuggestionClick && onSuggestionClick(suggestion.text)}
          >
            <div className="absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity duration-300"
                 style={{ 
                   background: 'linear-gradient(45deg, var(--accent-gradient-start), var(--accent-gradient-end))'
                 }}>
            </div>
            
            <div className="relative z-10 flex flex-col items-center text-center">
              <div className="mb-4 p-3 rounded-full transition-all duration-300 group-hover:scale-110"
                   style={{ backgroundColor: 'var(--bg-hover)' }}>
                <span className="material-symbols-rounded text-2xl" style={{ color: 'var(--accent-blue)' }}>
                                      {suggestion.icon}
                </span>
              </div>
              
              <h3 className="text-lg font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                {suggestion.text}
              </h3>
              
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                {index === 0 && "Upload and analyze your datasets with powerful AI insights"}
                {index === 1 && "Generate beautiful charts and graphs from your data"}
                {index === 2 && "Provide in depth insights and analytics"}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}