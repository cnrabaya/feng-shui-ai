// ─────────────────────────────────────────────
// mockData.js
// Realistic fake AI response for UI testing.
// Used when USE_MOCK = true in App.jsx
// ─────────────────────────────────────────────

export const MOCK_ANALYSIS = {
  description:
    "A cozy living room with a south-facing window that lets in strong afternoon light. The space has a relaxed, lived-in quality with mismatched furniture placement that disrupts the natural flow of energy through the room.",
  style: "Modern Eclectic",
  existingFurniture: [
    { id: "sofa_main",    type: "sofa_3",      label: "Sofa",         x: 2,  y: 8,  w: 9,  h: 4,  rotation: 0 },
    { id: "tv_unit_main", type: "tv_unit",     label: "TV Unit",      x: 2,  y: 1,  w: 8,  h: 2,  rotation: 0 },
    { id: "coffee_main",  type: "coffee_table",label: "Coffee Table", x: 4,  y: 5,  w: 6,  h: 3,  rotation: 0 },
    { id: "plant_corner", type: "plant_lg",    label: "Plant",        x: 14, y: 1,  w: 3,  h: 3,  rotation: 0 },
    { id: "armchair_1",   type: "armchair",    label: "Armchair",     x: 13, y: 7,  w: 4,  h: 4,  rotation: 0 },
    { id: "bookshelf_1",  type: "bookshelf",   label: "Bookshelf",    x: 14, y: 13, w: 5,  h: 2,  rotation: 0 },
  ],
  fengShuiScore: {
    total: 58,
    breakdown: {
      qi_flow:          { score: 45, label: "Qi Flow",          note: "Sofa positioned with back to entry disrupts energy circulation." },
      balance:          { score: 62, label: "Balance",          note: "Left side of room is heavier than right, creating imbalance." },
      natural_light:    { score: 75, label: "Natural Light",    note: "Good southern exposure, but window is partially blocked by furniture." },
      clutter:          { score: 60, label: "Clutter",          note: "Some accumulation in corners — especially the northeast." },
      bagua_alignment:  { score: 48, label: "Bagua Alignment",  note: "Wealth corner (southeast) is largely empty and unactivated." },
    },
    dominant_element: "earth",
    missing_element:  "water",
    summary:
      "The room has a grounded, stable energy (Earth) but lacks the flowing, reflective quality of Water — making the space feel stagnant at times. Repositioning the sofa to face the entry and activating the southeast corner would significantly improve qi circulation.",
  },
  issues: [
    "Sofa back faces the main entry door — occupants will feel unsettled and ungrounded.",
    "TV unit directly faces the bed position — creates conflicting fire and water energy.",
    "Northeast corner accumulates stagnant qi due to clutter and blocked airflow.",
    "Wealth corner (southeast) is empty — missing an opportunity to activate prosperity energy.",
    "No water element present — the space lacks reflective, flowing energy.",
  ],
  recommendations: [
    "Rotate the sofa so occupants have a clear sightline to the room's entry — the 'command position'.",
    "Add a small water feature or mirror in the southeast corner to activate wealth energy.",
    "Introduce a dark blue or black accent piece to balance the missing Water element.",
    "Clear the northeast corner completely and add a rounded-leaf plant to soften the energy.",
    "Place a floor lamp in the Fame area (south) to strengthen recognition and visibility.",
  ],
};

export const MOCK_LAYOUTS = [
  {
    id: "layout_1",
    name: "Command & Flow",
    theme: "Sofa in command position, open qi pathways",
    fengShuiImprovement: 24,
    dominant_element: "wood",
    rationale:
      "The sofa is rotated to face the entry, placing occupants in the traditional 'command position.' Furniture is pulled away from walls to allow qi to circulate freely on all sides, addressing the primary energy blockages.",
    furniture: [
      { id: "sofa_main",    type: "sofa_3",       label: "Sofa",          x: 3,  y: 5,  w: 9,  h: 4,  rotation: 0 },
      { id: "tv_unit_main", type: "tv_unit",      label: "TV Unit",       x: 3,  y: 1,  w: 8,  h: 2,  rotation: 0 },
      { id: "coffee_main",  type: "coffee_table", label: "Coffee Table",  x: 5,  y: 10, w: 6,  h: 3,  rotation: 0 },
      { id: "plant_1",      type: "plant_lg",     label: "Plant",         x: 1,  y: 1,  w: 3,  h: 3,  rotation: 0 },
      { id: "plant_2",      type: "plant_sm",     label: "Plant",         x: 15, y: 12, w: 2,  h: 2,  rotation: 0 },
      { id: "armchair_1",   type: "armchair",     label: "Armchair",      x: 14, y: 5,  w: 4,  h: 4,  rotation: 0 },
      { id: "lamp_1",       type: "lamp_floor",   label: "Floor Lamp",    x: 13, y: 1,  w: 2,  h: 2,  rotation: 0 },
      { id: "bookshelf_1",  type: "bookshelf",    label: "Bookshelf",     x: 1,  y: 13, w: 5,  h: 2,  rotation: 0 },
    ],
  },
  {
    id: "layout_2",
    name: "Bagua Activation",
    theme: "Furniture aligned to the eight trigram zones",
    fengShuiImprovement: 31,
    dominant_element: "water",
    rationale:
      "Each furniture piece is placed to activate a specific bagua zone. The southeast (wealth) corner is anchored with the bookshelf and a plant. The north (career) zone holds the desk. This is the highest-scoring layout.",
    furniture: [
      { id: "sofa_main",    type: "sofa_3",       label: "Sofa",          x: 4,  y: 6,  w: 9,  h: 4,  rotation: 0 },
      { id: "tv_unit_main", type: "tv_unit",      label: "TV Unit",       x: 4,  y: 1,  w: 8,  h: 2,  rotation: 0 },
      { id: "coffee_main",  type: "coffee_table", label: "Coffee Table",  x: 6,  y: 11, w: 5,  h: 3,  rotation: 0 },
      { id: "bookshelf_se", type: "bookshelf",    label: "Bookshelf (SE)",x: 14, y: 13, w: 5,  h: 2,  rotation: 0 },
      { id: "plant_se",     type: "plant_lg",     label: "Plant (SE)",    x: 14, y: 10, w: 3,  h: 3,  rotation: 0 },
      { id: "armchair_1",   type: "armchair",     label: "Armchair",      x: 1,  y: 6,  w: 4,  h: 4,  rotation: 0 },
      { id: "lamp_south",   type: "lamp_floor",   label: "Lamp (South)",  x: 9,  y: 14, w: 2,  h: 2,  rotation: 0 },
      { id: "plant_east",   type: "plant_sm",     label: "Plant (East)",  x: 17, y: 6,  w: 2,  h: 2,  rotation: 0 },
    ],
  },
  {
    id: "layout_3",
    name: "Five Elements Balance",
    theme: "Each element represented and in harmony",
    fengShuiImprovement: 18,
    dominant_element: "earth",
    rationale:
      "A more conservative rearrangement that keeps the existing layout's character while introducing all five elements. A mirror (Water), candle holder (Fire), wooden side table (Wood), and stone ornament (Earth) complete the elemental cycle without radical changes.",
    furniture: [
      { id: "sofa_main",    type: "sofa_3",       label: "Sofa",          x: 2,  y: 7,  w: 9,  h: 4,  rotation: 0 },
      { id: "tv_unit_main", type: "tv_unit",      label: "TV Unit",       x: 2,  y: 1,  w: 8,  h: 2,  rotation: 0 },
      { id: "coffee_main",  type: "coffee_table", label: "Coffee Table",  x: 4,  y: 12, w: 6,  h: 3,  rotation: 0 },
      { id: "armchair_1",   type: "armchair",     label: "Armchair",      x: 14, y: 7,  w: 4,  h: 4,  rotation: 0 },
      { id: "plant_1",      type: "plant_lg",     label: "Plant (Wood)",  x: 1,  y: 1,  w: 3,  h: 3,  rotation: 0 },
      { id: "plant_2",      type: "plant_sm",     label: "Plant",         x: 16, y: 1,  w: 2,  h: 2,  rotation: 0 },
      { id: "bookshelf_1",  type: "bookshelf",    label: "Bookshelf",     x: 13, y: 13, w: 5,  h: 2,  rotation: 0 },
      { id: "lamp_1",       type: "lamp_floor",   label: "Lamp (Fire)",   x: 13, y: 1,  w: 2,  h: 2,  rotation: 0 },
      { id: "side_table_1", type: "side_table",   label: "Side Table",    x: 12, y: 7,  w: 3,  h: 3,  rotation: 0 },
    ],
  },
];
