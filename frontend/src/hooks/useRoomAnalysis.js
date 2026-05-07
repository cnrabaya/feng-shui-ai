// ─────────────────────────────────────────────
// useRoomAnalysis.js
// Manages the full analysis + layout generation flow.
// Keeps all async state in one place.
// ─────────────────────────────────────────────

import { useState, useCallback } from 'react';
import { analyzeRoom, generateLayouts } from '../services/anthropicService';

export const ANALYSIS_STEPS = {
  IDLE:             'idle',
  ANALYZING:        'analyzing',
  GENERATING:       'generating',
  DONE:             'done',
  ERROR:            'error',
};

const initialState = {
  step:      ANALYSIS_STEPS.IDLE,
  analysis:  null,   // { description, fengShuiScore, existingFurniture, issues, recommendations }
  layouts:   null,   // [{ id, name, furniture, rationale, ... }]
  error:     null,
  progress:  '',     // Human-readable status message
};

export function useRoomAnalysis() {
  const [state, setState] = useState(initialState);

  const update = (patch) => setState(prev => ({ ...prev, ...patch }));

  /**
   * Run the full pipeline:
   *   1. analyzeRoom  → gets description + feng shui score
   *   2. generateLayouts → gets 3 layout alternatives
   */
  const runAnalysis = useCallback(async ({ imageBase64, imageMediaType, width, height, unit, orientation }) => {
    update({ step: ANALYSIS_STEPS.ANALYZING, error: null, progress: 'Reading the room…', analysis: null, layouts: null });

    try {
      const analysis = await analyzeRoom({ imageBase64, imageMediaType, width, height, unit, orientation });
      update({ analysis, step: ANALYSIS_STEPS.GENERATING, progress: 'Generating layout alternatives…' });

      const { layouts } = await generateLayouts({ analysis, width, height, unit, orientation });
      update({ layouts, step: ANALYSIS_STEPS.DONE, progress: '' });
    } catch (err) {
      update({ step: ANALYSIS_STEPS.ERROR, error: err.message || 'Something went wrong.', progress: '' });
    }
  }, []);

  const reset = useCallback(() => setState(initialState), []);

  // Mock helper — injects fake data with a simulated delay
  const setMockData = (mockAnalysis, mockLayouts) => {
    update({ step: ANALYSIS_STEPS.ANALYZING, error: null, progress: 'Reading the room…', analysis: null, layouts: null });
    setTimeout(() => {
      update({ analysis: mockAnalysis, step: ANALYSIS_STEPS.GENERATING, progress: 'Generating layout alternatives…' });
      setTimeout(() => {
        update({ layouts: mockLayouts, step: ANALYSIS_STEPS.DONE, progress: '' });
      }, 1800);
    }, 2000);
  };

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
