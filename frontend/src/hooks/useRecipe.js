import { useState, useEffect } from 'react';

export default function useRecipe(initialRecipe) {
  const [currentRecipe, setCurrentRecipe] = useState(initialRecipe);
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    setCurrentRecipe(initialRecipe);
    setCurrentStep(0);
  }, [initialRecipe]);

  const nextStep = () => {
    if (currentRecipe && currentRecipe.steps && currentStep < currentRecipe.steps.length - 1) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const setRecipe = (recipe) => {
    setCurrentRecipe(recipe);
    setCurrentStep(0);
  };

  const step = currentRecipe?.steps?.[currentStep] || null;
  const totalSteps = currentRecipe?.steps?.length || 0;

  return {
    currentRecipe,
    currentStep,
    step,
    totalSteps,
    nextStep,
    prevStep,
    setRecipe
  };
}
