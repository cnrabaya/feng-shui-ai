// ─────────────────────────────────────────────
// useRoomAnalysis.js
// Manages the full analysis + layout generation flow.
// Now accepts photos array instead of single image.
// ─────────────────────────────────────────────
import { useState, useCallback } from 'react';
import { analyzeRoom, generateLayouts } from '../services/anthropicService';

export const ANALYSIS_STEPS = {
  IDLE:       'idle',
  ANALYZING:  'analyzing',
  GENERATING: 'generating',
  DONE:       'done',
  ERROR:      'error',
};

const initialState = {
  step:     ANALYSIS_STEPS.IDLE,
  analysis: null,
  layouts:  null,
  error:    null,
  progress: '',
};

export function useRoomAnalysis() {
  const [state, setState] = useState(initialState);
  const update = (patch) => setState(prev => ({ ...prev, ...patch }));

  // photos: [{ base64, mediaType, orientation }]
  const runAnalysis = useCallback(async ({ photos, width, height, unit }) => {
    update({ step: ANALYSIS_STEPS.ANALYZING, error: null, progress: 'Reading the room…', analysis: null, layouts: null });
    try {
      const analysis = await analyzeRoom({ photos, width, height, unit });
      update({ analysis, step: ANALYSIS_STEPS.GENERATING, progress: 'Generating layout alternatives…' });
      const { layouts } = await generateLayouts({ analysis, width, height, unit });
      update({ layouts, step: ANALYSIS_STEPS.DONE, progress: '' });
    } catch (err) {
      update({ step: ANALYSIS_STEPS.ERROR, error: err.message || 'Something went wrong.', progress: '' });
    }
  }, []);

  // Mock helper — simulates the two-stage loading with fake data
  const setMockData = (mockAnalysis, mockLayouts) => {
    update({ step: ANALYSIS_STEPS.ANALYZING, error: null, progress: 'Reading the room…', analysis: null, layouts: null });
    setTimeout(() => {
      update({ analysis: mockAnalysis, step: ANALYSIS_STEPS.GENERATING, progress: 'Generating layout alternatives…' });
      setTimeout(() => {
        update({ layouts: mockLayouts, step: ANALYSIS_STEPS.DONE, progress: '' });
      }, 1800);
    }, 2000);
  };

  const reset = useCallback(() => setState(initialState), []);

  return {
    ...state,
    runAnalysis,
    setMockData,
    reset,
    isLoading: state.step === ANALYSIS_STEPS.ANALYZING || state.step === ANALYSIS_STEPS.GENERATING,
    isIdle:    state.step === ANALYSIS_STEPS.IDLE,
    isDone:    state.step === ANALYSIS_STEPS.DONE,
    isError:   state.step === ANALYSIS_STEPS.ERROR,
  };
}
