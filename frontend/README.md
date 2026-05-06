# 風水 Feng Shui Room Analyzer — Frontend Module

AI-powered Feng Shui room analysis with 2D layout editor. Built for React (Vite).

---

## Project Structure

```
src/
├── components/
│   ├── upload/
│   │   ├── ImageUploader.jsx       # Drag-drop image input
│   │   └── DimensionsInput.jsx     # Width/height/unit form
│   ├── analysis/
│   │   ├── FengShuiScore.jsx       # Score ring + breakdown bars
│   │   ├── RoomDescription.jsx     # Tabbed description/issues/recommendations
│   │   └── AnalysisPanel.jsx       # Combines the two above
│   ├── layout/
│   │   ├── RoomCanvas.jsx          # 2D SVG room with furniture
│   │   ├── FurnitureItem.jsx       # Individual furniture SVG element
│   │   ├── LayoutAlternatives.jsx  # Cards to select layout
│   │   └── LayoutEditor.jsx        # Rotate/remove/add controls
│   └── ui/
│       ├── Button.jsx              # Shared button (primary/secondary/ghost/danger)
│       ├── Card.jsx                # Surface card
│       ├── StepIndicator.jsx       # 4-step progress bar
│       └── LoadingState.jsx        # Animated loading screen
├── hooks/
│   ├── useRoomAnalysis.js          # Manages AI API state machine
│   └── useLayoutEditor.js          # Furniture selection + movement state
├── services/
│   └── anthropicService.js         # All Anthropic API calls (single source of truth)
├── constants/
│   └── furnitureTypes.js           # Furniture catalog + grid constants
├── styles/
│   ├── tokens.css                  # CSS custom properties (colors, fonts, spacing)
│   └── globals.css                 # Base reset + imports
└── App.jsx                         # Root + step router
```

---

## Integration Into Existing Repo

### Option A — Drop in as a route
```jsx
// In your existing router:
import FengShuiApp from './feng-shui-analyzer/src/App';

<Route path="/feng-shui" element={<FengShuiApp />} />
```
Import `globals.css` at the top of `FengShuiApp` (already done).

### Option B — Use individual components
Every component is self-contained. You can import them individually:
```jsx
import FengShuiScore    from './feng-shui-analyzer/src/components/analysis/FengShuiScore';
import RoomCanvas       from './feng-shui-analyzer/src/components/layout/RoomCanvas';
import { useRoomAnalysis } from './feng-shui-analyzer/src/hooks/useRoomAnalysis';
```

---

## AI Service Configuration

All API calls live in `src/services/anthropicService.js`.

- **Model**: `claude-sonnet-4-20250514` — change here to swap models
- **API key**: injected by Anthropic proxy (do NOT add a key in code)
- **Two functions**:
  - `analyzeRoom({ imageBase64, imageMediaType, width, height, unit })` → description + Feng Shui score
  - `generateLayouts({ analysis, width, height, unit })` → 3 layout alternatives

---

## Canvas / Layout System

- **Grid unit**: 1 unit = 20px (set in `constants/furnitureTypes.js` → `GRID_UNIT`)
- **Scale**: 5 grid units per real-world meter/foot
- Furniture positions are stored as `{ x, y, w, h, rotation }` in grid units
- Layouts are pure JSON — easy to save/restore/export

---

## Key Extension Points

| What to change | Where |
|---|---|
| Add new furniture types | `constants/furnitureTypes.js` → `FURNITURE_TYPES` |
| Change scoring weights | `services/anthropicService.js` → system prompt |
| Add drag-and-drop (future) | `hooks/useLayoutEditor.js` + `components/layout/RoomCanvas.jsx` |
| Export layout as image | Add `html-to-image` or `dom-to-svg` and call from `LayoutEditor.jsx` |
| Persist layouts | Add localStorage/backend calls in `useLayoutEditor.js` |
| Change color theme | `styles/tokens.css` → CSS variables |

---

## Dev Setup

```bash
# From your existing Vite project root:
npm install   # no new deps required — uses React + standard browser APIs

# Run dev server
npm run dev
```

Fonts loaded from Google Fonts (Noto Serif, DM Sans). Works offline if you self-host them.


