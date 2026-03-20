import { Bot, User, ChevronDown, ChevronUp, FileText } from 'lucide-react';
import { useState } from 'react';

interface Source {
  pdf: string;
  page: number;
  paragraph: number;
}

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  sources?: Source[];
}

export function ChatMessage({ role, content, timestamp, sources }: ChatMessageProps) {
  const isUser = role === 'user';
  const [showSources, setShowSources] = useState(false);

  return (
    <div className={`flex gap-4 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        isUser ? 'bg-gray-900' : 'bg-blue-600'
      }`}>
        {isUser ? (
          <User size={16} className="text-white" />
        ) : (
          <Bot size={16} className="text-white" />
        )}
      </div>
      
      <div className={`flex flex-col gap-2 max-w-[70%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div className={`px-4 py-3 rounded-2xl ${
          isUser 
            ? 'bg-gray-900 text-white' 
            : 'bg-gray-100 text-gray-900'
        }`}>
          <p className="whitespace-pre-wrap break-words">{content}</p>
        </div>

        {sources && sources.length > 0 && (
          <div className="w-full mt-1">
            <button 
              onClick={() => setShowSources(!showSources)}
              className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700 transition-colors"
            >
              <FileText size={12} />
              {showSources ? 'Hide Citations' : 'View Citations'}
              {showSources ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
            </button>
            
            {showSources && (
              <div className="mt-2 space-y-2">
                {sources.map((source, idx) => (
                  <div key={idx} className="bg-white border border-gray-200 rounded-lg p-3 text-sm">
                    <p className="font-medium text-gray-900 text-xs mb-1">
                      {source.pdf} (Page {source.page})
                    </p>
                    <p className="text-gray-600 text-xs">
                      Paragraph {source.paragraph}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {timestamp && (
          <span className="text-gray-400 px-2 text-xs">{timestamp}</span>
        )}
      </div>
    </div>
  );
}
