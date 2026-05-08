// ─────────────────────────────────────────────
// anthropicService.js
// Single source of truth for all AI API calls.
// Supports multiple images per analysis call.
// ─────────────────────────────────────────────

const API_URL   = 'https://api.anthropic.com/v1/messages';
const MODEL     = 'claude-sonnet-4-20250514';
const MAX_TOKENS = 4096;

async function callClaude(messages, systemPrompt) {
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: MODEL, max_tokens: MAX_TOKENS, system: systemPrompt, messages }),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err?.error?.message || `API error ${response.status}`);
  }
  const data = await response.json();
  return data.content.map(b => b.text || '').join('');
}

// ─────────────────────────────────────────────
// analyzeRoom
// Accepts an array of photos (each with base64 + orientation)
// plus room dimensions. Returns full analysis JSON including roomGrid.
//
// photos: [{ base64, mediaType, orientation }]
// ─────────────────────────────────────────────
export async function analyzeRoom({ photos, width, height, unit = 'm' }) {
  const gridW = Math.round(width  * 5);
  const gridH = Math.round(height * 5);

  const systemPrompt = `You are an expert interior designer and certified Feng Shui consultant.
You analyze room photos and return structured JSON only — no markdown, no explanation, no backticks.
The JSON must match this exact schema:
{
  "description": "string — 2-3 sentence natural description of the room",
  "style": "string — detected interior style",
  "roomShape": "rectangle | L-shape | U-shape | irregular | other",
  "roomGrid": [
    ["room"|"void"|"wall"|"door"|"window", ...]
  ],
  "existingFurniture": [
    { "id": "string", "label": "string", "x": number, "y": number, "w": number, "h": number, "rotation": 0 }
  ],
  "fengShuiScore": {
    "total": number (0-100),
    "breakdown": {
      "qi_flow":         { "score": number, "label": "string", "note": "string" },
      "balance":         { "score": number, "label": "string", "note": "string" },
      "natural_light":   { "score": number, "label": "string", "note": "string" },
      "clutter":         { "score": number, "label": "string", "note": "string" },
      "bagua_alignment": { "score": number, "label": "string", "note": "string" }
    },
    "dominant_element": "wood | fire | earth | metal | water",
    "missing_element":  "wood | fire | earth | metal | water | none",
    "summary": "string"
  },
  "issues": ["string"],
  "recommendations": ["string"]
}

CRITICAL roomGrid instructions:
- roomGrid must be exactly ${gridH} rows × ${gridW} columns (rows first, then columns)
- Cell values: "room" = walkable floor, "void" = outside the room boundary (for non-rectangular shapes), "wall" = fixed wall segment, "door" = doorway, "window" = window position
- For rectangular rooms, all cells are "room" except edges where doors/windows exist
- For L-shaped, U-shaped, or irregular rooms, use "void" for cells that fall outside the actual floor boundary
- Use information from ALL provided photos to determine the true shape
- Place doors and windows accurately based on photos and orientations provided`;

  // Build content blocks — one image block per photo with orientation context
  const photoBlocks = photos.flatMap((photo, i) => [
    {
      type: 'image',
      source: { type: 'base64', media_type: photo.mediaType || 'image/jpeg', data: photo.base64 },
    },
    {
      type: 'text',
      text: `Photo ${i + 1}${photo.orientation ? ` — photographer facing ${photo.orientation}` : ' — orientation unknown'}.`,
    },
  ]);

  const userContent = [
    ...photoBlocks,
    {
      type: 'text',
      text: `Room dimensions: ${width} × ${height} ${unit}.
Grid size: ${gridW} columns × ${gridH} rows (1 grid unit = 0.2${unit}).
${photos.length > 1 ? `${photos.length} photos provided from different angles — use all of them to determine the complete room shape, furniture placement, and any irregular features like alcoves or bay windows.` : ''}
Analyze this room and return only the JSON object.`,
    },
  ];

  const raw     = await callClaude([{ role: 'user', content: userContent }], systemPrompt);
  const cleaned = raw.replace(/```json|```/g, '').trim();
  return JSON.parse(cleaned);
}

// ─────────────────────────────────────────────
// generateLayouts
// Takes analysis (including roomGrid) + dimensions,
// returns 3 layout alternatives that respect the room shape.
// ─────────────────────────────────────────────
export async function generateLayouts({ analysis, width, height, unit = 'm' }) {
  const gridW = Math.round(width  * 5);
  const gridH = Math.round(height * 5);

  const systemPrompt = `You are a Feng Shui interior design expert.
Generate 3 optimized room layout alternatives as JSON only — no markdown, no explanation.
Respond ONLY with a valid JSON object matching this schema:
{
  "layouts": [
    {
      "id": "layout_1",
      "name": "string",
      "theme": "string",
      "fengShuiImprovement": number,
      "dominant_element": "wood | fire | earth | metal | water",
      "furniture": [
        { "id": "string", "type": "string", "label": "string",
          "x": number, "y": number, "w": number, "h": number, "rotation": 0 }
      ],
      "rationale": "string"
    }
  ]
}
IMPORTANT: Only place furniture on cells that are "room" in the roomGrid. Never place furniture on "void", "wall", "door", or "window" cells.`;

  const userText = `Room: ${width} × ${height} ${unit}. Grid: ${gridW}w × ${gridH}h.
Room shape: ${analysis.roomShape || 'rectangle'}.
Room grid (${gridH} rows × ${gridW} cols):
${JSON.stringify(analysis.roomGrid)}

Current analysis: ${JSON.stringify({ fengShuiScore: analysis.fengShuiScore, issues: analysis.issues }, null, 2)}

Generate 3 distinct Feng Shui layout alternatives. Furniture must only be placed on "room" cells.
Respond with JSON only.`;

  const raw     = await callClaude([{ role: 'user', content: userText }], systemPrompt);
  const cleaned = raw.replace(/```json|```/g, '').trim();
  return JSON.parse(cleaned);
}
