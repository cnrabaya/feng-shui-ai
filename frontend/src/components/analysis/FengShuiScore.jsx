// FengShuiScore.jsx — Hero score display + breakdown
// Score is now prominent, animated, and immediately visible at the top.
import React, { useEffect, useState } from 'react';
import Card from '../ui/Card';

const ELEMENT_COLORS = { wood:'#4a7c59', fire:'#c0392b', earth:'#8b6914', metal:'#7a8a9a', water:'#2c5f7a' };
const ELEMENT_ICONS  = { wood:'🌿', fire:'🔥', earth:'🏔', metal:'⚙', water:'💧' };
const SCORE_LABELS   = { qi_flow:'Qi Flow', balance:'Balance', natural_light:'Natural Light', clutter:'Clutter', bagua_alignment:'Bagua Alignment' };

// Animated count-up number
function CountUp({ target, duration = 1200 }) {
  const [val, setVal] = useState(0);
  useEffect(() => {
    let start = null;
    const step = (ts) => {
      if (!start) start = ts;
      const p = Math.min((ts - start) / duration, 1);
      // ease-out cubic
      const eased = 1 - Math.pow(1 - p, 3);
      setVal(Math.round(eased * target));
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [target, duration]);
  return val;
}

// Large hero score ring
function HeroRing({ score }) {
  const size = 160;
  const strokeW = 10;
  const r    = (size - strokeW) / 2;
  const circ = 2 * Math.PI * r;
  const color = score >= 75 ? '#4a7c59' : score >= 50 ? '#d4a84b' : '#c0392b';
  const label = score >= 75 ? 'Harmonious' : score >= 50 ? 'Balanced' : 'Needs Attention';
  const animatedScore = CountUp({ target: score });

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:'var(--space-3)' }}>
      <div style={{ position:'relative', width:size, height:size }}>
        {/* Glow */}
        <div style={{
          position:'absolute', inset:-8,
          borderRadius:'50%',
          background:`radial-gradient(circle, ${color}22 0%, transparent 70%)`,
          animation:'scorePulse 3s ease-in-out infinite',
        }}/>
        <style>{`
          @keyframes scorePulse { 0%,100%{opacity:0.6;transform:scale(0.97)} 50%{opacity:1;transform:scale(1.03)} }
          @keyframes ringFill { from{stroke-dasharray:0 ${circ}} }
        `}</style>
        <svg width={size} height={size} style={{transform:'rotate(-90deg)'}}>
          {/* Track */}
          <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={strokeW}/>
          {/* Filled arc */}
          <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth={strokeW}
            strokeDasharray={`${(score/100)*circ} ${circ}`} strokeLinecap="round"
            style={{ animation:'ringFill 1.2s cubic-bezier(0.4,0,0.2,1) both', transition:'stroke-dasharray 1s ease' }}/>
        </svg>
        {/* Center number */}
        <div style={{ position:'absolute', inset:0, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
          <span style={{ fontFamily:'var(--font-display)', fontSize:48, fontWeight:700, color, lineHeight:1, letterSpacing:'-0.02em' }}>
            {animatedScore}
          </span>
          <span style={{ fontSize:'var(--text-xs)', color:'var(--text-muted)', letterSpacing:'0.1em' }}>/100</span>
        </div>
      </div>
      {/* Label badge */}
      <div style={{
        background:`${color}22`, border:`1px solid ${color}55`,
        borderRadius:'var(--radius-sm)', padding:'4px 16px',
      }}>
        <span style={{ color, fontSize:'var(--text-sm)', fontWeight:600, letterSpacing:'0.08em' }}>{label}</span>
      </div>
    </div>
  );
}

function BreakdownBar({ label, score, note }) {
  const color = score >= 75 ? '#4a7c59' : score >= 50 ? '#d4a84b' : '#c0392b';
  const [hovered, setHovered] = useState(false);
  return (
    <div
      onMouseEnter={()=>setHovered(true)}
      onMouseLeave={()=>setHovered(false)}
      style={{ display:'flex', flexDirection:'column', gap:4, cursor:'default',
        padding:'var(--space-2) var(--space-3)', borderRadius:'var(--radius-sm)',
        background: hovered ? 'var(--bg-raised)' : 'transparent',
        transition:'background var(--duration-fast)' }}>
      <div style={{ display:'flex', alignItems:'center', gap:'var(--space-3)' }}>
        <span style={{ color:'var(--text-secondary)', fontSize:'var(--text-sm)', width:130, flexShrink:0 }}>{label}</span>
        <div style={{ flex:1, height:5, background:'var(--bg-overlay)', borderRadius:3, overflow:'hidden' }}>
          <div style={{ width:`${score}%`, height:'100%', background:color, borderRadius:3,
            transition:'width 1.2s cubic-bezier(0.4,0,0.2,1)', boxShadow:`0 0 6px ${color}88` }}/>
        </div>
        <span style={{ color, fontSize:'var(--text-sm)', width:28, textAlign:'right', fontWeight:700 }}>{score}</span>
      </div>
      {hovered && note && (
        <p style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)', lineHeight:1.5,
          paddingLeft:133, fontStyle:'italic', marginTop:2 }}>{note}</p>
      )}
    </div>
  );
}

export default function FengShuiScore({ fengShuiScore }) {
  if (!fengShuiScore) return null;
  const { total, breakdown, dominant_element, missing_element, summary } = fengShuiScore;
  const domColor  = ELEMENT_COLORS[dominant_element] || '#d4a84b';
  const missColor = ELEMENT_COLORS[missing_element]  || 'var(--text-muted)';

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:'var(--space-5)' }}>

      {/* ── HERO SCORE BANNER ── */}
      <div style={{
        background:'linear-gradient(135deg, var(--bg-surface) 0%, var(--bg-raised) 100%)',
        border:'1px solid var(--border-default)',
        borderRadius:'var(--radius-xl)',
        padding:'var(--space-8)',
        display:'flex', gap:'var(--space-8)', alignItems:'center',
        boxShadow:'var(--shadow-gold)',
        position:'relative', overflow:'hidden',
      }}>
        {/* Decorative bg glyph */}
        <div style={{ position:'absolute', right:24, top:'50%', transform:'translateY(-50%)',
          fontSize:120, opacity:0.04, fontFamily:'var(--font-accent)', pointerEvents:'none',
          userSelect:'none', lineHeight:1 }}>風水</div>

        <HeroRing score={total}/>

        <div style={{ flex:1, zIndex:1 }}>
          <p style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)', letterSpacing:'0.14em',
            textTransform:'uppercase', marginBottom:'var(--space-2)' }}>Feng Shui Score</p>
          <p style={{ color:'var(--text-secondary)', fontSize:'var(--text-sm)', lineHeight:1.8, marginBottom:'var(--space-4)' }}>
            {summary}
          </p>
          {/* Element pills */}
          <div style={{ display:'flex', gap:'var(--space-3)', flexWrap:'wrap' }}>
            <div style={{ display:'flex', alignItems:'center', gap:6,
              background:`${domColor}18`, border:`1px solid ${domColor}44`,
              borderRadius:'var(--radius-sm)', padding:'3px 10px' }}>
              <span style={{ fontSize:14 }}>{ELEMENT_ICONS[dominant_element]}</span>
              <span style={{ color:domColor, fontSize:'var(--text-xs)', fontWeight:600 }}>
                {dominant_element?.charAt(0).toUpperCase() + dominant_element?.slice(1)} dominant
              </span>
            </div>
            {missing_element && missing_element !== 'none' && (
              <div style={{ display:'flex', alignItems:'center', gap:6,
                background:`${missColor}18`, border:`1px solid ${missColor}44`,
                borderRadius:'var(--radius-sm)', padding:'3px 10px' }}>
                <span style={{ fontSize:14 }}>⚠</span>
                <span style={{ color:missColor, fontSize:'var(--text-xs)', fontWeight:600 }}>
                  {missing_element?.charAt(0).toUpperCase() + missing_element?.slice(1)} missing
                </span>
              </div>
            )}
            {(!missing_element || missing_element === 'none') && (
              <div style={{ display:'flex', alignItems:'center', gap:6,
                background:'#4a7c5918', border:'1px solid #4a7c5944',
                borderRadius:'var(--radius-sm)', padding:'3px 10px' }}>
                <span style={{ color:'#4a7c59', fontSize:'var(--text-xs)', fontWeight:600 }}>✓ All elements present</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── BREAKDOWN BARS ── */}
      {breakdown && (
        <Card>
          <p style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)', letterSpacing:'0.1em',
            textTransform:'uppercase', marginBottom:'var(--space-3)', paddingLeft:'var(--space-3)' }}>
            Score Breakdown <span style={{ fontWeight:300, opacity:0.6 }}>— hover for details</span>
          </p>
          <div style={{ display:'flex', flexDirection:'column', gap:'var(--space-1)' }}>
            {Object.entries(breakdown).map(([key, val]) => (
              <BreakdownBar key={key} label={SCORE_LABELS[key] || key} score={val.score} note={val.note}/>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
