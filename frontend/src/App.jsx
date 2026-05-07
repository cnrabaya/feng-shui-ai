// ─────────────────────────────────────────────
// App.jsx — Root component + step router
// Feng Shui Room Analyzer
// ─────────────────────────────────────────────
// USE_MOCK: set true to preview full UI without API. Flip to false when API is ready.
const USE_MOCK = true;

import React, { useState, useEffect } from 'react';
import './styles/tokens.css';
import { MOCK_ANALYSIS, MOCK_LAYOUTS } from './constants/mockData';

import StepIndicator  from './components/ui/StepIndicator';
import LoadingState   from './components/ui/LoadingState';
import Button         from './components/ui/Button';
import Card           from './components/ui/Card';

import ImageUploader  from './components/upload/ImageUploader';
import DimensionsInput from './components/upload/DimensionsInput';
import OrientationPicker from './components/upload/OrientationPicker';

import AnalysisPanel  from './components/analysis/AnalysisPanel';
import LayoutAlternatives from './components/layout/LayoutAlternatives';
import RoomCanvas     from './components/layout/RoomCanvas';
import LayoutEditor   from './components/layout/LayoutEditor';

import { useRoomAnalysis } from './hooks/useRoomAnalysis';
import { useLayoutEditor  } from './hooks/useLayoutEditor';

// ── Step IDs ──────────────────────────────────
const STEP = { UPLOAD: 1, ANALYZING: 2, RESULTS: 3, LAYOUTS: 4 };

export default function App() {
  // ── Image + dimensions state ──
  const [image, setImage]       = useState(null); // { base64, mediaType }
  const [dims, setDims]         = useState({ width: 0, height: 0, unit: 'm' });
  const [orientation, setOrientation] = useState(null); // compass direction string e.g. 'N', 'SW'
  const [currentStep, setStep]  = useState(STEP.UPLOAD);

  // ── AI analysis hook ──
  const analysis = useRoomAnalysis();

  // ── Layout editor hook ──
  const editor = useLayoutEditor([]);

  // When layouts arrive, init the editor
  useEffect(() => {
    if (analysis.layouts?.length) {
      editor.initLayouts(analysis.layouts);
      setStep(STEP.LAYOUTS);
    }
  }, [analysis.layouts]);

  useEffect(() => {
    if (analysis.isDone && analysis.analysis) setStep(STEP.RESULTS);
  }, [analysis.isDone, analysis.analysis]);

  useEffect(() => {
    if (analysis.isLoading) setStep(STEP.ANALYZING);
  }, [analysis.isLoading]);

  // ── Handlers ──
  const handleImageReady = ({ base64, mediaType }) => setImage({ base64, mediaType });

  const handleAnalyze = () => {
    if (USE_MOCK) {
      // Simulate loading delay then inject mock data
      analysis.setMockData(MOCK_ANALYSIS, MOCK_LAYOUTS);
      return;
    }
    if (!image || !dims.width || !dims.height) return;
    analysis.runAnalysis({
      imageBase64:   image.base64,
      imageMediaType: image.mediaType,
      width:  dims.width,
      height: dims.height,
      unit:   dims.unit,
      orientation,
    });
  };

  const canAnalyze = (USE_MOCK || image) && (USE_MOCK || dims.width > 0) && (USE_MOCK || dims.height > 0) && !analysis.isLoading;

  // ── Derived: which step number to show in indicator ──
  const indicatorStep = currentStep;

  return (
    <div style={{ minHeight:'100vh', background:'var(--bg-base)', display:'flex', flexDirection:'column' }}>

      {/* Header */}
      <header style={{ borderBottom:'1px solid var(--border-subtle)', padding:'var(--space-5) var(--space-8)',
        display:'flex', alignItems:'center', justifyContent:'space-between',
        background:'var(--bg-surface)', position:'sticky', top:0, zIndex:10 }}>
        <div>
          <h1 style={{ fontFamily:'var(--font-display)', fontSize:'var(--text-2xl)', fontWeight:300,
            color:'var(--gold-bright)', letterSpacing:'0.04em', lineHeight:1 }}>
            風水 <span style={{ color:'var(--text-primary)', fontWeight:300 }}>Analyzer</span>
          </h1>
          <p style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)', letterSpacing:'0.1em', marginTop:2 }}>
            AI-POWERED FENG SHUI ROOM ANALYSIS
          </p>
        </div>
        <StepIndicator currentStep={indicatorStep}/>
        {currentStep > STEP.UPLOAD && (
          <Button variant="ghost" size="sm" onClick={()=>{ analysis.reset(); setStep(STEP.UPLOAD); setImage(null); setOrientation(null); }}>
            ← New Analysis
          </Button>
        )}
      </header>

      {/* Main */}
      <main style={{ flex:1, padding:'var(--space-8)', maxWidth:1200, margin:'0 auto', width:'100%' }}>

        {/* ── STEP 1: Upload ── */}
        {currentStep === STEP.UPLOAD && (
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'var(--space-8)', alignItems:'start' }}>
            <div style={{ display:'flex', flexDirection:'column', gap:'var(--space-6)' }}>
              <div>
                <p style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)', letterSpacing:'0.12em', textTransform:'uppercase', marginBottom:'var(--space-2)' }}>Step 1</p>
                <h2 style={{ fontFamily:'var(--font-display)', fontSize:'var(--text-3xl)', fontWeight:300, color:'var(--text-primary)', lineHeight:1.2 }}>
                  Upload Your Room
                </h2>
                <p style={{ color:'var(--text-secondary)', marginTop:'var(--space-3)', lineHeight:1.7 }}>
                  Photograph your room and enter its dimensions. Our AI will evaluate the Feng Shui and suggest optimized layouts.
                </p>
              </div>
              <ImageUploader onImageReady={handleImageReady}/>
            </div>
            <div style={{ display:'flex', flexDirection:'column', gap:'var(--space-6)' }}>
              <Card>
                <DimensionsInput {...dims} onChange={setDims}/>
              </Card>
              <Card>
                <p style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)', letterSpacing:'0.1em', textTransform:'uppercase', marginBottom:'var(--space-4)' }}>Photo Orientation</p>
                <OrientationPicker value={orientation} onChange={setOrientation}/>
              </Card>
              <Button variant="primary" size="lg" fullWidth disabled={!canAnalyze} onClick={handleAnalyze}>
                Analyze Room →
              </Button>
              {analysis.isError && (
                <Card style={{ borderColor:'rgba(192,57,43,0.4)' }}>
                  <p style={{ color:'var(--red-accent)', fontSize:'var(--text-sm)' }}>⚠ {analysis.error}</p>
                </Card>
              )}
            </div>
          </div>
        )}

        {/* ── STEP 2: Loading ── */}
        {currentStep === STEP.ANALYZING && (
          <div style={{ display:'flex', alignItems:'center', justifyContent:'center', minHeight:'60vh' }}>
            <LoadingState message={analysis.progress}/>
          </div>
        )}

        {/* ── STEP 3: Results ── */}
        {currentStep === STEP.RESULTS && analysis.analysis && (
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'var(--space-8)', alignItems:'start' }}>
            <AnalysisPanel analysis={analysis.analysis}/>
            <div style={{ display:'flex', flexDirection:'column', gap:'var(--space-6)' }}>
              {image && (
                <Card style={{ padding:0, overflow:'hidden' }}>
                  <img src={`data:${image.mediaType};base64,${image.base64}`} alt="Analyzed room"
                    style={{ width:'100%', maxHeight:300, objectFit:'cover', borderRadius:'var(--radius-lg)' }}/>
                </Card>
              )}
              <Button variant="primary" size="lg" fullWidth onClick={()=>setStep(STEP.LAYOUTS)}>
                View Layout Alternatives →
              </Button>
            </div>
          </div>
        )}

        {/* ── STEP 4: Layouts ── */}
        {currentStep === STEP.LAYOUTS && (
          <div style={{ display:'grid', gridTemplateColumns:'340px 1fr', gap:'var(--space-8)', alignItems:'start' }}>
            {/* Left sidebar */}
            <div style={{ display:'flex', flexDirection:'column', gap:'var(--space-6)' }}>
              <LayoutAlternatives
                layouts={editor.layouts}
                selectedId={editor.selectedLayoutId}
                onSelect={editor.selectLayout}
              />
              <div style={{ borderTop:'1px solid var(--border-subtle)', paddingTop:'var(--space-6)' }}>
                <LayoutEditor
                  selectedFurnitureId={editor.selectedFurnitureId}
                  editMode={editor.editMode}
                  onToggleEdit={()=>editor.setEditMode(m=>!m)}
                  onRotate={editor.rotateFurniture}
                  onRemove={editor.removeFurniture}
                  onAdd={editor.addFurniture}
                />
              </div>
              <Button variant="ghost" size="sm" onClick={()=>setStep(STEP.RESULTS)}>
                ← Back to Analysis
              </Button>
            </div>

            {/* Canvas area */}
            <div style={{ display:'flex', flexDirection:'column', gap:'var(--space-4)' }}>
              <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between' }}>
                <div>
                  <p style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)', letterSpacing:'0.12em', textTransform:'uppercase' }}>2D Floor Plan</p>
                  <h3 style={{ fontFamily:'var(--font-display)', fontSize:'var(--text-xl)', fontWeight:300, color:'var(--text-primary)' }}>
                    {editor.activeLayout?.name || 'Select a layout'}
                  </h3>
                </div>
                {editor.activeLayout && (
                  <div style={{ textAlign:'right' }}>
                    <p style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)' }}>
                      {editor.activeLayout.furniture?.length || 0} pieces
                    </p>
                  </div>
                )}
              </div>
              <Card style={{ padding:'var(--space-4)', overflow:'auto' }}>
                {editor.activeLayout ? (
                  <RoomCanvas
                    roomWidth={dims.width}
                    roomHeight={dims.height}
                    furniture={editor.activeLayout.furniture || []}
                    selectedId={editor.selectedFurnitureId}
                    onSelectFurniture={editor.editMode ? editor.selectFurniture : undefined}
                    onPlaceFurniture={editor.placeFurniture}
                    editMode={editor.editMode}
                  />
                ) : (
                  <div style={{ padding:'var(--space-16)', textAlign:'center', color:'var(--text-muted)' }}>
                    Select a layout alternative to preview
                  </div>
                )}
              </Card>
              {editor.activeLayout?.rationale && (
                <p style={{ color:'var(--text-secondary)', fontSize:'var(--text-sm)', lineHeight:1.7,
                  fontStyle:'italic', paddingLeft:'var(--space-4)', borderLeft:'2px solid var(--border-default)' }}>
                  {editor.activeLayout.rationale}
                </p>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
