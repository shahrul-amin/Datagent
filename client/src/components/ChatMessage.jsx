// Clean ChatMessage component
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import Plot from 'react-plotly.js';

export default function ChatMessage({ type, text, file, loading, error }) {
  
  const renderContent = () => {
    if (loading) {
      return (
        <span className="flex items-center gap-2">
          <div className="flex gap-1">
            <div className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: 'var(--accent-blue)' }}></div>
            <div className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: 'var(--accent-blue)', animationDelay: '0.2s' }}></div>
            <div className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: 'var(--accent-blue)', animationDelay: '0.4s' }}></div>
          </div>
          <span style={{ color: 'var(--text-secondary)' }}>Thinking...</span>
        </span>
      );
    }

    if (error) {
      return (
        <div className="p-3 rounded-lg" style={{ backgroundColor: 'rgba(234, 67, 53, 0.1)', border: '1px solid rgba(234, 67, 53, 0.3)' }}>
          <p style={{ color: '#ea4335' }}>{text}</p>
        </div>
      );
    }

    if (type === 'user') {
      return (
        <>
          {file?.preview && (
            <div className="mb-3">
              {file.preview.startsWith('data:image/') ? (
                <img 
                  src={file.preview} 
                  alt="Attachment" 
                  className="max-w-full h-auto rounded-lg shadow-lg"
                />
              ) : (
                <div className="flex items-center gap-3 p-3 rounded-lg" 
                     style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-color)' }}>
                  <span className="material-symbols-rounded" style={{ color: 'var(--accent-blue)' }}>description</span>
                  <span style={{ color: 'var(--text-primary)' }}>{file.name}</span>
                </div>
              )}
            </div>
          )}
          <p style={{ color: 'var(--text-primary)' }}>{text}</p>
        </>
      );    }

    // Bot response - render markdown for all bot messages
    if (type === 'bot') {
      // Check if it's a rich response
      if (text?.type === 'rich_response') {
        return (
          <div className="rich-response">
            {text.content.map((section, idx) => {
              if (section.type === 'text') {                return (
                  <div key={idx} className="markdown-content prose dark:prose-invert max-w-none">
                    <ReactMarkdown
                      components={{
                        code: ({node, inline, className, children, ...props}) => {
                          const match = /language-(\w+)/.exec(className || '');
                          return !inline && match ? (
                            <SyntaxHighlighter
                              language={match[1]}
                              style={vscDarkPlus}
                              PreTag="div"
                              className="rounded-lg"
                              {...props}
                            >
                              {String(children).replace(/\n$/, '')}
                            </SyntaxHighlighter>
                          ) : (
                            <code className="bg-gray-600 rounded px-1 py-0.5" style={{ color: 'var(--text-primary)' }} {...props}>
                              {children}
                            </code>
                          );
                        },
                        h1: ({children, ...props}) => (
                          <h1 className="text-2xl font-bold mb-4 mt-6" style={{ color: 'var(--text-primary)' }} {...props}>
                            {children}
                          </h1>
                        ),
                        h2: ({children, ...props}) => (
                          <h2 className="text-xl font-semibold mb-3 mt-5" style={{ color: 'var(--text-primary)' }} {...props}>
                            {children}
                          </h2>
                        ),
                        h3: ({children, ...props}) => (
                          <h3 className="text-lg font-medium mb-2 mt-4" style={{ color: 'var(--text-primary)' }} {...props}>
                            {children}
                          </h3>
                        ),
                        p: ({children, ...props}) => (
                          <p className="mb-3 leading-relaxed" style={{ color: 'var(--text-primary)' }} {...props}>
                            {children}
                          </p>
                        ),
                        ul: ({children, ...props}) => (
                          <ul className="mb-3 ml-4 space-y-1" {...props}>
                            {children}
                          </ul>
                        ),
                        ol: ({children, ...props}) => (
                          <ol className="mb-3 ml-4 space-y-1" {...props}>
                            {children}
                          </ol>
                        ),
                        li: ({children, ...props}) => (
                          <li className="leading-relaxed" style={{ color: 'var(--text-primary)' }} {...props}>
                            {children}
                          </li>
                        ),
                        strong: ({children, ...props}) => (
                          <strong className="font-semibold" style={{ color: 'var(--text-primary)' }} {...props}>
                            {children}
                          </strong>
                        ),
                        em: ({children, ...props}) => (
                          <em className="italic" style={{ color: 'var(--text-secondary)' }} {...props}>
                            {children}
                          </em>
                        ),
                        blockquote: ({children, ...props}) => (
                          <blockquote className="border-l-4 pl-4 italic my-3" 
                                     style={{ borderColor: 'var(--accent-blue)', color: 'var(--text-secondary)' }} 
                                     {...props}>
                            {children}
                          </blockquote>
                        )
                      }}
                    >
                      {section.data}
                    </ReactMarkdown>
                  </div>
                );
              }
              
              if (section.type === 'code') {
                return (
                  <div key={idx} className="code-section mb-4">
                    <SyntaxHighlighter 
                      language="python"
                      style={vscDarkPlus}
                      className="rounded-lg"
                    >
                      {section.data.code}
                    </SyntaxHighlighter>
                    {section.data.output && (
                      <pre className="p-3 rounded-lg mt-2 text-sm overflow-x-auto font-mono" 
                           style={{ backgroundColor: 'var(--bg-secondary)', color: 'var(--text-secondary)', border: '1px solid var(--border-color)' }}>
                        {section.data.output}
                      </pre>
                    )}
                    
                    {section.data.figures?.map((figure, fidx) => (
                      <div key={fidx} className="mt-4">
                        {figure.type === 'matplotlib' && (
                          <img 
                            src={`data:image/png;base64,${figure.data}`}
                            alt="Visualization"
                            className="max-w-full rounded-lg"
                          />
                        )}
                        {figure.type === 'plotly' && (
                          <Plot
                            data={figure.data.data}
                            layout={{
                              ...figure.data.layout,
                              width: undefined,
                              height: 400,
                              margin: { t: 30 }
                            }}
                            config={{ responsive: true }}
                            className="w-full"
                          />
                        )}
                      </div>
                    ))}
                  </div>
                );
              }
              
              return null;
            })}
          </div>
        );
      }

      // Plain text bot response - render as markdown
      return (
        <div className="markdown-content prose dark:prose-invert max-w-none">
          <ReactMarkdown
            components={{
              code: ({node, inline, className, children, ...props}) => {
                const match = /language-(\w+)/.exec(className || '');
                return !inline && match ? (
                  <SyntaxHighlighter
                    language={match[1]}
                    style={vscDarkPlus}
                    PreTag="div"
                    className="rounded-lg"
                    {...props}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                ) : (
                  <code className="bg-gray-600 rounded px-1 py-0.5" style={{ color: 'var(--text-primary)' }} {...props}>
                    {children}
                  </code>
                );
              },
              h1: ({children, ...props}) => (
                <h1 className="text-2xl font-bold mb-4 mt-6" style={{ color: 'var(--text-primary)' }} {...props}>
                  {children}
                </h1>
              ),
              h2: ({children, ...props}) => (
                <h2 className="text-xl font-semibold mb-3 mt-5" style={{ color: 'var(--text-primary)' }} {...props}>
                  {children}
                </h2>
              ),
              h3: ({children, ...props}) => (
                <h3 className="text-lg font-medium mb-2 mt-4" style={{ color: 'var(--text-primary)' }} {...props}>
                  {children}
                </h3>
              ),
              p: ({children, ...props}) => (
                <p className="mb-3 leading-relaxed" style={{ color: 'var(--text-primary)' }} {...props}>
                  {children}
                </p>
              ),
              ul: ({children, ...props}) => (
                <ul className="mb-3 ml-4 space-y-1" {...props}>
                  {children}
                </ul>
              ),
              ol: ({children, ...props}) => (
                <ol className="mb-3 ml-4 space-y-1" {...props}>
                  {children}
                </ol>
              ),
              li: ({children, ...props}) => (
                <li className="leading-relaxed" style={{ color: 'var(--text-primary)' }} {...props}>
                  {children}
                </li>
              ),
              strong: ({children, ...props}) => (
                <strong className="font-semibold" style={{ color: 'var(--text-primary)' }} {...props}>
                  {children}
                </strong>
              ),
              em: ({children, ...props}) => (
                <em className="italic" style={{ color: 'var(--text-secondary)' }} {...props}>
                  {children}
                </em>
              ),
              blockquote: ({children, ...props}) => (
                <blockquote className="border-l-4 pl-4 italic my-3" 
                           style={{ borderColor: 'var(--accent-blue)', color: 'var(--text-secondary)' }} 
                           {...props}>
                  {children}
                </blockquote>
              )
            }}
          >
            {text}
          </ReactMarkdown>
        </div>
      );
    }

    // Plain text response
    return <p>{text}</p>;
  };

  return (
    <div className={`flex gap-4 my-6 ${type === 'user' ? 'justify-end' : ''}`}>
      {type === 'bot' && (
        <div className="w-10 h-10 rounded-full p-1 flex-shrink-0" 
             style={{ backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--border-color)' }}>
          <img 
            src="./gemini_icon.png" 
            alt="Bot" 
            className={`w-full h-full rounded-full ${loading ? 'animate-spin' : ''}`} 
          />
        </div>
      )}
      
      <div className={`max-w-[75%] p-4 rounded-2xl shadow-lg transition-all duration-200 hover:shadow-xl ${
        type === 'user' ? 'rounded-br-md' : 'rounded-bl-md'
      }`} style={{
        backgroundColor: type === 'user' ? 'var(--accent-blue)' : 'var(--bg-secondary)',
        color: type === 'user' ? 'var(--bg-primary)' : 'var(--text-primary)',
        border: type === 'user' ? 'none' : '1px solid var(--border-color)'
      }}>
        {renderContent()}
      </div>
    </div>
  );
}