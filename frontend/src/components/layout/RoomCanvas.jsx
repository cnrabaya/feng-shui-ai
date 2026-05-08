// ─────────────────────────────────────────────
// RoomCanvas.jsx
// Tile-based 2D grid renderer.
// Only "room" tiles are active — void tiles are transparent,
// naturally rendering L-shapes, alcoves, and irregular rooms.
// ─────────────────────────────────────────────
import React, { useRef, useCallback, useMemo } from 'react';
import FurnitureItem from './FurnitureItem';
import { GRID_UNIT } from '../../constants/furnitureTypes';

// Cell type → visual style
const CELL_STYLES = {
  room:    { fill: 'var(--bg-overlay)',   stroke: 'rgba(212,168,75,0.07)', opacity: 1 },
  void:    { fill: 'transparent',         stroke: 'none',                  opacity: 0 },
  wall:    { fill: '#1a1a2a',             stroke: 'rgba(100,100,150,0.3)', opacity: 1 },
  door:    { fill: '#2a1a0a',             stroke: 'rgba(212,140,60,0.4)',  opacity: 1 },
  window:  { fill: '#0a1a2a',             stroke: 'rgba(100,180,220,0.4)', opacity: 1 },
};

const CELL_ICONS = { door: '▭', window: '▭' };
const PAD = 2; // grid units padding around the room

// Build a fallback rectangular grid if AI didn't return one
function buildRectGrid(cols, rows) {
  return Array.from({ length: rows }, () => Array(cols).fill('room'));
}

// Validate and normalize the roomGrid from AI
function normalizeGrid(roomGrid, cols, rows) {
  if (!Array.isArray(roomGrid) || roomGrid.length === 0) return buildRectGrid(cols, rows);
  const validTypes = new Set(['room', 'void', 'wall', 'door', 'window']);
  return Array.from({ length: rows }, (_, r) =>
    Array.from({ length: cols }, (_, c) => {
      const val = roomGrid[r]?.[c];
      return validTypes.has(val) ? val : 'room';
    })
  );
}

export default function RoomCanvas({
  roomWidth, roomHeight,
  roomGrid: rawGrid,
  furniture = [],
  selectedId,
  onSelectFurniture,
  onPlaceFurniture,
  editMode = false,
}) {
  const svgRef = useRef(null);

  const cols = Math.round(roomWidth  * 5);
  const rows = Math.round(roomHeight * 5);
  const grid = useMemo(() => normalizeGrid(rawGrid, cols, rows), [rawGrid, cols, rows]);

  const totalW = (cols + PAD * 2) * GRID_UNIT;
  const totalH = (rows + PAD * 2) * GRID_UNIT;
  const offsetX = PAD * GRID_UNIT;
  const offsetY = PAD * GRID_UNIT;

  // Click on canvas → move selected furniture
  const handleCanvasClick = useCallback((e) => {
    if (!editMode || !selectedId || !svgRef.current) return;
    const rect = svgRef.current.getBoundingClientRect();
    const scaleX = totalW / rect.width;
    const scaleY = totalH / rect.height;
    const svgX   = (e.clientX - rect.left)  * scaleX;
    const svgY   = (e.clientY - rect.top)   * scaleY;
    const gridX  = Math.round((svgX - offsetX) / GRID_UNIT);
    const gridY  = Math.round((svgY - offsetY) / GRID_UNIT);
    // Only allow placement on "room" tiles
    const cellType = grid[gridY]?.[gridX];
    if (cellType === 'room') {
      onPlaceFurniture?.(selectedId, Math.max(0, Math.min(gridX, cols - 1)), Math.max(0, Math.min(gridY, rows - 1)));
    }
  }, [editMode, selectedId, grid, cols, rows, offsetX, offsetY, totalW, totalH, onPlaceFurniture]);

  // Compass labels
  const compass = [
    { label: 'N', x: offsetX + (cols * GRID_UNIT) / 2, y: offsetY - 12 },
    { label: 'S', x: offsetX + (cols * GRID_UNIT) / 2, y: offsetY + rows * GRID_UNIT + 16 },
    { label: 'E', x: offsetX + cols * GRID_UNIT + 16,  y: offsetY + (rows * GRID_UNIT) / 2 },
    { label: 'W', x: offsetX - 12,                     y: offsetY + (rows * GRID_UNIT) / 2 },
  ];

  // Legend items
  const legendItems = [
    { type: 'room',   label: 'Floor' },
    { type: 'wall',   label: 'Wall'  },
    { type: 'door',   label: 'Door'  },
    { type: 'window', label: 'Window'},
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
      <div style={{ overflowX: 'auto', overflowY: 'auto' }}>
        <svg
          ref={svgRef}
          viewBox={`0 0 ${totalW} ${totalH}`}
          style={{
            display: 'block', width: '100%', maxWidth: totalW,
            cursor: editMode && selectedId ? 'crosshair' : 'default',
          }}
          onClick={handleCanvasClick}
        >
          {/* SVG background */}
          <rect width={totalW} height={totalH} fill="var(--bg-raised)"/>

          {/* Render tiles */}
          {grid.map((row, r) =>
            row.map((cellType, c) => {
              const style   = CELL_STYLES[cellType] || CELL_STYLES.room;
              const px      = offsetX + c * GRID_UNIT;
              const py      = offsetY + r * GRID_UNIT;
              const icon    = CELL_ICONS[cellType];
              return (
                <g key={`${r}-${c}`} opacity={style.opacity}>
                  <rect
                    x={px} y={py} width={GRID_UNIT} height={GRID_UNIT}
                    fill={style.fill} stroke={style.stroke} strokeWidth={0.5}
                  />
                  {icon && GRID_UNIT >= 16 && (
                    <text x={px + GRID_UNIT / 2} y={py + GRID_UNIT / 2}
                      textAnchor="middle" dominantBaseline="middle"
                      style={{ fontSize: 7, fill: style.stroke, pointerEvents: 'none', userSelect: 'none' }}>
                      {icon}
                    </text>
                  )}
                </g>
              );
            })
          )}

          {/* Compass labels */}
          {compass.map(c => (
            <text key={c.label} x={c.x} y={c.y} textAnchor="middle" dominantBaseline="middle"
              style={{ fontSize: 10, fontFamily: 'var(--font-body)', fill: 'rgba(212,168,75,0.4)', letterSpacing: '0.05em' }}>
              {c.label}
            </text>
          ))}

          {/* Furniture layer */}
          <g transform={`translate(${offsetX}, ${offsetY})`}>
            {furniture.map(item => (
              <FurnitureItem
                key={item.id} item={item}
                selected={selectedId === item.id}
                onClick={onSelectFurniture}
                editMode={editMode}
              />
            ))}
          </g>

          {/* Edit hint */}
          {editMode && selectedId && (
            <text x={totalW / 2} y={totalH - 8} textAnchor="middle"
              style={{ fontSize: 10, fontFamily: 'var(--font-body)', fill: 'rgba(212,168,75,0.55)' }}>
              Click a floor tile to place the selected item
            </text>
          )}
        </svg>
      </div>

      {/* Legend */}
      <div style={{ display: 'flex', gap: 'var(--space-4)', flexWrap: 'wrap', paddingLeft: 'var(--space-2)' }}>
        {legendItems.map(({ type, label }) => {
          const s = CELL_STYLES[type];
          return (
            <div key={type} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <div style={{
                width: 12, height: 12, borderRadius: 2,
                background: s.fill === 'transparent' ? 'transparent' : s.fill,
                border: `1px solid ${s.stroke === 'none' ? 'var(--border-subtle)' : s.stroke}`,
              }}/>
              <span style={{ color: 'var(--text-muted)', fontSize: 'var(--text-xs)' }}>{label}</span>
            </div>
          );
        })}
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginLeft: 'auto' }}>
          <span style={{ color: 'var(--text-muted)', fontSize: 'var(--text-xs)' }}>
            {cols} × {rows} grid · 1 cell = 0.2m
          </span>
        </div>
      </div>
    </div>
  );
}
