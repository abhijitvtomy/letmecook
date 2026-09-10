import React, { useState } from 'react';
import Navbar from './components/Navbar';
import ChatWindow from './components/ChatWindow';
import StepByStep from './components/StepByStep';
import SearchBar from './components/SearchBar';

function App() {
  const [view, setView] = useState('chat'); // 'chat', 'browse', 'cook-with-me'
  const [activeRecipe, setActiveRecipe] = useState(null);

  const startCooking = (recipe) => {
    setActiveRecipe(recipe);
    setView('cook-with-me');
  };

  const stopCooking = () => {
    setActiveRecipe(null);
    setView('chat');
  };

  return (
    <div className="flex flex-col h-screen bg-neutral-900 text-neutral-100 font-sans">
      <Navbar currentView={view} setView={setView} />
      
      <main className="flex-1 overflow-hidden relative flex flex-col">
        {view === 'chat' && (
          <ChatWindow onStartCooking={startCooking} />
        )}
        
        {view === 'browse' && (
          <div className="p-4 max-w-4xl mx-auto w-full h-full flex flex-col">
            <h1 className="text-3xl font-serif mb-6 text-orange-500">Browse Recipes</h1>
            <SearchBar onSelectRecipe={(recipe) => {
              setActiveRecipe(recipe);
              setView('cook-with-me');
            }} />
            <div className="flex-1 mt-8 text-center text-neutral-400">
              <p>Search for your favorite recipes above!</p>
            </div>
          </div>
        )}

        {view === 'cook-with-me' && activeRecipe && (
          <StepByStep recipe={activeRecipe} onClose={stopCooking} />
        )}
      </main>
    </div>
  );
}

export default App;
