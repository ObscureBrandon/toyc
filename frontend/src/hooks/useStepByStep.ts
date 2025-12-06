import { useState, useEffect, useCallback, useRef } from 'react';
import { TraceStep } from '@/lib/api';

export interface PlaybackControls {
  isPlaying: boolean;
  currentStep: number;
  totalSteps: number;
  speed: number; // steps per second
  canGoNext: boolean;
  canGoPrevious: boolean;
}

export interface StepByStepState {
  controls: PlaybackControls;
  currentStepData: TraceStep | null;
  visibleSteps: TraceStep[];
  play: () => void;
  pause: () => void;
  nextStep: () => void;
  previousStep: () => void;
  goToStep: (stepIndex: number) => void;
  setSpeed: (speed: number) => void;
  reset: () => void;
}

export function useStepByStep(steps: TraceStep[]): StepByStepState {
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState(1); // 1 step per second
  const intervalRef = useRef<number | null>(null);

  const totalSteps = steps.length;
  const canGoNext = currentStep < totalSteps - 1;
  const canGoPrevious = currentStep > 0;
  const currentStepData = steps[currentStep] || null;
  
  // Get all steps up to current step (for cumulative visualization)
  const visibleSteps = steps.slice(0, currentStep + 1);

  const clearInterval = useCallback(() => {
    if (intervalRef.current) {
      window.clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const nextStep = useCallback(() => {
    setCurrentStep(prev => Math.min(prev + 1, totalSteps - 1));
  }, [totalSteps]);

  const previousStep = useCallback(() => {
    setCurrentStep(prev => Math.max(prev - 1, 0));
  }, []);

  const goToStep = useCallback((stepIndex: number) => {
    setCurrentStep(Math.max(0, Math.min(stepIndex, totalSteps - 1)));
  }, [totalSteps]);

  const play = useCallback(() => {
    if (currentStep >= totalSteps - 1) {
      setCurrentStep(0);
    }
    setIsPlaying(true);
  }, [currentStep, totalSteps]);

  const pause = useCallback(() => {
    setIsPlaying(false);
  }, []);

  const reset = useCallback(() => {
    setIsPlaying(false);
    setCurrentStep(0);
    clearInterval();
  }, [clearInterval]);

  const updateSpeed = useCallback((newSpeed: number) => {
    setSpeed(Math.max(0.1, Math.min(5, newSpeed))); // Clamp between 0.1 and 5
  }, []);

  // Handle automatic playback
  useEffect(() => {
    // Recalculate canGoNext inside effect to avoid stale closure
    const canProgress = currentStep < totalSteps - 1;
    
    if (isPlaying && canProgress) {
      intervalRef.current = window.setInterval(() => {
        setCurrentStep(prev => {
          const next = prev + 1;
          if (next >= totalSteps) {
            setIsPlaying(false);
            return prev;
          }
          return next;
        });
      }, 1000 / speed);
    } else {
      clearInterval();
      if (!canProgress && isPlaying) {
        setIsPlaying(false);
      }
    }

    return clearInterval;
  }, [isPlaying, currentStep, speed, totalSteps, clearInterval]);

  // Cleanup on unmount
  useEffect(() => {
    return clearInterval;
  }, [clearInterval]);

  // Reset when steps change (new trace data loaded)
  useEffect(() => {
    setIsPlaying(false);
    setCurrentStep(0);
    if (intervalRef.current) {
      window.clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, [steps]);

  const controls: PlaybackControls = {
    isPlaying,
    currentStep,
    totalSteps,
    speed,
    canGoNext,
    canGoPrevious,
  };

  return {
    controls,
    currentStepData,
    visibleSteps,
    play,
    pause,
    nextStep,
    previousStep,
    goToStep,
    setSpeed: updateSpeed,
    reset,
  };
}