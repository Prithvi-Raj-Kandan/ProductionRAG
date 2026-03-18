import { useState } from 'react';
import { FileUpload } from './components/FileUpload';
import { ChatMessage } from './components/ChatMessage';
import { ChatInput } from './components/ChatInput';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! Upload your documents and I\'ll help you query them. What would you like to know?',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsProcessing(true);

    // Simulate API call - replace this with your backend integration
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'This is a placeholder response. Connect your RAG backend to get real answers based on your uploaded documents.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      setIsProcessing(false);
    }, 1000);

    // TODO: Replace the above with your actual backend call
    // Example:
    // try {
    //   const response = await fetch('YOUR_BACKEND_URL/query', {
    //     method: 'POST',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify({ query: content })
    //   });
    //   const data = await response.json();
    //   const assistantMessage: Message = {
    //     id: (Date.now() + 1).toString(),
    //     role: 'assistant',
    //     content: data.answer,
    //     timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    //   };
    //   setMessages(prev => [...prev, assistantMessage]);
    // } catch (error) {
    //   console.error('Error:', error);
    // } finally {
    //   setIsProcessing(false);
    // }
  };

  return (
    <div className="size-full flex bg-gray-50">
      {/* Left Sidebar - File Upload */}
      <div className="w-96 flex-shrink-0">
        <FileUpload />
      </div>

      {/* Right Main Area - Chat */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="p-6 bg-white border-b border-gray-200">
          <h1 className="text-gray-900">RAG Chatbot</h1>
          <p className="text-gray-500 mt-1">Ask questions about your documents</p>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.map(message => (
            <ChatMessage
              key={message.id}
              role={message.role}
              content={message.content}
              timestamp={message.timestamp}
            />
          ))}
          
          {isProcessing && (
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-blue-600">
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              </div>
              <div className="px-4 py-3 bg-gray-100 rounded-2xl">
                <p className="text-gray-500">Thinking...</p>
              </div>
            </div>
          )}
        </div>

        {/* Chat Input */}
        <ChatInput onSendMessage={handleSendMessage} disabled={isProcessing} />
      </div>
    </div>
  );
}
