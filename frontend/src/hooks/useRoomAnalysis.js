// ─────────────────────────────────────────────
// useRoomAnalysis.js
// Manages full analysis, layout generation, and re-analysis of edited layouts.
// ─────────────────────────────────────────────
import { useState, useCallback } from 'react';
import { analyzeRoom, generateLayouts, reanalyzeLayout } from '../services/anthropicService';

export const ANALYSIS_STEPS = {
  IDLE:         'idle',
  ANALYZING:    'analyzing',
  GENERATING:   'generating',
  REANALYZING:  'reanalyzing',
  DONE:         'done',
  ERROR:        'error',
};

const initialState = {
  step:           ANALYSIS_STEPS.IDLE,
  analysis:       null,
  layouts:        null,
  reanalysisResult: null, // fengShuiScore for the edited layout
  error:          null,
  progress:       '',
};

export function useRoomAnalysis() {
  const [state, setState] = useState(initialState);
  const update = (patch) => setState(prev => ({ ...prev, ...patch }));

  // Full pipeline: analyze images → generate layouts
  const runAnalysis = useCallback(async ({ photos, width, height, unit }) => {
    update({ step: ANALYSIS_STEPS.ANALYZING, error:null, progress:'Reading the room…', analysis:null, layouts:null, reanalysisResult:null });
    try {
      const analysis = await analyzeRoom({ photos, width, height, unit });
      update({ analysis, step: ANALYSIS_STEPS.GENERATING, progress:'Generating layout alternatives…' });
      const { layouts } = await generateLayouts({ analysis, width, height, unit });
      update({ layouts, step: ANALYSIS_STEPS.DONE, progress:'' });
    } catch (err) {
      update({ step: ANALYSIS_STEPS.ERROR, error: err.message || 'Something went wrong.', progress:'' });
    }
  }, []);

  // Re-score an edited layout
  const runReanalysis = useCallback(async ({ layout, width, height, unit }) => {
    update({ step: ANALYSIS_STEPS.REANALYZING, progress:'Scoring your edited layout…', reanalysisResult:null, error:null });
    try {
      const result = await reanalyzeLayout({
        layout,
        originalAnalysis: state.analysis,
        width, height, unit,
      });
      update({ reanalysisResult: result, step: ANALYSIS_STEPS.DONE, progress:'' });
    } catch (err) {
      update({ step: ANALYSIS_STEPS.ERROR, error: err.message || 'Re-analysis failed.', progress:'' });
    }
  }, [state.analysis]);

  // Mock helper — injects fake data with simulated delay
  const setMockData = (mockAnalysis, mockLayouts) => {
    update({ step: ANALYSIS_STEPS.ANALYZING, error:null, progress:'Reading the room…', analysis:null, layouts:null, reanalysisResult:null });
    setTimeout(() => {
      update({ analysis: mockAnalysis, step: ANALYSIS_STEPS.GENERATING, progress:'Generating layout alternatives…' });
      setTimeout(() => {
        update({ layouts: mockLayouts, step: ANALYSIS_STEPS.DONE, progress:'' });
      }, 1800);
    }, 2000);
  };

  // Mock re-analysis — bumps the score by a random delta
  const setMockReanalysis = (layout) => {
    update({ step: ANALYSIS_STEPS.REANALYZING, progress:'Scoring your edited layout…', reanalysisResult:null });
    setTimeout(() => {
      const base  = state.analysis?.fengShuiScore?.total || 60;
      const delta = Math.round((Math.random() * 16) - 4); // -4 to +12
      const total = Math.max(0, Math.min(100, base + delta));
      update({
        step: ANALYSIS_STEPS.DONE,
        progress: '',
        reanalysisResult: {
          total,
          delta,
          breakdown: state.analysis?.fengShuiScore?.breakdown,
          dominant_element: state.analysis?.fengShuiScore?.dominant_element,
          missing_element:  state.analysis?.fengShuiScore?.missing_element,
          summary: delta >= 0
            ? `Your edits improved the layout's qi flow. The rearrangement scores ${total}/100.`
            : `The edited arrangement shifts some energy patterns. Score: ${total}/100.`,
          issues:          [],
          recommendations: ['Continue refining to raise the score further.'],
        },
      });
    }, 2200);
  };

  const clearReanalysis = useCallback(() => update({ reanalysisResult: null }), []);

  const reset = useCallback(() => setState(initialState), []);

  return {
    ...state,
    runAnalysis,
    runReanalysis,
    setMockData,
    setMockReanalysis,
    clearReanalysis,
    reset,
    isLoading:     state.step === ANALYSIS_STEPS.ANALYZING || state.step === ANALYSIS_STEPS.GENERATING,
    isReanalyzing: state.step === ANALYSIS_STEPS.REANALYZING,
    isIdle:        state.step === ANALYSIS_STEPS.IDLE,
    isDone:        state.step === ANALYSIS_STEPS.DONE,
    isError:       state.step === ANALYSIS_STEPS.ERROR,
  };
}
