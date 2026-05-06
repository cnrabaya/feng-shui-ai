// LayoutAlternatives.jsx — Cards to pick between 2-3 layout alternatives
import React from 'react';
import Card from '../ui/Card';

const ELEMENT_COLORS = { wood:'#4a7c59', fire:'#c0392b', earth:'#8b6914', metal:'#7a8a9a', water:'#2c5f7a' };

function ScoreDelta({ delta }) {
  const color = delta > 0 ? 'var(--green-qi)' : delta < 0 ? 'var(--red-accent)' : 'var(--text-muted)';
  return (
    <span style={{ color, fontSize:'var(--text-sm)', fontWeight:600 }}>
      {delta > 0 ? '+' : ''}{delta} pts
    </span>
  );
}

export default function LayoutAlternatives({ layouts = [], selectedId, onSelect }) {
  if (!layouts.length) return null;
  return (
    <div style={{ display:'flex', flexDirection:'column', gap:'var(--space-4)' }}>
      <p style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)', letterSpacing:'0.12em', textTransform:'uppercase' }}>
        Layout Alternatives
      </p>
      <div style={{ display:'flex', flexDirection:'column', gap:'var(--space-3)' }}>
        {layouts.map((layout, i) => {
          const isSelected = layout.id === selectedId;
          const elemColor  = ELEMENT_COLORS[layout.dominant_element] || 'var(--gold-bright)';
          return (
            <Card key={layout.id} highlight={isSelected} onClick={()=>onSelect(layout.id)}
              style={{ transition:'all var(--duration-normal)', position:'relative', overflow:'hidden',
                background: isSelected ? 'var(--bg-raised)' : 'var(--bg-surface)' }}>
              {/* Left accent bar */}
              <div style={{ position:'absolute', left:0, top:0, bottom:0, width:3,
                background: isSelected ? 'var(--gold-bright)' : elemColor, opacity: isSelected?1:0.5 }}/>
              <div style={{ paddingLeft:'var(--space-4)' }}>
                <div style={{ display:'flex', alignItems:'flex-start', justifyContent:'space-between', marginBottom:'var(--space-2)' }}>
                  <div>
                    <div style={{ display:'flex', alignItems:'center', gap:'var(--space-2)', marginBottom:'var(--space-1)' }}>
                      <span style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)' }}>0{i+1}</span>
                      <h3 style={{ fontFamily:'var(--font-display)', color: isSelected?'var(--gold-bright)':'var(--text-primary)',
                        fontSize:'var(--text-base)', fontWeight: isSelected?600:400 }}>
                        {layout.name}
                      </h3>
                    </div>
                    <p style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)', fontStyle:'italic' }}>{layout.theme}</p>
                  </div>
                  <div style={{ textAlign:'right', flexShrink:0, marginLeft:'var(--space-4)' }}>
                    <ScoreDelta delta={layout.fengShuiImprovement}/>
                    <p style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)', marginTop:2 }}>vs current</p>
                  </div>
                </div>
                {isSelected && (
                  <p style={{ color:'var(--text-secondary)', fontSize:'var(--text-sm)', lineHeight:1.6, marginTop:'var(--space-3)',
                    borderTop:'1px solid var(--border-subtle)', paddingTop:'var(--space-3)' }}>
                    {layout.rationale}
                  </p>
                )}
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
