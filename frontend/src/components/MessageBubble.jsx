import React from 'react';
import ReactMarkdown from 'react-markdown';
import RecipeCard from './RecipeCard';

export default function MessageBubble({ message, onStartCooking }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex w-full animate-fade-in ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex flex-col max-w-[85%] ${isUser ? 'items-end' : 'items-start'}`}>
        {message.content && (
          <div 
            className={`p-4 rounded-2xl shadow-sm ${
              isUser 
                ? 'bg-orange-600 text-white rounded-tr-sm' 
                : 'bg-neutral-800 text-neutral-100 rounded-tl-sm border border-neutral-700 prose prose-invert max-w-none'
            }`}
          >
            {isUser ? (
              <p className="whitespace-pre-wrap">{message.content}</p>
            ) : (
              <ReactMarkdown>{message.content}</ReactMarkdown>
            )}
          </div>
        )}
        
        {message.image && isUser && (
          <div className="mt-2 rounded-xl overflow-hidden border border-neutral-700 w-64 h-64">
            <img src={message.image} alt="Uploaded food" className="w-full h-full object-cover" />
          </div>
        )}

        {message.recipe && !isUser && (
          <div className="mt-4 w-full">
            <RecipeCard recipe={message.recipe} onStartCooking={onStartCooking} />
          </div>
        )}
        
        <span className="text-xs text-neutral-500 mt-1 px-1">
          {new Date(message.timestamp || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    </div>
  );
}
