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

import MultiImageUploader from './components/upload/MultiImageUploader';
import DimensionsInput from './components/upload/DimensionsInput';
import OrientationPicker from './components/upload/OrientationPicker';

import AnalysisPanel  from './components/analysis/AnalysisPanel';
import FengShuiScore  from './components/analysis/FengShuiScore';
import LayoutAlternatives from './components/layout/LayoutAlternatives';
import RoomCanvas     from './components/layout/RoomCanvas';
import LayoutEditor   from './components/layout/LayoutEditor';

import { useRoomAnalysis } from './hooks/useRoomAnalysis';
import { useLayoutEditor  } from './hooks/useLayoutEditor';

// ── Step IDs ──────────────────────────────────
const STEP = { UPLOAD: 1, ANALYZING: 2, RESULTS: 3, LAYOUTS: 4 };

export default function App() {
  // ── Image + dimensions state ──
  const [photos, setPhotos]     = useState([]); // [{ id, base64, mediaType, orientation, previewUrl }]
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
  const handleAnalyze = () => {
    if (USE_MOCK) {
      // Simulate loading delay then inject mock data
      analysis.setMockData(MOCK_ANALYSIS, MOCK_LAYOUTS);
      return;
    }
    if (!photos.length || !dims.width || !dims.height) return;
    analysis.runAnalysis({
      photos: photos.map(p => ({ base64: p.base64, mediaType: p.mediaType, orientation: p.orientation })),
      width:  dims.width,
      height: dims.height,
      unit:   dims.unit,
    });
  };

  const canAnalyze = (USE_MOCK || photos.length > 0) && (USE_MOCK || dims.width > 0) && (USE_MOCK || dims.height > 0) && !analysis.isLoading;

  const handleReanalyze = () => {
    if (!editor.activeLayout) return;
    if (USE_MOCK) {
      analysis.setMockReanalysis(editor.activeLayout);
    } else {
      analysis.runReanalysis({
        layout: editor.activeLayout,
        width: dims.width,
        height: dims.height,
        unit: dims.unit,
      });
    }
  };

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
          <Button variant="ghost" size="sm" onClick={()=>{ analysis.reset(); setStep(STEP.UPLOAD); setPhotos([]); setOrientation(null); }}>
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
              <MultiImageUploader photos={photos} onPhotosChange={setPhotos}/>
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
              {photos.length > 0 && (
                <Card style={{ padding:'var(--space-3)', overflow:'hidden' }}>
                  <div style={{ display:'flex', gap:'var(--space-2)', overflowX:'auto' }}>
                    {photos.map((p,i) => (
                      <div key={p.id} style={{ position:'relative', flexShrink:0 }}>
                        <img src={p.previewUrl} alt={`Photo ${i+1}`}
                          style={{ height:120, width:'auto', borderRadius:'var(--radius-md)', objectFit:'cover', display:'block' }}/>
                        {p.orientation && (
                          <span style={{ position:'absolute', bottom:4, left:4, background:'rgba(0,0,0,0.7)',
                            color:'var(--gold-bright)', fontSize:'var(--text-xs)', padding:'1px 6px',
                            borderRadius:'var(--radius-sm)', fontWeight:600 }}>↑{p.orientation}</span>
                        )}
                      </div>
                    ))}
                  </div>
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
              {/* Header row */}
              <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between' }}>
                <div>
                  <p style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)', letterSpacing:'0.12em', textTransform:'uppercase' }}>2D Floor Plan</p>
                  <h3 style={{ fontFamily:'var(--font-display)', fontSize:'var(--text-xl)', fontWeight:300, color:'var(--text-primary)' }}>
                    {editor.activeLayout?.name || 'Select a layout'}
                  </h3>
                </div>
                {editor.activeLayout && (
                  <div style={{ display:'flex', alignItems:'center', gap:'var(--space-3)' }}>
                    <p style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)' }}>
                      {editor.activeLayout.furniture?.length || 0} pieces
                    </p>
                    {/* Re-analyze button */}
                    <Button
                      variant={analysis.reanalysisResult ? 'ghost' : 'secondary'}
                      size="sm"
                      disabled={analysis.isReanalyzing}
                      onClick={handleReanalyze}
                      style={{ whiteSpace:'nowrap' }}
                    >
                      {analysis.isReanalyzing ? '◎ Scoring…' : '☯ Re-analyze Layout'}
                    </Button>
                  </div>
                )}
              </div>

              {/* Canvas */}
              <Card style={{ padding:'var(--space-4)', overflow:'auto' }}>
                {editor.activeLayout ? (
                  <RoomCanvas
                    roomWidth={dims.width}
                    roomHeight={dims.height}
                    roomGrid={analysis.analysis?.roomGrid}
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

              {/* Rationale */}
              {editor.activeLayout?.rationale && !analysis.reanalysisResult && (
                <p style={{ color:'var(--text-secondary)', fontSize:'var(--text-sm)', lineHeight:1.7,
                  fontStyle:'italic', paddingLeft:'var(--space-4)', borderLeft:'2px solid var(--border-default)' }}>
                  {editor.activeLayout.rationale}
                </p>
              )}

              {/* Re-analysis loading */}
              {analysis.isReanalyzing && (
                <Card style={{ textAlign:'center', padding:'var(--space-8)' }}>
                  <p style={{ color:'var(--gold-bright)', fontFamily:'var(--font-display)', fontSize:'var(--text-lg)' }}>
                    ◎ Scoring your edited layout…
                  </p>
                  <p style={{ color:'var(--text-muted)', fontSize:'var(--text-sm)', marginTop:'var(--space-2)' }}>
                    Consulting the bagua for your arrangement
                  </p>
                </Card>
              )}

              {/* Re-analysis result */}
              {analysis.reanalysisResult && !analysis.isReanalyzing && (
                <div style={{ display:'flex', flexDirection:'column', gap:'var(--space-4)' }}>
                  <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between' }}>
                    <p style={{ color:'var(--gold-bright)', fontSize:'var(--text-sm)', fontWeight:600, letterSpacing:'0.05em' }}>
                      ✓ Edited Layout Score
                    </p>
                    <button onClick={analysis.clearReanalysis}
                      style={{ background:'none', border:'none', cursor:'pointer',
                        color:'var(--text-muted)', fontSize:'var(--text-xs)', fontFamily:'var(--font-body)' }}>
                      ✕ dismiss
                    </button>
                  </div>
                  {/* Delta badge */}
                  <div style={{ display:'flex', alignItems:'center', gap:'var(--space-4)',
                    background:'var(--bg-raised)', borderRadius:'var(--radius-md)',
                    padding:'var(--space-3) var(--space-4)', border:'1px solid var(--border-default)' }}>
                    <div style={{ textAlign:'center', flexShrink:0 }}>
                      <p style={{
                        fontFamily:'var(--font-display)', fontSize:40, fontWeight:700, lineHeight:1,
                        color: analysis.reanalysisResult.total >= 75 ? 'var(--green-qi)'
                          : analysis.reanalysisResult.total >= 50 ? 'var(--gold-bright)' : 'var(--red-accent)',
                      }}>{analysis.reanalysisResult.total}</p>
                      <p style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)' }}>/100</p>
                    </div>
                    <div style={{ flex:1 }}>
                      <div style={{ display:'flex', alignItems:'center', gap:'var(--space-2)', marginBottom:'var(--space-2)' }}>
                        <span style={{
                          color: analysis.reanalysisResult.delta >= 0 ? 'var(--green-qi)' : 'var(--red-accent)',
                          fontSize:'var(--text-sm)', fontWeight:700,
                        }}>
                          {analysis.reanalysisResult.delta >= 0 ? '+' : ''}{analysis.reanalysisResult.delta} pts
                        </span>
                        <span style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)' }}>vs original</span>
                      </div>
                      <p style={{ color:'var(--text-secondary)', fontSize:'var(--text-sm)', lineHeight:1.6 }}>
                        {analysis.reanalysisResult.summary}
                      </p>
                    </div>
                  </div>
                  <FengShuiScore fengShuiScore={analysis.reanalysisResult}/>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
