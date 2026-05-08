// AnalysisPanel.jsx — Score first, then description
import React from 'react';
import FengShuiScore from './FengShuiScore';
import RoomDescription from './RoomDescription';

export default function AnalysisPanel({ analysis }) {
  if (!analysis) return null;
  return (
    <div style={{ display:'flex', flexDirection:'column', gap:'var(--space-6)' }}>
      <div>
        <p style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)', letterSpacing:'0.12em', textTransform:'uppercase', marginBottom:'var(--space-2)' }}>Room Analysis</p>
        <h2 style={{ fontFamily:'var(--font-display)', fontSize:'var(--text-3xl)', color:'var(--text-primary)', fontWeight:300 }}>
          Your Space, Evaluated
        </h2>
      </div>
      {/* Score banner comes first — immediately visible */}
      <FengShuiScore fengShuiScore={analysis.fengShuiScore}/>
      <RoomDescription analysis={analysis}/>
    </div>
  );
}
