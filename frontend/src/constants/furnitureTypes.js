// ─────────────────────────────────────────────
// Furniture Types Catalog
// Each item has: id, label, category, defaultW, defaultH (in grid units), color, icon (SVG path hint)
// Grid units: 1 unit = 20px on canvas at 100% zoom
// ─────────────────────────────────────────────

export const FURNITURE_CATEGORIES = {
  SEATING:   'Seating',
  TABLES:    'Tables',
  STORAGE:   'Storage',
  BEDS:      'Beds',
  DECOR:     'Decor',
  FIXTURES:  'Fixtures',
};

export const FURNITURE_TYPES = [
  // ── Seating ──
  { id: 'sofa_3',      label: 'Sofa (3-seat)',    category: 'Seating',  w: 9,  h: 4,  color: '#5a6a7a' },
  { id: 'sofa_2',      label: 'Sofa (2-seat)',    category: 'Seating',  w: 7,  h: 4,  color: '#5a6a7a' },
  { id: 'armchair',    label: 'Armchair',         category: 'Seating',  w: 4,  h: 4,  color: '#6a7a5a' },
  { id: 'chair',       label: 'Chair',            category: 'Seating',  w: 3,  h: 3,  color: '#7a6a5a' },
  // ── Tables ──
  { id: 'coffee_table',label: 'Coffee Table',     category: 'Tables',   w: 6,  h: 3,  color: '#8b6914' },
  { id: 'dining_table',label: 'Dining Table',     category: 'Tables',   w: 8,  h: 5,  color: '#8b6914' },
  { id: 'desk',        label: 'Desk',             category: 'Tables',   w: 7,  h: 4,  color: '#7a5a3a' },
  { id: 'side_table',  label: 'Side Table',       category: 'Tables',   w: 3,  h: 3,  color: '#8b6914' },
  // ── Storage ──
  { id: 'bookshelf',   label: 'Bookshelf',        category: 'Storage',  w: 5,  h: 2,  color: '#5a4a3a' },
  { id: 'wardrobe',    label: 'Wardrobe',         category: 'Storage',  w: 6,  h: 3,  color: '#4a3a2a' },
  { id: 'cabinet',     label: 'Cabinet',          category: 'Storage',  w: 4,  h: 2,  color: '#5a4a3a' },
  { id: 'tv_unit',     label: 'TV Unit',          category: 'Storage',  w: 8,  h: 2,  color: '#3a3a4a' },
  // ── Beds ──
  { id: 'bed_king',    label: 'King Bed',         category: 'Beds',     w: 10, h: 11, color: '#4a5a6a' },
  { id: 'bed_queen',   label: 'Queen Bed',        category: 'Beds',     w: 8,  h: 10, color: '#4a5a6a' },
  { id: 'bed_single',  label: 'Single Bed',       category: 'Beds',     w: 5,  h: 10, color: '#4a5a6a' },
  { id: 'nightstand',  label: 'Nightstand',       category: 'Beds',     w: 3,  h: 3,  color: '#5a4a3a' },
  // ── Decor ──
  { id: 'plant_lg',    label: 'Plant (Large)',    category: 'Decor',    w: 3,  h: 3,  color: '#3a5a3a' },
  { id: 'plant_sm',    label: 'Plant (Small)',    category: 'Decor',    w: 2,  h: 2,  color: '#4a6a4a' },
  { id: 'rug',         label: 'Rug',             category: 'Decor',    w: 10, h: 7,  color: '#6a4a3a' },
  { id: 'lamp_floor',  label: 'Floor Lamp',       category: 'Decor',    w: 2,  h: 2,  color: '#8a7a4a' },
  // ── Fixtures ──
  { id: 'door',        label: 'Door',            category: 'Fixtures', w: 4,  h: 1,  color: '#3a3a5a' },
  { id: 'window',      label: 'Window',          category: 'Fixtures', w: 4,  h: 1,  color: '#4a6a8a' },
];

export const FURNITURE_BY_ID = Object.fromEntries(
  FURNITURE_TYPES.map(f => [f.id, f])
);

export const GRID_UNIT = 20; // px per grid unit at 100% zoom

// Feng Shui element mapping
export const ELEMENT_AFFINITY = {
  bed_king:    'earth',
  bed_queen:   'earth',
  bed_single:  'earth',
  plant_lg:    'wood',
  plant_sm:    'wood',
  bookshelf:   'wood',
  lamp_floor:  'fire',
  tv_unit:     'fire',
  desk:        'water',
  wardrobe:    'metal',
  cabinet:     'metal',
  sofa_3:      'earth',
  sofa_2:      'earth',
  armchair:    'earth',
};
