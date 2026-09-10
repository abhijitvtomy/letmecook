import React, { useState, useEffect } from 'react';
import { Search, Loader2 } from 'lucide-react';
import API_BASE from '../config';

export default function SearchBar({ onSelectRecipe }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    const timer = setTimeout(async () => {
      if (query.trim().length < 2) {
        setResults([]);
        return;
      }

      setIsSearching(true);
      try {
        const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
        if (response.ok) {
          const data = await response.json();
          setResults(Array.isArray(data) ? data : (data.recipes || []));
        }
      } catch (err) {
        console.error("Search error:", err);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  return (
    <div className="relative w-full max-w-2xl">
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-400" size={20} />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for recipes, ingredients, cuisines..."
          className="w-full bg-neutral-800 border border-neutral-700 rounded-2xl py-4 pl-12 pr-12 text-white placeholder-neutral-500 focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500"
        />
        {isSearching && (
          <Loader2 className="absolute right-4 top-1/2 -translate-y-1/2 text-orange-500 animate-spin" size={20} />
        )}
      </div>

      {results.length > 0 && query.trim().length >= 2 && (
        <div className="absolute top-full mt-2 w-full bg-neutral-800 border border-neutral-700 rounded-xl shadow-xl z-10 max-h-96 overflow-y-auto">
          {results.map((recipe) => (
            <div
              key={recipe.id || recipe.name || recipe.title}
              onClick={() => onSelectRecipe(recipe)}
              className="p-4 border-b border-neutral-700 last:border-0 hover:bg-neutral-700 cursor-pointer transition-colors"
            >
              <h4 className="font-bold text-white">{recipe.name || recipe.title}</h4>
              <p className="text-sm text-neutral-400 mt-1 flex gap-3">
                {recipe.cuisine && <span>{recipe.cuisine}</span>}
                {recipe.total_time_minutes && <span>• {recipe.total_time_minutes} mins</span>}
                {recipe.difficulty && <span>• {recipe.difficulty}</span>}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
