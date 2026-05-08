// ─────────────────────────────────────────────
// RoomCanvas.jsx — Battleship-style tile grid
// Features:
//   • Grid size derived from actual room dimensions
//   • Hover tile highlighting (like battleship)
//   • Furniture grab + ghost preview while hovering
//   • Only valid "room" tiles accept furniture
//   • Click to place, click furniture to pick up
// ─────────────────────────────────────────────
import React, { useRef, useState, useCallback, useMemo, useEffect } from 'react';
import { GRID_UNIT, FURNITURE_BY_ID } from '../../constants/furnitureTypes';

// ── Cell visual styles ──────────────────────
const CELL_BASE = {
  room:   { fill:'#2a2a3a', stroke:'rgba(212,168,75,0.10)', hoverFill:'rgba(212,168,75,0.18)' },
  void:   { fill:'transparent', stroke:'none', hoverFill:'transparent' },
  wall:   { fill:'#18182a', stroke:'rgba(100,100,180,0.25)', hoverFill:'#18182a' },
  door:   { fill:'#2a1808', stroke:'rgba(212,140,60,0.45)', hoverFill:'#3a2010' },
  window: { fill:'#08182a', stroke:'rgba(80,160,220,0.45)', hoverFill:'#102030' },
};

// ── Padding around the room ─────────────────
const PAD = 1;

// ── Grid size: 1 cell = 0.2 real-world units ─
const CELLS_PER_UNIT = 5;

function buildRectGrid(cols, rows) {
  return Array.from({ length: rows }, () => Array(cols).fill('room'));
}

function normalizeGrid(roomGrid, cols, rows) {
  if (!Array.isArray(roomGrid) || roomGrid.length === 0) return buildRectGrid(cols, rows);
  const valid = new Set(['room','void','wall','door','window']);
  return Array.from({ length: rows }, (_, r) =>
    Array.from({ length: cols }, (_, c) => {
      const v = roomGrid[r]?.[c];
      return valid.has(v) ? v : 'room';
    })
  );
}

// Get all cells a furniture item would occupy
function getFootprint(item) {
  const cells = [];
  for (let dy = 0; dy < item.h; dy++)
    for (let dx = 0; dx < item.w; dx++)
      cells.push({ c: item.x + dx, r: item.y + dy });
  return cells;
}

// Check if placing item at (gx, gy) is valid
function isPlacementValid(grid, item, gx, gy, rows, cols, dragId) {
  for (let dy = 0; dy < item.h; dy++) {
    for (let dx = 0; dx < item.w; dx++) {
      const c = gx + dx, r = gy + dy;
      if (r < 0 || r >= rows || c < 0 || c >= cols) return false;
      if ((grid[r]?.[c] ?? 'void') !== 'room') return false;
    }
  }
  return true;
}

export default function RoomCanvas({
  roomWidth = 4,
  roomHeight = 4,
  roomGrid: rawGrid,
  furniture = [],
  selectedId,
  onSelectFurniture,
  onPlaceFurniture,
  editMode = false,
}) {
  const containerRef = useRef(null);
  const [containerW, setContainerW] = useState(600);
  const [hoveredCell, setHoveredCell] = useState(null); // {c, r}
  const [ghostCell,   setGhostCell]   = useState(null); // {c, r} — where dragged item would land
  const [dragging,    setDragging]    = useState(false); // mouse held down on furniture

  // ── Dynamic cell size based on container width ──
  const cols = Math.round(roomWidth  * CELLS_PER_UNIT);
  const rows = Math.round(roomHeight * CELLS_PER_UNIT);

  // Measure container, recalc on resize
  useEffect(() => {
    if (!containerRef.current) return;
    const obs = new ResizeObserver(entries => {
      setContainerW(entries[0].contentRect.width || 600);
    });
    obs.observe(containerRef.current);
    return () => obs.disconnect();
  }, []);

  // Cell size: fit the grid inside container with padding
  const cellSize = Math.max(
    8,
    Math.min(28, Math.floor((containerW - PAD * 2 * 8) / (cols + PAD * 2)))
  );

  const totalW = (cols + PAD * 2) * cellSize;
  const totalH = (rows + PAD * 2) * cellSize;
  const offX   = PAD * cellSize;
  const offY   = PAD * cellSize;

  const grid = useMemo(() => normalizeGrid(rawGrid, cols, rows), [rawGrid, cols, rows]);

  // ── Get the selected furniture def ──
  const selectedItem = selectedId
    ? furniture.find(f => f.id === selectedId)
    : null;
  const selectedDef = selectedItem
    ? (FURNITURE_BY_ID[selectedItem.type] || { w: selectedItem.w, h: selectedItem.h })
    : null;

  // ── SVG coordinate → grid cell ──
  const svgToGrid = useCallback((clientX, clientY) => {
    if (!containerRef.current) return null;
    const rect = containerRef.current.querySelector('svg')?.getBoundingClientRect();
    if (!rect) return null;
    const scaleX = totalW / rect.width;
    const scaleY = totalH / rect.height;
    const svgX = (clientX - rect.left)  * scaleX;
    const svgY = (clientY - rect.top)   * scaleY;
    const c = Math.floor((svgX - offX) / cellSize);
    const r = Math.floor((svgY - offY) / cellSize);
    return { c, r };
  }, [totalW, totalH, offX, offY, cellSize]);

  // ── Mouse events ──
  const handleMouseMove = useCallback((e) => {
    const cell = svgToGrid(e.clientX, e.clientY);
    setHoveredCell(cell && cell.c >= 0 && cell.r >= 0 && cell.c < cols && cell.r < rows ? cell : null);
    if (editMode && selectedId && cell) setGhostCell(cell);
  }, [svgToGrid, editMode, selectedId, cols, rows]);

  const handleMouseLeave = useCallback(() => {
    setHoveredCell(null);
    setGhostCell(null);
  }, []);

  const handleClick = useCallback((e) => {
    if (!editMode || !selectedId || !ghostCell) return;
    if (!selectedItem) return;
    const valid = isPlacementValid(grid, selectedItem, ghostCell.c, ghostCell.r, rows, cols, selectedId);
    if (valid) {
      onPlaceFurniture?.(selectedId, ghostCell.c, ghostCell.r);
    }
  }, [editMode, selectedId, ghostCell, selectedItem, grid, rows, cols, onPlaceFurniture]);

  // ── Ghost footprint: cells the dragged item would occupy ──
  const ghostFootprint = useMemo(() => {
    if (!editMode || !selectedId || !ghostCell || !selectedItem) return new Set();
    const cells = new Set();
    for (let dy = 0; dy < selectedItem.h; dy++)
      for (let dx = 0; dx < selectedItem.w; dx++)
        cells.add(`${ghostCell.r + dy}-${ghostCell.c + dx}`);
    return cells;
  }, [editMode, selectedId, ghostCell, selectedItem]);

  const ghostValid = selectedItem && ghostCell
    ? isPlacementValid(grid, selectedItem, ghostCell.c, ghostCell.r, rows, cols, selectedId)
    : false;

  // ── Furniture footprint sets (for highlighting occupied cells) ──
  const occupiedCells = useMemo(() => {
    const map = {};
    furniture.forEach(item => {
      getFootprint(item).forEach(({ c, r }) => {
        map[`${r}-${c}`] = item.id;
      });
    });
    return map;
  }, [furniture]);

  // ── Legend ──
  const legendItems = [
    { type:'room',   label:'Floor'  },
    { type:'wall',   label:'Wall'   },
    { type:'door',   label:'Door'   },
    { type:'window', label:'Window' },
  ];

  // ── Compass ──
  const compass = [
    { label:'N', x: offX + (cols*cellSize)/2, y: offY - cellSize*0.7 },
    { label:'S', x: offX + (cols*cellSize)/2, y: offY + rows*cellSize + cellSize*0.8 },
    { label:'E', x: offX + cols*cellSize + cellSize*0.8, y: offY + (rows*cellSize)/2 },
    { label:'W', x: offX - cellSize*0.7,                 y: offY + (rows*cellSize)/2 },
  ];

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:'var(--space-3)' }}>
      <div ref={containerRef} style={{ width:'100%', overflowX:'auto' }}>
        <svg
          width={totalW} height={totalH}
          viewBox={`0 0 ${totalW} ${totalH}`}
          style={{
            display:'block',
            width:'100%', maxWidth:totalW,
            cursor: editMode && selectedId
              ? (ghostCell ? (ghostValid ? 'cell' : 'not-allowed') : 'crosshair')
              : 'default',
            userSelect:'none',
          }}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          onClick={handleClick}
        >
          {/* Background */}
          <rect width={totalW} height={totalH} fill="var(--bg-raised)"/>

          {/* ── Tile layer ── */}
          {grid.map((row, r) => row.map((cellType, c) => {
            const base    = CELL_BASE[cellType] || CELL_BASE.room;
            const key     = `${r}-${c}`;
            const isHov   = hoveredCell?.c === c && hoveredCell?.r === r;
            const isGhost = ghostFootprint.has(key);
            const isFurni = !!occupiedCells[key];
            const isVoid  = cellType === 'void';

            let fill = base.fill;
            if (!isVoid) {
              if (isGhost) fill = ghostValid ? 'rgba(212,168,75,0.30)' : 'rgba(192,57,43,0.30)';
              else if (isHov && !isFurni) fill = base.hoverFill;
            }

            const px = offX + c * cellSize;
            const py = offY + r * cellSize;

            return (
              <g key={key}>
                <rect x={px} y={py} width={cellSize} height={cellSize}
                  fill={fill} stroke={base.stroke} strokeWidth={0.5}
                  opacity={isVoid ? 0 : 1}/>
                {/* Ghost border */}
                {isGhost && !isVoid && (
                  <rect x={px+1} y={py+1} width={cellSize-2} height={cellSize-2}
                    fill="none"
                    stroke={ghostValid ? 'rgba(212,168,75,0.7)' : 'rgba(192,57,43,0.7)'}
                    strokeWidth={1} strokeDasharray="3 2"/>
                )}
              </g>
            );
          }))}

          {/* ── Grid coordinate labels (every 5 cells = 1m) ── */}
          {Array.from({ length: Math.ceil(cols / 5) + 1 }, (_, i) => i * 5).filter(c => c <= cols).map(c => (
            <text key={`cx${c}`}
              x={offX + c * cellSize} y={offY - 2}
              textAnchor="middle" dominantBaseline="auto"
              style={{ fontSize: Math.max(6, cellSize * 0.45), fontFamily:'var(--font-body)', fill:'rgba(212,168,75,0.3)' }}>
              {c/5}
            </text>
          ))}
          {Array.from({ length: Math.ceil(rows / 5) + 1 }, (_, i) => i * 5).filter(r => r <= rows).map(r => (
            <text key={`ry${r}`}
              x={offX - 2} y={offY + r * cellSize}
              textAnchor="end" dominantBaseline="middle"
              style={{ fontSize: Math.max(6, cellSize * 0.45), fontFamily:'var(--font-body)', fill:'rgba(212,168,75,0.3)' }}>
              {r/5}
            </text>
          ))}

          {/* Compass */}
          {compass.map(cp => (
            <text key={cp.label} x={cp.x} y={cp.y} textAnchor="middle" dominantBaseline="middle"
              style={{ fontSize: Math.max(8, cellSize * 0.6), fontFamily:'var(--font-body)',
                fill:'rgba(212,168,75,0.4)', fontWeight:600 }}>
              {cp.label}
            </text>
          ))}

          {/* ── Furniture layer ── */}
          <g>
            {furniture.map(item => {
              const def       = FURNITURE_BY_ID[item.type] || {};
              const isSelected = item.id === selectedId;
              const px = offX + item.x * cellSize;
              const py = offY + item.y * cellSize;
              const fw = item.w * cellSize;
              const fh = item.h * cellSize;
              const cx = px + fw / 2;
              const cy = py + fh / 2;
              const color = def.color || '#556';
              // When this piece is being dragged (selected + ghost active), fade it
              const isBeingMoved = isSelected && editMode && ghostCell;

              return (
                <g key={item.id}
                  transform={item.rotation ? `rotate(${item.rotation},${cx},${cy})` : undefined}
                  onClick={e => { e.stopPropagation(); if (editMode) onSelectFurniture?.(item.id); }}
                  style={{ cursor: editMode ? 'grab' : 'default' }}>
                  {/* Drop shadow */}
                  <rect x={px+2} y={py+2} width={fw} height={fh} rx={2} fill="rgba(0,0,0,0.4)"/>
                  {/* Body */}
                  <rect x={px} y={py} width={fw} height={fh} rx={2}
                    fill={color}
                    opacity={isBeingMoved ? 0.35 : 1}
                    stroke={isSelected ? '#d4a84b' : 'rgba(255,255,255,0.10)'}
                    strokeWidth={isSelected ? 2 : 0.75}/>
                  {/* Top sheen */}
                  {!isBeingMoved && (
                    <rect x={px+1} y={py+1} width={fw-2} height={Math.min(fh*0.25,6)} rx={1}
                      fill="rgba(255,255,255,0.09)"/>
                  )}
                  {/* Label */}
                  {fw > 24 && fh > 14 && !isBeingMoved && (
                    <text x={cx} y={cy} textAnchor="middle" dominantBaseline="middle"
                      style={{ fontSize:Math.min(10, fw/5, fh/2),
                        fontFamily:'var(--font-body)', fill:'rgba(255,255,255,0.8)',
                        pointerEvents:'none', userSelect:'none' }}>
                      {item.label || def.label || item.type}
                    </text>
                  )}
                  {/* Selected dashed outline */}
                  {isSelected && (
                    <rect x={px-2} y={py-2} width={fw+4} height={fh+4} rx={4}
                      fill="none" stroke="#d4a84b" strokeWidth={1.5}
                      strokeDasharray="4 3" opacity={0.8}/>
                  )}
                </g>
              );
            })}
          </g>

          {/* ── Ghost preview of item being placed ── */}
          {editMode && selectedId && ghostCell && selectedItem && (() => {
            const def = FURNITURE_BY_ID[selectedItem.type] || {};
            const px  = offX + ghostCell.c * cellSize;
            const py  = offY + ghostCell.r * cellSize;
            const fw  = selectedItem.w * cellSize;
            const fh  = selectedItem.h * cellSize;
            const color = ghostValid ? 'rgba(212,168,75,0.5)' : 'rgba(192,57,43,0.5)';
            const borderColor = ghostValid ? '#d4a84b' : '#c0392b';
            return (
              <g pointerEvents="none">
                <rect x={px} y={py} width={fw} height={fh} rx={2}
                  fill={color} stroke={borderColor} strokeWidth={1.5} strokeDasharray="5 3"/>
                {fw > 24 && fh > 14 && (
                  <text x={px+fw/2} y={py+fh/2} textAnchor="middle" dominantBaseline="middle"
                    style={{ fontSize:Math.min(10,fw/5,fh/2), fontFamily:'var(--font-body)',
                      fill: ghostValid ? '#d4a84b' : '#c0392b', fontWeight:600 }}>
                    {selectedItem.label || def.label}
                  </text>
                )}
              </g>
            );
          })()}

          {/* Status hint bar */}
          {editMode && (
            <text x={totalW/2} y={totalH - 4} textAnchor="middle"
              style={{ fontSize: Math.max(8, cellSize*0.5), fontFamily:'var(--font-body)',
                fill: selectedId ? (ghostValid ? 'rgba(212,168,75,0.7)' : 'rgba(192,57,43,0.6)') : 'rgba(255,255,255,0.2)' }}>
              {selectedId
                ? ghostValid
                  ? `Click to place ${selectedItem?.label || ''}`
                  : 'Invalid position — floor tiles only'
                : 'Click a piece to select it'}
            </text>
          )}
        </svg>
      </div>

      {/* Legend + grid info */}
      <div style={{ display:'flex', gap:'var(--space-4)', flexWrap:'wrap',
        alignItems:'center', paddingLeft:'var(--space-1)' }}>
        {legendItems.map(({ type, label }) => {
          const s = CELL_BASE[type];
          return (
            <div key={type} style={{ display:'flex', alignItems:'center', gap:5 }}>
              <div style={{ width:11, height:11, borderRadius:2,
                background: s.fill === 'transparent' ? 'transparent' : s.fill,
                border:`1px solid ${s.stroke === 'none' ? 'var(--border-subtle)' : s.stroke}` }}/>
              <span style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)' }}>{label}</span>
            </div>
          );
        })}
        <span style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)', marginLeft:'auto' }}>
          {cols} × {rows} cells · 1 cell = 0.2m · room {roomWidth}×{roomHeight}m
        </span>
      </div>
    </div>
  );
}
