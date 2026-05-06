// ─────────────────────────────────────────────
// useLayoutEditor.js
// Manages selected layout + furniture click-to-move editing.
// ─────────────────────────────────────────────

import { useState, useCallback } from 'react';
import { GRID_UNIT } from '../constants/furnitureTypes';

export function useLayoutEditor(initialLayouts = []) {
  const [layouts, setLayouts]               = useState(initialLayouts);
  const [selectedLayoutId, setSelectedLayoutId] = useState(null);
  const [selectedFurnitureId, setSelectedFurnitureId] = useState(null);
  const [editMode, setEditMode]             = useState(false);

  // Derive the active layout object
  const activeLayout = layouts.find(l => l.id === selectedLayoutId) ?? layouts[0] ?? null;

  // ── Select a layout from the alternatives panel ──
  const selectLayout = useCallback((layoutId) => {
    setSelectedLayoutId(layoutId);
    setSelectedFurnitureId(null);
  }, []);

  // ── Initialize layouts from AI response ──
  const initLayouts = useCallback((newLayouts) => {
    setLayouts(newLayouts);
    setSelectedLayoutId(newLayouts[0]?.id ?? null);
    setSelectedFurnitureId(null);
  }, []);

  // ── Select / deselect a furniture item ──
  const selectFurniture = useCallback((furnitureId) => {
    setSelectedFurnitureId(prev => (prev === furnitureId ? null : furnitureId));
  }, []);

  // ── Move selected furniture by delta grid units ──
  const moveFurniture = useCallback((furnitureId, dx, dy) => {
    setLayouts(prev => prev.map(layout => {
      if (layout.id !== selectedLayoutId) return layout;
      return {
        ...layout,
        furniture: layout.furniture.map(item => {
          if (item.id !== furnitureId) return item;
          return { ...item, x: Math.max(0, item.x + dx), y: Math.max(0, item.y + dy) };
        }),
      };
    }));
  }, [selectedLayoutId]);

  // ── Move furniture to absolute position (from canvas click) ──
  const placeFurniture = useCallback((furnitureId, x, y) => {
    setLayouts(prev => prev.map(layout => {
      if (layout.id !== selectedLayoutId) return layout;
      return {
        ...layout,
        furniture: layout.furniture.map(item => {
          if (item.id !== furnitureId) return item;
          return { ...item, x: Math.max(0, x), y: Math.max(0, y) };
        }),
      };
    }));
  }, [selectedLayoutId]);

  // ── Rotate selected furniture 90° ──
  const rotateFurniture = useCallback((furnitureId) => {
    setLayouts(prev => prev.map(layout => {
      if (layout.id !== selectedLayoutId) return layout;
      return {
        ...layout,
        furniture: layout.furniture.map(item => {
          if (item.id !== furnitureId) return item;
          const newRotation = ((item.rotation || 0) + 90) % 360;
          // swap w/h on 90/270
          const swapDims = newRotation % 180 !== 0;
          return {
            ...item,
            rotation: newRotation,
            w: swapDims ? item.h : item.w,
            h: swapDims ? item.w : item.h,
          };
        }),
      };
    }));
  }, [selectedLayoutId]);

  // ── Remove furniture item ──
  const removeFurniture = useCallback((furnitureId) => {
    setLayouts(prev => prev.map(layout => {
      if (layout.id !== selectedLayoutId) return layout;
      return { ...layout, furniture: layout.furniture.filter(f => f.id !== furnitureId) };
    }));
    setSelectedFurnitureId(null);
  }, [selectedLayoutId]);

  // ── Add a new furniture item ──
  const addFurniture = useCallback((furnitureType) => {
    const newItem = {
      id:       `${furnitureType.id}_${Date.now()}`,
      type:     furnitureType.id,
      label:    furnitureType.label,
      x:        2,
      y:        2,
      w:        furnitureType.w,
      h:        furnitureType.h,
      rotation: 0,
    };
    setLayouts(prev => prev.map(layout => {
      if (layout.id !== selectedLayoutId) return layout;
      return { ...layout, furniture: [...layout.furniture, newItem] };
    }));
    setSelectedFurnitureId(newItem.id);
  }, [selectedLayoutId]);

  return {
    layouts,
    activeLayout,
    selectedLayoutId,
    selectedFurnitureId,
    editMode,
    setEditMode,
    selectLayout,
    initLayouts,
    selectFurniture,
    moveFurniture,
    placeFurniture,
    rotateFurniture,
    removeFurniture,
    addFurniture,
  };
}
