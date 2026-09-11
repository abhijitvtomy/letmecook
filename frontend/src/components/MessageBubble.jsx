import React from 'react';
import ReactMarkdown from 'react-markdown';
import RecipeCard from './RecipeCard';

export default function MessageBubble({ message, onStartCooking }) {
  const isUser = message.role === 'user';
  const dishImage = !isUser && (message.imageUrl || message.recipe?.image_url);
  const dishName = message.recipe?.name || message.recipe?.title;

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

            {/* Dish Picture Displayed at the end of the chatbot response */}
            {dishImage && (
              <div className="mt-4 not-prose rounded-xl overflow-hidden border border-neutral-700/80 bg-neutral-900 shadow-md group transition-all duration-300 hover:border-orange-500/50">
                <div className="relative aspect-[16/9] w-full overflow-hidden">
                  <img 
                    src={dishImage} 
                    alt={dishName || "Finished dish presentation"} 
                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                    loading="lazy"
                    onError={(e) => { e.currentTarget.parentElement.parentElement.style.display = 'none'; }}
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent flex items-end p-3">
                    <span className="text-xs sm:text-sm font-semibold text-white flex items-center gap-1.5 drop-shadow-md">
                      <span className="text-orange-400">🍽️ Finished Dish:</span> {dishName || "Recipe Presentation"}
                    </span>
                  </div>
                </div>
              </div>
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
