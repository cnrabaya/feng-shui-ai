// RoomDescription.jsx — AI-generated room description + issues/recommendations
import React, { useState } from 'react';
import Card from '../ui/Card';

export default function RoomDescription({ analysis }) {
  const [tab, setTab] = useState('description');
  if (!analysis) return null;
  const { description, style, issues = [], recommendations = [] } = analysis;

  const TabBtn = ({ id, label }) => (
    <button onClick={()=>setTab(id)} style={{
      background:'none', border:'none', cursor:'pointer', padding:'var(--space-2) var(--space-4)',
      fontFamily:'var(--font-body)', fontSize:'var(--text-sm)', letterSpacing:'0.05em',
      color: tab===id ? 'var(--gold-bright)' : 'var(--text-muted)',
      borderBottom: `2px solid ${tab===id ? 'var(--gold-bright)' : 'transparent'}`,
      transition:'all var(--duration-fast)',
    }}>{label}</button>
  );

  return (
    <Card>
      {style && (
        <div style={{ display:'inline-block', background:'var(--gold-glow)', border:'1px solid var(--border-default)',
          borderRadius:'var(--radius-sm)', padding:'2px 10px', marginBottom:'var(--space-4)' }}>
          <span style={{ color:'var(--gold-bright)', fontSize:'var(--text-xs)', letterSpacing:'0.1em', textTransform:'uppercase' }}>{style}</span>
        </div>
      )}

      <div style={{ display:'flex', gap:0, borderBottom:'1px solid var(--border-subtle)', marginBottom:'var(--space-4)' }}>
        <TabBtn id="description" label="Overview"/>
        <TabBtn id="issues" label={`Issues (${issues.length})`}/>
        <TabBtn id="recommendations" label="Recommendations"/>
      </div>

      {tab === 'description' && (
        <p style={{ color:'var(--text-secondary)', lineHeight:1.8, fontFamily:'var(--font-display)', fontSize:'var(--text-base)' }}>{description}</p>
      )}
      {tab === 'issues' && (
        <ul style={{ listStyle:'none', display:'flex', flexDirection:'column', gap:'var(--space-3)' }}>
          {issues.length === 0 ? <li style={{color:'var(--green-qi)'}}>✓ No major issues detected</li> :
            issues.map((issue, i) => (
              <li key={i} style={{ display:'flex', gap:'var(--space-3)', color:'var(--text-secondary)', fontSize:'var(--text-sm)', lineHeight:1.6 }}>
                <span style={{ color:'var(--red-accent)', flexShrink:0 }}>⚠</span>{issue}
              </li>
            ))}
        </ul>
      )}
      {tab === 'recommendations' && (
        <ul style={{ listStyle:'none', display:'flex', flexDirection:'column', gap:'var(--space-3)' }}>
          {recommendations.map((rec, i) => (
            <li key={i} style={{ display:'flex', gap:'var(--space-3)', color:'var(--text-secondary)', fontSize:'var(--text-sm)', lineHeight:1.6 }}>
              <span style={{ color:'var(--gold-bright)', flexShrink:0 }}>◈</span>{rec}
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
