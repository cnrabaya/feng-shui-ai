// FengShuiScore.jsx — Score display + breakdown
import React from 'react';
import Card from '../ui/Card';

const ELEMENT_COLORS = { wood:'#4a7c59', fire:'#c0392b', earth:'#8b6914', metal:'#7a8a9a', water:'#2c5f7a' };
const ELEMENT_ICONS  = { wood:'🌿', fire:'🔥', earth:'🏔', metal:'⚙', water:'💧' };
const SCORE_LABELS   = { qi_flow:'Qi Flow', balance:'Balance', natural_light:'Natural Light', clutter:'Clutter', bagua_alignment:'Bagua Alignment' };

function ScoreRing({ score, size = 100 }) {
  const r = (size - 12) / 2;
  const circ = 2 * Math.PI * r;
  const dash = (score / 100) * circ;
  const color = score >= 75 ? 'var(--green-qi)' : score >= 50 ? 'var(--gold-bright)' : 'var(--red-accent)';
  return (
    <div style={{ position:'relative', width:size, height:size, flexShrink:0 }}>
      <svg width={size} height={size} style={{transform:'rotate(-90deg)'}}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="var(--border-subtle)" strokeWidth="6"/>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth="6"
          strokeDasharray={`${dash} ${circ}`} strokeLinecap="round"
          style={{transition:'stroke-dasharray 1s var(--ease-smooth)'}}/>
      </svg>
      <div style={{ position:'absolute', inset:0, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
        <span style={{ fontSize: size > 80 ? 'var(--text-2xl)' : 'var(--text-lg)', fontWeight:700, color, fontFamily:'var(--font-display)', lineHeight:1 }}>{score}</span>
        {size > 80 && <span style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)' }}>/100</span>}
      </div>
    </div>
  );
}

function BreakdownBar({ label, score }) {
  const color = score >= 75 ? 'var(--green-qi)' : score >= 50 ? 'var(--gold-bright)' : 'var(--red-accent)';
  return (
    <div style={{ display:'flex', alignItems:'center', gap:'var(--space-3)' }}>
      <span style={{ color:'var(--text-secondary)', fontSize:'var(--text-sm)', width:130, flexShrink:0 }}>{label}</span>
      <div style={{ flex:1, height:4, background:'var(--bg-raised)', borderRadius:2, overflow:'hidden' }}>
        <div style={{ width:`${score}%`, height:'100%', background:color, borderRadius:2, transition:'width 1s var(--ease-smooth)' }}/>
      </div>
      <span style={{ color, fontSize:'var(--text-sm)', width:28, textAlign:'right', fontWeight:600 }}>{score}</span>
    </div>
  );
}

export default function FengShuiScore({ fengShuiScore }) {
  if (!fengShuiScore) return null;
  const { total, breakdown, dominant_element, missing_element, summary } = fengShuiScore;
  const domColor  = ELEMENT_COLORS[dominant_element] || 'var(--gold-bright)';
  const missColor = ELEMENT_COLORS[missing_element]  || 'var(--text-muted)';

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:'var(--space-6)' }}>
      {/* Total score */}
      <Card style={{ display:'flex', alignItems:'center', gap:'var(--space-6)' }}>
        <ScoreRing score={total} size={110}/>
        <div style={{ flex:1 }}>
          <p style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)', letterSpacing:'0.1em', textTransform:'uppercase', marginBottom:'var(--space-1)' }}>
            Feng Shui Score
          </p>
          <h2 style={{ fontFamily:'var(--font-display)', fontSize:'var(--text-2xl)', color:'var(--text-primary)', marginBottom:'var(--space-3)' }}>
            {total >= 75 ? 'Harmonious' : total >= 50 ? 'Balanced' : 'Needs Attention'}
          </h2>
          <p style={{ color:'var(--text-secondary)', fontSize:'var(--text-sm)', lineHeight:1.7 }}>{summary}</p>
        </div>
      </Card>

      {/* Breakdown bars */}
      {breakdown && (
        <Card>
          <p style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)', letterSpacing:'0.1em', textTransform:'uppercase', marginBottom:'var(--space-4)' }}>Score Breakdown</p>
          <div style={{ display:'flex', flexDirection:'column', gap:'var(--space-3)' }}>
            {Object.entries(breakdown).map(([key, val]) => (
              <BreakdownBar key={key} label={SCORE_LABELS[key] || key} score={val.score}/>
            ))}
          </div>
        </Card>
      )}

      {/* Elements */}
      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'var(--space-4)' }}>
        <Card style={{ borderColor: `${domColor}55` }}>
          <p style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)', letterSpacing:'0.08em', textTransform:'uppercase', marginBottom:'var(--space-2)' }}>Dominant Element</p>
          <div style={{ display:'flex', alignItems:'center', gap:'var(--space-3)' }}>
            <span style={{ fontSize:28 }}>{ELEMENT_ICONS[dominant_element]}</span>
            <span style={{ fontFamily:'var(--font-display)', fontSize:'var(--text-xl)', color:domColor, textTransform:'capitalize' }}>{dominant_element}</span>
          </div>
        </Card>
        <Card style={{ borderColor: missing_element !== 'none' ? `${missColor}55` : 'var(--border-subtle)' }}>
          <p style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)', letterSpacing:'0.08em', textTransform:'uppercase', marginBottom:'var(--space-2)' }}>Missing Element</p>
          <div style={{ display:'flex', alignItems:'center', gap:'var(--space-3)' }}>
            <span style={{ fontSize:28 }}>{missing_element && missing_element !== 'none' ? ELEMENT_ICONS[missing_element] : '✓'}</span>
            <span style={{ fontFamily:'var(--font-display)', fontSize:'var(--text-xl)', color: missing_element !== 'none' ? missColor : 'var(--green-qi)', textTransform:'capitalize' }}>
              {missing_element === 'none' ? 'All Present' : missing_element}
            </span>
          </div>
        </Card>
      </div>
    </div>
  );
}
