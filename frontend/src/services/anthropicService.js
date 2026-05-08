// ─────────────────────────────────────────────
// anthropicService.js
// All Anthropic API calls. Supports:
//   • analyzeRoom   — multi-image + roomGrid
//   • generateLayouts — shape-aware layout generation
//   • reanalyzeLayout — score an edited layout
// ─────────────────────────────────────────────
const API_URL    = 'https://api.anthropic.com/v1/messages';
const MODEL      = 'claude-sonnet-4-20250514';
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
// photos: [{ base64, mediaType, orientation }]
// Returns full analysis JSON including roomGrid.
// ─────────────────────────────────────────────
export async function analyzeRoom({ photos, width, height, unit = 'm' }) {
  const gridW = Math.round(width  * 5);
  const gridH = Math.round(height * 5);

  const systemPrompt = `You are an expert interior designer and certified Feng Shui consultant.
Analyze room photos and return structured JSON only — no markdown, no backticks, no explanation.
Schema:
{
  "description": "string",
  "style": "string",
  "roomShape": "rectangle | L-shape | U-shape | irregular | other",
  "roomGrid": [["room"|"void"|"wall"|"door"|"window", ...]],
  "existingFurniture": [{ "id":"string","label":"string","x":number,"y":number,"w":number,"h":number,"rotation":0 }],
  "fengShuiScore": {
    "total": number,
    "breakdown": {
      "qi_flow":         { "score":number, "label":"string", "note":"string" },
      "balance":         { "score":number, "label":"string", "note":"string" },
      "natural_light":   { "score":number, "label":"string", "note":"string" },
      "clutter":         { "score":number, "label":"string", "note":"string" },
      "bagua_alignment": { "score":number, "label":"string", "note":"string" }
    },
    "dominant_element": "wood|fire|earth|metal|water",
    "missing_element":  "wood|fire|earth|metal|water|none",
    "summary": "string"
  },
  "issues": ["string"],
  "recommendations": ["string"]
}
roomGrid must be exactly ${gridH} rows × ${gridW} columns.
Cell values: "room"=floor, "void"=outside boundary, "wall"=fixed wall, "door"=doorway, "window"=window.`;

  const photoBlocks = photos.flatMap((photo, i) => [
    { type:'image', source:{ type:'base64', media_type: photo.mediaType||'image/jpeg', data: photo.base64 } },
    { type:'text',  text:`Photo ${i+1}${photo.orientation ? ` — facing ${photo.orientation}` : ''}.` },
  ]);

  const userContent = [
    ...photoBlocks,
    { type:'text', text:`Room: ${width}×${height}${unit}. Grid: ${gridW}×${gridH}. ${photos.length > 1 ? `${photos.length} photos — use all to determine shape.` : ''} Return JSON only.` },
  ];

  const raw = await callClaude([{ role:'user', content: userContent }], systemPrompt);
  return JSON.parse(raw.replace(/```json|```/g,'').trim());
}

// ─────────────────────────────────────────────
// generateLayouts
// ─────────────────────────────────────────────
export async function generateLayouts({ analysis, width, height, unit = 'm' }) {
  const gridW = Math.round(width  * 5);
  const gridH = Math.round(height * 5);

  const systemPrompt = `You are a Feng Shui interior design expert. Return JSON only — no markdown, no explanation.
Schema:
{
  "layouts": [{
    "id":"layout_1","name":"string","theme":"string",
    "fengShuiImprovement":number,"dominant_element":"string",
    "furniture":[{ "id":"string","type":"string","label":"string","x":number,"y":number,"w":number,"h":number,"rotation":0 }],
    "rationale":"string"
  }]
}
Only place furniture on "room" cells — never on void, wall, door, or window.`;

  const userText = `Room: ${width}×${height}${unit}. Grid: ${gridW}w×${gridH}h. Shape: ${analysis.roomShape||'rectangle'}.
roomGrid: ${JSON.stringify(analysis.roomGrid)}
Analysis: ${JSON.stringify({ fengShuiScore: analysis.fengShuiScore, issues: analysis.issues })}
Generate 3 distinct layouts. JSON only.`;

  const raw = await callClaude([{ role:'user', content: userText }], systemPrompt);
  return JSON.parse(raw.replace(/```json|```/g,'').trim());
}

// ─────────────────────────────────────────────
// reanalyzeLayout
// Takes a user-edited layout + the original room data,
// returns a fresh fengShuiScore for the new arrangement.
// ─────────────────────────────────────────────
export async function reanalyzeLayout({ layout, originalAnalysis, width, height, unit = 'm' }) {
  const systemPrompt = `You are a certified Feng Shui consultant.
Evaluate the provided room layout and return a JSON fengShuiScore only — no markdown, no explanation.
Schema:
{
  "total": number (0-100),
  "breakdown": {
    "qi_flow":         { "score":number, "label":"string", "note":"string" },
    "balance":         { "score":number, "label":"string", "note":"string" },
    "natural_light":   { "score":number, "label":"string", "note":"string" },
    "clutter":         { "score":number, "label":"string", "note":"string" },
    "bagua_alignment": { "score":number, "label":"string", "note":"string" }
  },
  "dominant_element": "wood|fire|earth|metal|water",
  "missing_element":  "wood|fire|earth|metal|water|none",
  "summary": "string",
  "issues": ["string"],
  "recommendations": ["string"],
  "delta": number
}
"delta" = difference from original score (can be negative).`;

  const userText = `Original room: ${width}×${height}${unit}.
Original score: ${originalAnalysis.fengShuiScore?.total}.
Room shape: ${originalAnalysis.roomShape || 'rectangle'}.
Room grid: ${JSON.stringify(originalAnalysis.roomGrid)}

Edited layout name: "${layout.name}"
Furniture positions: ${JSON.stringify(layout.furniture)}

Evaluate this edited arrangement and return the JSON fengShuiScore.`;

  const raw = await callClaude([{ role:'user', content: userText }], systemPrompt);
  return JSON.parse(raw.replace(/```json|```/g,'').trim());
}
