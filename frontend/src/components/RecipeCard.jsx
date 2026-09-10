import React, { useState } from 'react';
import { Clock, Users, Flame, ChefHat, Play, ChevronDown, ChevronUp, AlertTriangle } from 'lucide-react';

export default function RecipeCard({ recipe, onStartCooking }) {
  const [ingredientsExpanded, setIngredientsExpanded] = useState(false);
  const [checkedIngredients, setCheckedIngredients] = useState({});

  const toggleIngredient = (idx) => {
    setCheckedIngredients(prev => ({ ...prev, [idx]: !prev[idx] }));
  };

  return (
    <div className="bg-neutral-800 border border-neutral-700 rounded-2xl overflow-hidden shadow-lg w-full max-w-2xl text-left">
      <div className="p-6 border-b border-neutral-700">
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-2xl font-serif font-bold text-white">{recipe.title}</h3>
          {recipe.cuisine && (
            <span className="bg-orange-500/20 text-orange-400 text-xs px-2 py-1 rounded-full font-medium">
              {recipe.cuisine}
            </span>
          )}
        </div>
        
        <div className="flex flex-wrap gap-4 text-sm text-neutral-400 mt-4">
          <div className="flex items-center gap-1"><Clock size={16} /> Prep: {recipe.prep_time || '?'}</div>
          <div className="flex items-center gap-1"><Flame size={16} /> Cook: {recipe.cook_time || '?'}</div>
          <div className="flex items-center gap-1 text-orange-400"><Clock size={16} /> Total: {recipe.total_time || '?'}</div>
          <div className="flex items-center gap-1"><Users size={16} /> Serves: {recipe.servings || '?'}</div>
          <div className="flex items-center gap-1"><ChefHat size={16} /> {recipe.difficulty || 'Medium'}</div>
        </div>
      </div>

      <div className="p-6 border-b border-neutral-700">
        <button 
          onClick={() => setIngredientsExpanded(!ingredientsExpanded)}
          className="flex items-center justify-between w-full text-lg font-bold text-neutral-200 hover:text-white"
        >
          <span>Ingredients ({recipe.ingredients?.length || 0})</span>
          {ingredientsExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </button>
        
        {ingredientsExpanded && (
          <ul className="mt-4 space-y-2">
            {recipe.ingredients?.map((ing, idx) => (
              <li key={idx} className="flex items-start gap-3 text-neutral-300">
                <input 
                  type="checkbox" 
                  checked={checkedIngredients[idx] || false}
                  onChange={() => toggleIngredient(idx)}
                  className="mt-1 w-4 h-4 rounded border-neutral-600 text-orange-500 focus:ring-orange-500 bg-neutral-700 cursor-pointer"
                />
                <span className={checkedIngredients[idx] ? 'line-through text-neutral-500' : ''}>
                  <strong>{ing.amount} {ing.unit}</strong> {ing.item} {ing.notes ? `(${ing.notes})` : ''}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="p-6">
        <h4 className="text-lg font-bold text-neutral-200 mb-4">Steps</h4>
        <div className="space-y-6">
          {recipe.steps?.map((step, idx) => (
            <div key={idx} className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-neutral-700 text-orange-400 flex items-center justify-center font-bold">
                {step.step_number || idx + 1}
              </div>
              <div className="flex-1 pt-1">
                {step.phase && (
                  <span className="text-xs uppercase tracking-wider text-neutral-500 font-bold mb-1 block">
                    {step.phase}
                  </span>
                )}
                <p className="text-neutral-200">{step.instruction}</p>
                
                {(step.duration || step.temperature || step.visual_cue) && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {step.duration && (
                      <span className="inline-flex items-center gap-1 text-xs bg-neutral-700 px-2 py-1 rounded text-neutral-300">
                        <Clock size={12} /> {step.duration}
                      </span>
                    )}
                    {step.temperature && (
                      <span className="inline-flex items-center gap-1 text-xs bg-red-900/30 text-red-400 px-2 py-1 rounded">
                        <Flame size={12} /> {step.temperature}
                      </span>
                    )}
                    {step.visual_cue && (
                      <span className="inline-flex items-center gap-1 text-xs italic text-orange-300">
                        "{step.visual_cue}"
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {recipe.safety_notes && recipe.safety_notes.length > 0 && (
        <div className="px-6 pb-6">
          <div className="bg-yellow-900/20 border border-yellow-700/50 rounded-lg p-4 flex gap-3">
            <AlertTriangle className="text-yellow-500 flex-shrink-0" size={20} />
            <div>
              <h5 className="text-yellow-500 font-bold text-sm mb-1">Safety Notes</h5>
              <ul className="text-sm text-yellow-200/70 list-disc list-inside">
                {recipe.safety_notes.map((note, i) => <li key={i}>{note}</li>)}
              </ul>
            </div>
          </div>
        </div>
      )}

      <div className="p-6 pt-0">
        <button 
          onClick={() => onStartCooking(recipe)}
          className="w-full py-3 bg-orange-600 hover:bg-orange-500 text-white rounded-xl font-bold flex items-center justify-center gap-2 transition-colors shadow-md"
        >
          <Play fill="currentColor" size={18} />
          Cook With Me
        </button>
      </div>
    </div>
  );
}
