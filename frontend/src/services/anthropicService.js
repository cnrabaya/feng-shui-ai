// ─────────────────────────────────────────────
// anthropicService.js
// Single source of truth for all AI API calls.
// Swap model, endpoint, or prompt structure here.
// ─────────────────────────────────────────────

const API_URL = 'https://api.anthropic.com/v1/messages';
const MODEL   = 'claude-sonnet-4-20250514';
const MAX_TOKENS = 2048;

/**
 * Low-level fetch wrapper.
 * API key is injected by the Anthropic proxy — do NOT add it here.
 */
async function callClaude(messages, systemPrompt) {
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: MODEL,
      max_tokens: MAX_TOKENS,
      system: systemPrompt,
      messages,
    }),
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
// Takes an image (base64) + dimensions, returns:
//   { description, fengShuiScore, elements, layouts }
// ─────────────────────────────────────────────
export async function analyzeRoom({ imageBase64, imageMediaType = 'image/jpeg', width, height, unit = 'm', orientation = null }) {
  const systemPrompt = `You are an expert interior designer and certified Feng Shui consultant.
You analyze room photos and return structured JSON analysis.
Always respond ONLY with a valid JSON object — no markdown, no explanation, no backticks.
The JSON must match this exact schema:
{
  "description": "string — 2-3 sentence natural description of the room",
  "style": "string — detected interior style (e.g. modern, bohemian, minimalist)",
  "existingFurniture": [
    { "id": "string", "label": "string", "x": number, "y": number, "w": number, "h": number, "rotation": 0 }
  ],
  "fengShuiScore": {
    "total": number (0-100),
    "breakdown": {
      "qi_flow":    { "score": number, "label": "string", "note": "string" },
      "balance":    { "score": number, "label": "string", "note": "string" },
      "natural_light": { "score": number, "label": "string", "note": "string" },
      "clutter":    { "score": number, "label": "string", "note": "string" },
      "bagua_alignment": { "score": number, "label": "string", "note": "string" }
    },
    "dominant_element": "wood | fire | earth | metal | water",
    "missing_element": "wood | fire | earth | metal | water | none",
    "summary": "string — 2-3 sentence overall Feng Shui assessment"
  },
  "issues": ["string"],
  "recommendations": ["string"]
}`;

  const userContent = [
    {
      type: 'image',
      source: { type: 'base64', media_type: imageMediaType, data: imageBase64 },
    },
    {
      type: 'text',
      text: `Analyze this room. Dimensions: ${width} × ${height} ${unit}.
${orientation ? `Camera orientation: the photographer was facing ${orientation}. This means the wall at the back of the photo faces ${orientation}, and the wall directly behind the photographer faces the opposite direction. Use this to determine which walls face which cardinal directions for bagua mapping.` : ''}
Map furniture positions to a grid where the room fits in a ${Math.round(width * 5)} × ${Math.round(height * 5)} grid unit space.
Respond only with the JSON object.`,
    },
  ];

  const raw = await callClaude([{ role: 'user', content: userContent }], systemPrompt);
  const cleaned = raw.replace(/```json|```/g, '').trim();
  return JSON.parse(cleaned);
}

// ─────────────────────────────────────────────
// generateLayouts
// Takes room analysis + dimensions, returns 3 layout alternatives
// ─────────────────────────────────────────────
export async function generateLayouts({ analysis, width, height, unit = 'm', orientation = null }) {
  const systemPrompt = `You are a Feng Shui interior design expert.
Generate optimized room layout alternatives as JSON only — no markdown, no explanation.
Respond ONLY with a valid JSON object matching this schema:
{
  "layouts": [
    {
      "id": "layout_1",
      "name": "string — evocative layout name",
      "theme": "string — one-line design philosophy",
      "fengShuiImprovement": number (delta from current score, can be negative),
      "dominant_element": "wood | fire | earth | metal | water",
      "furniture": [
        { "id": "string (unique instance id)", "type": "string (furnitureTypes id)", "label": "string",
          "x": number, "y": number, "w": number, "h": number, "rotation": 0 }
      ],
      "rationale": "string — 2-sentence explanation of why this layout improves Feng Shui"
    }
  ]
}`;

  const userText = `Room: ${width} × ${height} ${unit}.
${orientation ? `Camera was facing ${orientation} — use this for directional furniture placement recommendations.` : ''}
Grid: ${Math.round(width * 5)} × ${Math.round(height * 5)} units.
Current analysis: ${JSON.stringify(analysis, null, 2)}

Generate 3 distinct layout alternatives that improve the Feng Shui score.
Each layout should use a meaningfully different furniture arrangement philosophy.
Keep furniture within grid bounds. Respond with JSON only.`;

  const raw = await callClaude([{ role: 'user', content: userText }], systemPrompt);
  const cleaned = raw.replace(/```json|```/g, '').trim();
  return JSON.parse(cleaned);
}
