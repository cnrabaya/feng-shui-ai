// ─────────────────────────────────────────────
// OrientationPicker.jsx
// Visual compass rose — user selects the cardinal
// direction they were FACING when they took the photo.
// This tells the AI which wall is which.
// ─────────────────────────────────────────────
import React, { useState } from 'react';

const DIRECTIONS = [
  { id: 'N',  label: 'North', angle: 0,   x: 50, y: 8  },
  { id: 'NE', label: 'NE',    angle: 45,  x: 82, y: 18 },
  { id: 'E',  label: 'East',  angle: 90,  x: 92, y: 50 },
  { id: 'SE', label: 'SE',    angle: 135, x: 82, y: 82 },
  { id: 'S',  label: 'South', angle: 180, x: 50, y: 92 },
  { id: 'SW', label: 'SW',    angle: 225, x: 18, y: 82 },
  { id: 'W',  label: 'West',  angle: 270, x: 8,  y: 50 },
  { id: 'NW', label: 'NW',    angle: 315, x: 18, y: 18 },
];

const CARDINAL = ['N', 'E', 'S', 'W'];

// Needle points toward selected direction
function CompassNeedle({ angle }) {
  const rad    = (angle - 90) * (Math.PI / 180);
  const cx     = 50; const cy = 50; const len = 28;
  const tipX   = cx + Math.cos(rad) * len;
  const tipY   = cy + Math.sin(rad) * len;
  const tailX  = cx - Math.cos(rad) * 10;
  const tailY  = cy - Math.sin(rad) * 10;
  const perpX  = -Math.sin(rad) * 4;
  const perpY  =  Math.cos(rad) * 4;
  return (
    <g>
      {/* Gold needle tip */}
      <polygon
        points={`${tipX},${tipY} ${cx+perpX},${cy+perpY} ${tailX},${tailY} ${cx-perpX},${cy-perpY}`}
        fill="var(--gold-bright)" opacity={0.95}/>
      {/* South half (muted) */}
      <polygon
        points={`${tailX},${tailY} ${cx+perpX},${cy+perpY} ${cx*2-tipX},${cy*2-tipY} ${cx-perpX},${cy-perpY}`}
        fill="var(--ink-400)" opacity={0.6}/>
      {/* Center pin */}
      <circle cx={cx} cy={cy} r={3} fill="var(--gold-bright)"/>
      <circle cx={cx} cy={cy} r={1.5} fill="var(--ink-900)"/>
    </g>
  );
}

export default function OrientationPicker({ value, onChange }) {
  const [hovered, setHovered] = useState(null);
  const selected = DIRECTIONS.find(d => d.id === value);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--space-6)' }}>

        {/* Compass SVG */}
        <div style={{ position: 'relative', flexShrink: 0 }}>
          <svg viewBox="0 0 100 100" width={160} height={160} style={{ display: 'block' }}>
            {/* Outer ring */}
            <circle cx={50} cy={50} r={46} fill="var(--bg-raised)"
              stroke="var(--border-default)" strokeWidth={1}/>
            {/* Inner ring */}
            <circle cx={50} cy={50} r={32} fill="var(--bg-overlay)"
              stroke="var(--border-subtle)" strokeWidth={0.5}/>
            {/* Tick marks */}
            {Array.from({length: 36}).map((_, i) => {
              const a   = (i * 10 - 90) * Math.PI / 180;
              const r1  = i % 9 === 0 ? 38 : i % 3 === 0 ? 40 : 42;
              const r2  = 44;
              return (
                <line key={i}
                  x1={50 + Math.cos(a)*r1} y1={50 + Math.sin(a)*r1}
                  x2={50 + Math.cos(a)*r2} y2={50 + Math.sin(a)*r2}
                  stroke="var(--border-default)" strokeWidth={i % 9 === 0 ? 1 : 0.5}/>
              );
            })}
            {/* Cardinal cross lines */}
            {[0,90,180,270].map(deg => {
              const a = (deg-90)*Math.PI/180;
              return <line key={deg} x1={50+Math.cos(a)*20} y1={50+Math.sin(a)*20}
                x2={50+Math.cos(a)*32} y2={50+Math.sin(a)*32}
                stroke="var(--border-subtle)" strokeWidth={0.5}/>;
            })}

            {/* Direction buttons */}
            {DIRECTIONS.map(dir => {
              const isSelected = dir.id === value;
              const isHovered  = dir.id === hovered;
              const isCardinal = CARDINAL.includes(dir.id);
              const size = isCardinal ? 9 : 7;
              return (
                <g key={dir.id}
                  style={{ cursor: 'pointer' }}
                  onClick={() => onChange(dir.id)}
                  onMouseEnter={() => setHovered(dir.id)}
                  onMouseLeave={() => setHovered(null)}>
                  <circle
                    cx={dir.x} cy={dir.y} r={size}
                    fill={isSelected ? 'var(--gold-bright)' : isHovered ? 'var(--bg-overlay)' : 'transparent'}
                    stroke={isSelected ? 'var(--gold-bright)' : isHovered ? 'var(--border-default)' : 'transparent'}
                    strokeWidth={1}/>
                  <text x={dir.x} y={dir.y}
                    textAnchor="middle" dominantBaseline="middle"
                    style={{
                      fontSize: isCardinal ? 7 : 5,
                      fontFamily: 'var(--font-body)',
                      fontWeight: isCardinal ? 700 : 400,
                      fill: isSelected
                        ? 'var(--ink-900)'
                        : isCardinal
                          ? 'var(--text-secondary)'
                          : 'var(--text-muted)',
                      pointerEvents: 'none',
                      userSelect: 'none',
                      letterSpacing: '0.02em',
                    }}>
                    {dir.id}
                  </text>
                </g>
              );
            })}

            {/* Animated needle */}
            {value && <CompassNeedle angle={selected?.angle ?? 0}/>}

            {/* Center label when nothing selected */}
            {!value && (
              <text x={50} y={50} textAnchor="middle" dominantBaseline="middle"
                style={{ fontSize: 6, fontFamily: 'var(--font-body)', fill: 'var(--text-muted)', pointerEvents: 'none' }}>
                tap a direction
              </text>
            )}
          </svg>
        </div>

        {/* Right side: description */}
        <div style={{ flex: 1, paddingTop: 'var(--space-2)' }}>
          <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-sm)', lineHeight: 1.7, marginBottom: 'var(--space-4)' }}>
            Which direction were you <strong style={{ color: 'var(--text-primary)' }}>facing</strong> when you took the photo?
          </p>

          {value ? (
            <div style={{ background: 'var(--gold-glow)', border: '1px solid var(--border-default)',
              borderRadius: 'var(--radius-md)', padding: 'var(--space-3) var(--space-4)' }}>
              <p style={{ color: 'var(--gold-bright)', fontSize: 'var(--text-sm)', fontWeight: 600, marginBottom: 4 }}>
                Facing {selected?.label}
              </p>
              <p style={{ color: 'var(--text-muted)', fontSize: 'var(--text-xs)', lineHeight: 1.6 }}>
                {orientationHint(value)}
              </p>
            </div>
          ) : (
            <div style={{ border: '1px dashed var(--border-subtle)', borderRadius: 'var(--radius-md)',
              padding: 'var(--space-3) var(--space-4)' }}>
              <p style={{ color: 'var(--text-muted)', fontSize: 'var(--text-xs)', lineHeight: 1.6 }}>
                Orientation helps the AI determine which walls face which cardinal directions — essential for accurate bagua mapping.
              </p>
            </div>
          )}

          {/* Quick direction buttons for mobile convenience */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)', marginTop: 'var(--space-4)' }}>
            {DIRECTIONS.map(dir => (
              <button key={dir.id} onClick={() => onChange(dir.id)} style={{
                background: value === dir.id ? 'var(--gold-bright)' : 'var(--bg-raised)',
                color: value === dir.id ? 'var(--ink-900)' : 'var(--text-muted)',
                border: `1px solid ${value === dir.id ? 'var(--gold-bright)' : 'var(--border-subtle)'}`,
                borderRadius: 'var(--radius-sm)', padding: '4px 10px', cursor: 'pointer',
                fontSize: 'var(--text-xs)', fontFamily: 'var(--font-body)', fontWeight: value === dir.id ? 700 : 400,
                transition: 'all var(--duration-fast)',
              }}>
                {dir.id}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// Contextual hint per direction
function orientationHint(dir) {
  const hints = {
    N:  'The wall behind you faces South. Good for rooms that need strong yang energy.',
    NE: 'The wall behind you faces Southwest — the Earth direction in Feng Shui.',
    E:  'The wall behind you faces West. Morning light enters from the front — Wood energy.',
    SE: 'The wall behind you faces Northwest — strong Metal energy behind the room.',
    S:  'The wall behind you faces North. Water energy enters from the back — great for career.',
    SW: 'The wall behind you faces Northeast — the Knowledge and Wisdom direction.',
    W:  'The wall behind you faces East. Afternoon light enters — Metal energy.',
    NW: 'The wall behind you faces Southeast — the Wealth corner is in front of you.',
  };
  return hints[dir] || '';
}
