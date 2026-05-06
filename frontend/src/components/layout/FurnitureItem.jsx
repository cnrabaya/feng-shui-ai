// FurnitureItem.jsx — Single furniture piece on the 2D canvas (SVG)
import React from 'react';
import { GRID_UNIT, FURNITURE_BY_ID } from '../../constants/furnitureTypes';

export default function FurnitureItem({ item, selected, onClick, editMode }) {
  const def = FURNITURE_BY_ID[item.type] || {};
  const x   = item.x * GRID_UNIT;
  const y   = item.y * GRID_UNIT;
  const w   = item.w * GRID_UNIT;
  const h   = item.h * GRID_UNIT;
  const cx  = x + w / 2;
  const cy  = y + h / 2;
  const rot = item.rotation || 0;
  const color = def.color || '#555';

  return (
    <g transform={`rotate(${rot}, ${cx}, ${cy})`} style={{cursor: editMode?'pointer':'default'}}
      onClick={e=>{e.stopPropagation(); if(editMode) onClick(item.id);}}>
      <rect x={x+3} y={y+3} width={w} height={h} rx={3} fill="rgba(0,0,0,0.35)"/>
      <rect x={x} y={y} width={w} height={h} rx={3} fill={color}
        stroke={selected?'#d4a84b':'rgba(255,255,255,0.12)'} strokeWidth={selected?2:1}/>
      <rect x={x+1} y={y+1} width={w-2} height={Math.min(h*0.3,8)} rx={2} fill="rgba(255,255,255,0.08)"/>
      {w>40 && h>20 && (
        <text x={cx} y={cy} textAnchor="middle" dominantBaseline="middle"
          style={{fontSize:Math.min(11,w/6),fontFamily:'var(--font-body)',fill:'rgba(255,255,255,0.75)',pointerEvents:'none',userSelect:'none'}}>
          {item.label||def.label||item.type}
        </text>
      )}
      {selected && <rect x={x-3} y={y-3} width={w+6} height={h+6} rx={5} fill="none" stroke="#d4a84b" strokeWidth={1.5} strokeDasharray="4 3" opacity={0.7}/>}
    </g>
  );
}
