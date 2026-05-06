// RoomCanvas.jsx — 2D SVG room renderer with click-to-move furniture
import React, { useRef, useCallback } from 'react';
import FurnitureItem from './FurnitureItem';
import { GRID_UNIT } from '../../constants/furnitureTypes';

const GRID_COLOR = 'rgba(212,168,75,0.05)';
const ROOM_PAD   = 2; // grid units of padding around room

export default function RoomCanvas({
  roomWidth, roomHeight,         // in real-world units (m/ft)
  furniture = [],
  selectedId,
  onSelectFurniture,
  onPlaceFurniture,
  editMode = false,
  scale = 1,
}) {
  const svgRef = useRef(null);

  // Grid dims: 5 grid units per real-world unit
  const gridW = Math.round(roomWidth  * 5);
  const gridH = Math.round(roomHeight * 5);
  const totalW = (gridW + ROOM_PAD * 2) * GRID_UNIT;
  const totalH = (gridH + ROOM_PAD * 2) * GRID_UNIT;
  const roomX  = ROOM_PAD * GRID_UNIT;
  const roomY  = ROOM_PAD * GRID_UNIT;
  const roomPxW = gridW * GRID_UNIT;
  const roomPxH = gridH * GRID_UNIT;

  // When canvas is clicked while a furniture is selected → move it there
  const handleCanvasClick = useCallback((e) => {
    if (!editMode || !selectedId || !svgRef.current) return;
    const rect = svgRef.current.getBoundingClientRect();
    const svgX  = (e.clientX - rect.left) / scale;
    const svgY  = (e.clientY - rect.top)  / scale;
    const gridX = Math.round((svgX - roomX) / GRID_UNIT);
    const gridY = Math.round((svgY - roomY) / GRID_UNIT);
    onPlaceFurniture?.(selectedId, Math.max(0, Math.min(gridX, gridW)), Math.max(0, Math.min(gridY, gridH)));
  }, [editMode, selectedId, roomX, roomY, gridW, gridH, scale, onPlaceFurniture]);

  // Build grid lines
  const gridLines = [];
  for (let gx = 0; gx <= gridW; gx++) {
    gridLines.push(<line key={`vg${gx}`} x1={roomX+gx*GRID_UNIT} y1={roomY} x2={roomX+gx*GRID_UNIT} y2={roomY+roomPxH} stroke={GRID_COLOR} strokeWidth={0.5}/>);
  }
  for (let gy = 0; gy <= gridH; gy++) {
    gridLines.push(<line key={`hg${gy}`} x1={roomX} y1={roomY+gy*GRID_UNIT} x2={roomX+roomPxW} y2={roomY+gy*GRID_UNIT} stroke={GRID_COLOR} strokeWidth={0.5}/>);
  }

  // Compass rose positions (N top, E right, S bottom, W left)
  const compassItems = [
    { label:'N', x: roomX+roomPxW/2, y: roomY-12 },
    { label:'S', x: roomX+roomPxW/2, y: roomY+roomPxH+16 },
    { label:'E', x: roomX+roomPxW+16, y: roomY+roomPxH/2 },
    { label:'W', x: roomX-12, y: roomY+roomPxH/2 },
  ];

  return (
    <div style={{ overflowAuto:'auto', position:'relative' }}>
      <svg
        ref={svgRef}
        width={totalW * scale}
        height={totalH * scale}
        viewBox={`0 0 ${totalW} ${totalH}`}
        style={{ display:'block', cursor: editMode && selectedId ? 'crosshair' : 'default', maxWidth:'100%' }}
        onClick={handleCanvasClick}
      >
        {/* Background */}
        <rect width={totalW} height={totalH} fill="var(--bg-raised)"/>

        {/* Room floor */}
        <rect x={roomX} y={roomY} width={roomPxW} height={roomPxH}
          fill="var(--bg-overlay)" stroke="var(--border-default)" strokeWidth={1.5} rx={2}/>

        {/* Grid */}
        {gridLines}

        {/* Compass */}
        {compassItems.map(c=>(
          <text key={c.label} x={c.x} y={c.y} textAnchor="middle" dominantBaseline="middle"
            style={{fontSize:10,fontFamily:'var(--font-body)',fill:'rgba(212,168,75,0.4)',letterSpacing:'0.05em'}}>
            {c.label}
          </text>
        ))}

        {/* Dimension labels */}
        <text x={roomX+roomPxW/2} y={roomY+roomPxH+28} textAnchor="middle"
          style={{fontSize:10,fontFamily:'var(--font-body)',fill:'rgba(212,168,75,0.5)'}}>
          {roomWidth}
        </text>
        <text x={roomX+roomPxW+28} y={roomY+roomPxH/2} textAnchor="middle" dominantBaseline="middle"
          transform={`rotate(90, ${roomX+roomPxW+28}, ${roomY+roomPxH/2})`}
          style={{fontSize:10,fontFamily:'var(--font-body)',fill:'rgba(212,168,75,0.5)'}}>
          {roomHeight}
        </text>

        {/* Furniture — offset by room position */}
        <g transform={`translate(${roomX}, ${roomY})`}>
          {furniture.map(item=>(
            <FurnitureItem key={item.id} item={item} selected={selectedId===item.id}
              onClick={onSelectFurniture} editMode={editMode}/>
          ))}
        </g>

        {/* Edit mode hint */}
        {editMode && selectedId && (
          <text x={totalW/2} y={totalH-8} textAnchor="middle"
            style={{fontSize:10,fontFamily:'var(--font-body)',fill:'rgba(212,168,75,0.6)'}}>
            Click anywhere in the room to place selected item
          </text>
        )}
      </svg>
    </div>
  );
}
