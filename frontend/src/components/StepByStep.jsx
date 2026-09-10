import React from 'react';
import { X, ChevronLeft, ChevronRight, Clock, Flame, AlertCircle } from 'lucide-react';
import useRecipe from '../hooks/useRecipe';

export default function StepByStep({ recipe, onClose }) {
  const { currentStep, nextStep, prevStep, totalSteps, step } = useRecipe(recipe);

  if (!step) return null;

  const progress = ((currentStep + 1) / totalSteps) * 100;

  return (
    <div className="absolute inset-0 bg-neutral-900 z-50 flex flex-col animate-fade-in">
      <div className="flex items-center justify-between p-4 border-b border-neutral-800 bg-neutral-900">
        <h2 className="font-serif text-xl font-bold text-white truncate pr-4">{recipe.title}</h2>
        <button 
          onClick={onClose}
          className="p-2 text-neutral-400 hover:text-white hover:bg-neutral-800 rounded-full transition-colors"
        >
          <X size={24} />
        </button>
      </div>

      <div className="h-1 bg-neutral-800">
        <div 
          className="h-full bg-orange-500 transition-all duration-300 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="flex-1 overflow-y-auto p-8 flex flex-col items-center justify-center">
        <div className="w-full max-w-3xl">
          <div className="mb-8 text-center">
            <span className="text-orange-500 font-bold uppercase tracking-widest text-sm mb-2 block">
              Step {currentStep + 1} of {totalSteps}
            </span>
            {step.phase && (
              <span className="inline-block bg-neutral-800 text-neutral-300 px-3 py-1 rounded-full text-sm">
                {step.phase}
              </span>
            )}
          </div>

          <p className="text-3xl md:text-5xl font-serif text-white leading-tight text-center mb-12">
            {step.instruction}
          </p>

          <div className="flex flex-wrap justify-center gap-4 mb-12">
            {step.duration && (
              <div className="flex items-center gap-2 bg-neutral-800 px-4 py-3 rounded-xl border border-neutral-700 text-neutral-200">
                <Clock className="text-orange-400" />
                <span className="text-lg font-medium">{step.duration}</span>
              </div>
            )}
            {step.temperature && (
              <div className="flex items-center gap-2 bg-neutral-800 px-4 py-3 rounded-xl border border-neutral-700 text-neutral-200">
                <Flame className="text-red-400" />
                <span className="text-lg font-medium">{step.temperature}</span>
              </div>
            )}
            {step.visual_cue && (
              <div className="flex items-center gap-2 bg-neutral-800 px-4 py-3 rounded-xl border border-neutral-700 text-neutral-200">
                <AlertCircle className="text-yellow-400" />
                <span className="text-lg font-medium italic">{step.visual_cue}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="border-t border-neutral-800 bg-neutral-900 p-6 flex justify-between items-center">
        <button
          onClick={prevStep}
          disabled={currentStep === 0}
          className="flex items-center gap-2 px-6 py-3 rounded-xl bg-neutral-800 text-white font-bold disabled:opacity-50 disabled:cursor-not-allowed hover:bg-neutral-700 transition-colors"
        >
          <ChevronLeft size={20} />
          Previous
        </button>
        
        <button
          onClick={nextStep}
          disabled={currentStep === totalSteps - 1}
          className="flex items-center gap-2 px-8 py-3 rounded-xl bg-orange-600 text-white font-bold disabled:opacity-50 disabled:cursor-not-allowed hover:bg-orange-500 transition-colors shadow-lg shadow-orange-900/20"
        >
          Next
          <ChevronRight size={20} />
        </button>
      </div>
    </div>
  );
}
