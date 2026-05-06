// LayoutEditor.jsx — Edit mode toolbar: rotate, remove, add furniture
import React, { useState } from 'react';
import Button from '../ui/Button';
import { FURNITURE_TYPES, FURNITURE_CATEGORIES, FURNITURE_BY_ID } from '../../constants/furnitureTypes';

export default function LayoutEditor({
  selectedFurnitureId,
  onRotate,
  onRemove,
  onAdd,
  editMode,
  onToggleEdit,
}) {
  const [addPanelOpen, setAddPanelOpen] = useState(false);
  const [activeCategory, setActiveCategory] = useState('Seating');
  const selectedDef = selectedFurnitureId ? FURNITURE_BY_ID[selectedFurnitureId.split('_').slice(0,-1).join('_')] : null;

  const categories = [...new Set(FURNITURE_TYPES.map(f=>f.category))];
  const filteredFurniture = FURNITURE_TYPES.filter(f=>f.category===activeCategory);

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:'var(--space-4)' }}>
      {/* Edit toggle */}
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between' }}>
        <div>
          <p style={{ color:'var(--text-muted)', fontSize:'var(--text-xs)', letterSpacing:'0.12em', textTransform:'uppercase' }}>Layout Editor</p>
          <p style={{ color:'var(--text-secondary)', fontSize:'var(--text-sm)', marginTop:2 }}>
            {editMode ? 'Click a piece to select, then click the room to move it' : 'Enable to rearrange furniture'}
          </p>
        </div>
        <Button variant={editMode?'primary':'secondary'} size="sm" onClick={onToggleEdit}>
          {editMode ? '✓ Editing' : '✎ Edit'}
        </Button>
      </div>

      {/* Selected furniture controls */}
      {editMode && selectedFurnitureId && (
        <div style={{ background:'var(--bg-raised)', borderRadius:'var(--radius-md)', padding:'var(--space-4)',
          border:'1px solid var(--border-default)', display:'flex', flexDirection:'column', gap:'var(--space-3)' }}>
          <p style={{ color:'var(--gold-bright)', fontSize:'var(--text-sm)', fontWeight:500 }}>
            Selected: {selectedDef?.label || selectedFurnitureId}
          </p>
          <div style={{ display:'flex', gap:'var(--space-2)' }}>
            <Button variant="ghost" size="sm" onClick={()=>onRotate(selectedFurnitureId)}>⟳ Rotate 90°</Button>
            <Button variant="danger" size="sm" onClick={()=>onRemove(selectedFurnitureId)}>✕ Remove</Button>
          </div>
        </div>
      )}

      {/* Add furniture */}
      {editMode && (
        <div>
          <Button variant="secondary" size="sm" fullWidth onClick={()=>setAddPanelOpen(p=>!p)}>
            {addPanelOpen ? '▲ Close' : '+ Add Furniture'}
          </Button>
          {addPanelOpen && (
            <div style={{ marginTop:'var(--space-3)', background:'var(--bg-raised)', borderRadius:'var(--radius-md)',
              border:'1px solid var(--border-subtle)', padding:'var(--space-4)' }}>
              {/* Category tabs */}
              <div style={{ display:'flex', flexWrap:'wrap', gap:'var(--space-2)', marginBottom:'var(--space-4)' }}>
                {categories.map(cat=>(
                  <button key={cat} onClick={()=>setActiveCategory(cat)} style={{
                    background: activeCategory===cat?'var(--gold-glow)':'none',
                    border:`1px solid ${activeCategory===cat?'var(--border-strong)':'var(--border-subtle)'}`,
                    borderRadius:'var(--radius-sm)', padding:'3px 10px', cursor:'pointer',
                    color: activeCategory===cat?'var(--gold-bright)':'var(--text-muted)',
                    fontSize:'var(--text-xs)', fontFamily:'var(--font-body)', transition:'all var(--duration-fast)',
                  }}>{cat}</button>
                ))}
              </div>
              {/* Items grid */}
              <div style={{ display:'grid', gridTemplateColumns:'repeat(2, 1fr)', gap:'var(--space-2)' }}>
                {filteredFurniture.map(item=>(
                  <button key={item.id} onClick={()=>{ onAdd(item); setAddPanelOpen(false); }} style={{
                    background:'var(--bg-surface)', border:'1px solid var(--border-subtle)',
                    borderRadius:'var(--radius-sm)', padding:'var(--space-2) var(--space-3)', cursor:'pointer',
                    color:'var(--text-secondary)', fontSize:'var(--text-xs)', fontFamily:'var(--font-body)',
                    textAlign:'left', transition:'all var(--duration-fast)',
                    display:'flex', alignItems:'center', gap:'var(--space-2)',
                  }}
                    onMouseEnter={e=>{e.currentTarget.style.borderColor='var(--border-default)';e.currentTarget.style.color='var(--text-primary)';}}
                    onMouseLeave={e=>{e.currentTarget.style.borderColor='var(--border-subtle)';e.currentTarget.style.color='var(--text-secondary)';}}>
                    <span style={{ width:10, height:10, borderRadius:2, background:item.color, flexShrink:0, display:'inline-block' }}/>
                    {item.label}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
