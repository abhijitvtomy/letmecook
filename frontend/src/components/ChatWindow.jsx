import React, { useRef, useEffect, useState } from 'react';
import { Send, Image as ImageIcon, Loader2 } from 'lucide-react';
import useChat from '../hooks/useChat';
import MessageBubble from './MessageBubble';
import ImageUpload from './ImageUpload';

export default function ChatWindow({ onStartCooking }) {
  const { messages, isLoading, sendMessage, sendImage } = useChat();
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    sendMessage(input);
    setInput('');
  };

  const handleImageSelect = (base64) => {
    sendImage(base64);
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto w-full relative">
      <div className="flex-1 overflow-y-auto p-4 space-y-6 pb-32">
        {messages.length === 0 && (
          <div className="text-center mt-20 animate-fade-in">
            <span className="text-6xl block mb-6">🍳</span>
            <h2 className="text-2xl font-serif text-white mb-2">Hey! I'm LetMeCook</h2>
            <p className="text-neutral-400 max-w-md mx-auto">
              Tell me a dish name, upload a food photo, or ask me anything about cooking!
            </p>
          </div>
        )}
        
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} onStartCooking={onStartCooking} />
        ))}
        
        {isLoading && (
          <div className="flex items-center gap-2 text-neutral-400 animate-pulse w-fit bg-neutral-800 p-4 rounded-2xl rounded-tl-sm">
            <Loader2 className="animate-spin" size={20} />
            <span>Cooking up a response...</span>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-neutral-900 via-neutral-900 to-transparent p-4 pt-10">
        <form onSubmit={handleSubmit} className="flex items-end gap-2 bg-neutral-800 p-2 rounded-xl shadow-lg border border-neutral-700">
          <ImageUpload onImageSelect={handleImageSelect} disabled={isLoading} />
          
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            placeholder="What would you like to cook?"
            className="flex-1 bg-transparent text-white resize-none max-h-32 min-h-12 p-2 focus:outline-none scrollbar-thin"
            rows={1}
            disabled={isLoading}
          />
          
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="p-3 bg-orange-500 hover:bg-orange-600 disabled:bg-neutral-700 disabled:text-neutral-500 text-white rounded-lg transition-colors flex-shrink-0"
          >
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  );
}
