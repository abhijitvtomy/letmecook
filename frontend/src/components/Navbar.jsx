import React from 'react';
import { ChefHat, Search, MessageSquare } from 'lucide-react';

export default function Navbar({ currentView, setView }) {
  return (
    <nav className="sticky top-0 z-50 flex items-center justify-between px-6 py-4 bg-neutral-900 border-b border-neutral-800 shadow-sm">
      <div 
        className="flex items-center gap-2 cursor-pointer"
        onClick={() => setView('chat')}
      >
        <span className="text-2xl">🍳</span>
        <span className="text-xl font-bold font-serif tracking-tight text-white">LetMeCook</span>
      </div>
      
      <div className="flex items-center gap-4">
        <button 
          onClick={() => setView('chat')}
          className={`flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${
            currentView === 'chat' 
              ? 'bg-neutral-800 text-orange-500' 
              : 'text-neutral-400 hover:bg-neutral-800 hover:text-neutral-200'
          }`}
        >
          <MessageSquare size={18} />
          <span className="font-medium">Chat</span>
        </button>
        <button 
          onClick={() => setView('browse')}
          className={`flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${
            currentView === 'browse' 
              ? 'bg-neutral-800 text-orange-500' 
              : 'text-neutral-400 hover:bg-neutral-800 hover:text-neutral-200'
          }`}
        >
          <Search size={18} />
          <span className="font-medium">Browse</span>
        </button>
      </div>
    </nav>
  );
}
