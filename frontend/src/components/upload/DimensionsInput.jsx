// DimensionsInput.jsx — Room dimensions form
import React from 'react';

export default function DimensionsInput({ width, height, unit, onChange }) {
  const fieldStyle = {
    background:'var(--bg-raised)', border:'1px solid var(--border-default)',
    borderRadius:'var(--radius-md)', padding:'var(--space-3) var(--space-4)',
    color:'var(--text-primary)', fontSize:'var(--text-base)',
    fontFamily:'var(--font-body)', width:'100%', outline:'none',
    transition:'border-color var(--duration-fast)',
  };
  const labelStyle = { color:'var(--text-secondary)', fontSize:'var(--text-sm)', marginBottom:'var(--space-2)', display:'block', fontFamily:'var(--font-body)' };

  return (
    <div style={{display:'flex', flexDirection:'column', gap:'var(--space-4)'}}>
      <p style={{color:'var(--text-secondary)', fontSize:'var(--text-sm)', fontStyle:'italic'}}>
        Enter your room's floor dimensions
      </p>
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr 100px', gap:'var(--space-4)', alignItems:'end'}}>
        <div>
          <label style={labelStyle}>Width</label>
          <input type="number" min="1" max="100" value={width} placeholder="e.g. 4.5"
            style={fieldStyle}
            onFocus={e=>e.target.style.borderColor='var(--gold-bright)'}
            onBlur={e=>e.target.style.borderColor='var(--border-default)'}
            onChange={e=>onChange({width:parseFloat(e.target.value)||0, height, unit})}/>
        </div>
        <div>
          <label style={labelStyle}>Length</label>
          <input type="number" min="1" max="100" value={height} placeholder="e.g. 6"
            style={fieldStyle}
            onFocus={e=>e.target.style.borderColor='var(--gold-bright)'}
            onBlur={e=>e.target.style.borderColor='var(--border-default)'}
            onChange={e=>onChange({width, height:parseFloat(e.target.value)||0, unit})}/>
        </div>
        <div>
          <label style={labelStyle}>Unit</label>
          <select value={unit} style={{...fieldStyle, cursor:'pointer'}}
            onChange={e=>onChange({width, height, unit:e.target.value})}>
            <option value="m">meters</option>
            <option value="ft">feet</option>
          </select>
        </div>
      </div>
      {width > 0 && height > 0 && (
        <p style={{color:'var(--gold-muted)', fontSize:'var(--text-sm)'}}>
          ◻ Floor area: <strong style={{color:'var(--gold-bright)'}}>{(width * height).toFixed(1)} {unit}²</strong>
        </p>
      )}
    </div>
  );
}
