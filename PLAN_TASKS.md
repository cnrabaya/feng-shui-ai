# Implementation Plan: FengShuiAI

## Overview

Build an AI-powered room Feng Shui evaluator: React/Vite frontend uploads a room photo, FastAPI backend processes it and queries a vision-language model, returns a score + suggestions.

## Architecture Decisions

- **Frontend-first vertical slice:** Build a working end-to-end demo with mock AI responses before integrating the real model
- **Session-less by default:** Redis/session store deferred — store all state client-side until session management is proven needed
- **Python 3.12 + FastAPI:** Async endpoints, Pydantic validation, uvicorn ASGI server (see `backend/.python-version`)
- **Vite proxy:** `/v1` → `http://127.0.0.1:8000` (dev convenience; swap for nginx in prod)

---

## Phase 1: Project Foundation

### Task 1: Frontend scaffold
- [x] Run `npm create vite@latest frontend -- --template react` (creates `package.json`)
- [x] Install deps: `npm install axios react-hook-form @hookform/resolvers zod tailwindcss postcss autoprefixer`
- [x] Initialize Tailwind: `npx tailwindcss init -p` → configure `content: ["./index.html", "./src/**/*.{js,jsx}"]`
- [x] Fix `frontend/index.html` title → `"FengShuiAI"`
- [x] Create `frontend/src/styles.css` with Tailwind directives

**Verification:** `npm run dev` starts without errors, Tailwind classes apply.

**Files:** `frontend/package.json`, `frontend/tailwind.config.js`, `frontend/postcss.config.js`, `frontend/src/styles.css`, `frontend/index.html`

---

### Task 2: App shell + routing
- [x] Create `frontend/src/App.jsx` with basic layout: header, upload area placeholder, score card placeholder
- [x] Create `frontend/src/lib/api.js` with axios client pointing to `/v1`

**Verification:** App renders at `localhost:5173` without console errors.

**Files:** `frontend/src/App.jsx`, `frontend/src/lib/api.js`

---

### Task 3: Backend scaffold
- [x] Add to `backend/pyproject.toml`: `fastapi`, `uvicorn[standard]`, `pydantic-settings`, `python-multipart`
- [x] Create `backend/app/core/config.py` with `settings` object (app_name, app_version, cors_origins)
- [x] Create `backend/app/routes/__init__.py` (empty router)
- [x] Update `backend/app/main.py` — verify it can import settings and router

**Verification:** `uvicorn app.main:app --reload` starts on port 8000 with no import errors.

**Files:** `backend/pyproject.toml`, `backend/app/core/config.py`, `backend/app/routes/__init__.py`

---

### Checkpoint: Phase 1
- [x] Frontend builds and serves on :5173
- [x] Backend starts on :8000
- [x] No import errors in either

---

## Phase 2: API Contract & Mock Backend

### Task 4: Define Pydantic models + API endpoints
- [x] Create `backend/app/models/schemas.py`: `EvaluateRequest`, `EvaluateResponse`, `SuggestRequest`, `SuggestResponse`, `AddElementRequest`, `AddElementResponse`
- [x] Create `backend/app/routes/evaluate.py`: `POST /v1/evaluate` — returns mock element detection + score
- [x] Create `backend/app/routes/suggest.py`: `POST /v1/suggest` — returns mock suggestions
- [x] Create `backend/app/routes/elements.py`: `POST /v1/add-element` — returns updated mock score
- [x] Wire all routes into `backend/app/routes/__init__.py` → included in main router

**Verification:** `POST /v1/evaluate` returns JSON, `POST /v1/suggest` returns JSON, `POST /v1/add-element` returns JSON. HTTP 200 for valid input, 422 for invalid.

**Files:** `backend/app/models/schemas.py`, `backend/app/routes/evaluate.py`, `backend/app/routes/suggest.py`, `backend/app/routes/elements.py`

---

### Checkpoint: Phase 2
- [ ] End-to-end: upload photo → see score → get suggestions → add element → updated score
- [ ] No console errors in browser devtools
- [ ] API responses are valid JSON

---

## Phase 3: Feng Shui Scoring Logic

### Task 6: Scoring engine (backend, no AI yet)
- [ ] Create `backend/app/services/scoring.py` with `calculate_feng_shui_score(elements, dimensions)` — pure Python, no model calls
- [ ] Implement commanding position check (25pts): primary furniture must face door without being in direct line
- [ ] Implement Bagua zone alignment (20pts): items matched to correct zones
- [ ] Implement chi flow (20pts): check for blocked pathways
- [ ] Implement five elements balance (15pts): count Wood/Fire/Earth/Metal/Water elements
- [ ] Implement light/air check (10pts): window coverage, light source detection
- [ ] Implement mirror placement (10pts): no mirrors facing bed or reflecting door
- [ ] Update `POST /v1/evaluate` to call the scoring engine

**Verification:** Pass sample element lists → get consistent numeric scores.

**Files:** `backend/app/services/scoring.py`

---

### Task 7: Element detection mock → real placeholder
- [ ] Create `backend/app/services/vision.py` with `detect_elements(image_base64) -> list[Element]` stub that returns hardcoded element list
- [ ] Update `POST /v1/evaluate` to call `detect_elements` before scoring
- [ ] Document the `detect_elements` interface so it can be swapped for Qwen-VL later

**Verification:** `POST /v1/evaluate` with a real base64 image returns element list + score.

**Files:** `backend/app/services/vision.py`

---

### Checkpoint: Phase 3
- [ ] Real scoring logic runs server-side (not hardcoded responses)
- [ ] Element detection is pluggable (swap stub for model when ready)

---

## Phase 4: Frontend UI Polish

### Task 8: Bagua map visualization
- [ ] Create `frontend/src/components/BaguaMap.jsx` — 3×3 grid with zone labels, color-coded by score
- [ ] Integrate into score card display

**Verification:** Score card shows colored Bagua overlay matching score breakdown.

**Files:** `frontend/src/components/BaguaMap.jsx`

---

### Task 9: Suggestion overlays
- [ ] Create `frontend/src/components/SuggestionCard.jsx` with move list and projected score delta
- [ ] Create `frontend/src/components/OverlayRenderer.jsx` — renders base64 annotated image if provided

**Verification:** Suggestions display with clear before/after moves.

**Files:** `frontend/src/components/SuggestionCard.jsx`, `frontend/src/components/OverlayRenderer.jsx`

---

### Task 10: Add-element UI
- [ ] Create `frontend/src/components/ElementAdder.jsx` — type-in or select element type + position
- [ ] Wire to `POST /v1/add-element` and update score display

**Verification:** Add "plant to southeast corner" → score updates reflect the addition.

**Files:** `frontend/src/components/ElementAdder.jsx`

---

## Phase 5: Real AI Integration (Future)

### Task 11: Qwen-VL integration
- [ ] Add `vllm`, `transformers`, `torch` to `pyproject.toml`
- [ ] Replace `backend/app/services/vision.py` stub with real Qwen-VL call
- [ ] Implement two-pass prompting (element extraction → scoring)
- [ ] Implement backend state handling for element augmentation (append to room context and re-evaluate without re-processing image)

**Verification:** Real photo upload returns AI-detected elements matching actual room contents.

---

## Phase 6: Multi-Photo Processing

### Task 12: Multi-photo upload and direction labeling
- [ ] Add multi-photo upload support to frontend (array of files)
- [ ] Add per-photo direction dropdown (North/South/East/West/Not sure) in upload UI
- [ ] Add instructional UI guidance for optimal photo quantity (1-4+ photos, sweet spot is 2-3)
- [ ] Pass photo direction metadata to backend with each photo

**Verification:** Multiple photos can be uploaded with direction labels attached.

**Files:** `frontend/src/App.jsx`, `backend/app/models/schemas.py`

---

### Task 13: Per-photo element extraction (parallel)
- [ ] Create `backend/app/services/vision.py` async parallel call support
- [ ] Implement `extract_elements_batch(images: list[ImageData])` with direction-aware prompts
- [ ] Add element vocabulary constant to enforce consistent furniture labels

**Verification:** 4 photos processed in parallel return consistent element labels.

**Files:** `backend/app/services/vision.py`

---

### Task 14: Merge and deduplicate
- [ ] Create `backend/app/services/merge.py` with merge prompt logic
- [ ] Implement `merge_element_results(photo_results: list[dict]) -> UnifiedRoom`
- [ ] Mark unconfirmed_elements (seen in only 1 photo) vs confirmed_elements

**Verification:** Same sofa seen in 2 photos becomes one confirmed element.

**Files:** `backend/app/services/merge.py`

---

### Task 15: Pre-upload Image Processing
- [ ] Add EXIF rotation fix using `ImageOps.exif_transpose` in `backend/app/services/image_processor.py`
- [ ] Add image resizing in `backend/app/services/image_processor.py` (max 1920px)
- [ ] Apply to all photos in batch before base64 encoding

**Verification:** 4K photos resized to ≤1920px before API calls.

**Files:** `backend/app/services/image_processor.py`

---

## Phase 7: PDF Report

### Task 16: PDF report generation
- [ ] Add `reportlab` to `pyproject.toml`
- [ ] Create `backend/app/services/report.py` with `generate_pdf_report(session_id) -> bytes`
- [ ] Implement `GET /report/{session_id}` endpoint returning PDF response
- [ ] Include: original photo, score card, all suggestion layouts, explanations

**Verification:** Download PDF at `GET /report/{session_id}` with all sections rendered.

**Files:** `backend/app/services/report.py`, `backend/app/routes/report.py`

---

## Phase 8: Async Task Queue (Future)

### Task 17: Celery & Redis Integration for Batch Processing
- [ ] Setup Redis session store for persisting room context across requests
- [ ] Setup Celery workers to handle heavy vision model inferences in the background
- [ ] Refactor API endpoints to return job IDs and allow frontend polling

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Vision model JSON output is malformed | Medium | Add retry loop + regex fallback extraction |
| Frontend state gets complex | Medium | Keep component tree flat, use React context for session |
| AI scoring is inconsistent | Medium | Lock scoring prompt, validate output schema |
| Vite proxy CORS in prod | Low | Production serves from nginx, not Vite proxy |

## Open Questions

- [ ] Should Redis session store be added now or deferred to when real multi-session support is needed?
- [ ] Any preferred Tailwind color palette / design system to follow?
- [ ] Is there an existing room photo to test with, or should I use a placeholder image?