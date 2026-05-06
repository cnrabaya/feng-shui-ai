# PLAN.md — AI Room Feng Shui Evaluator

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [Solution](#3-solution)
4. [Core Features](#4-core-features)
5. [User Flow](#5-user-flow)
6. [System Architecture](#6-system-architecture)
7. [Tech Stack](#7-tech-stack)
8. [Feng Shui Scoring System](#8-feng-shui-scoring-system)
9. [API Design](#9-api-design)
10. [Risks & Mitigations](#10-risks--mitigations)
11. [Future Extensions](#11-future-extensions)
12. [Preprocessing for Multiple Photos](#12-preprocessing-for-multiple-photos)

---

## 1. Project Overview

**Project Name:** FengShuiAI  
**Tagline:** *Upload your room. Unlock its energy.*  
**Track:** Track 3 — Vision & Multimodal AI  
**Compute:** AMD Instinct MI300X via AMD Developer Cloud  
**Model:** Qwen-VL served via vLLM on ROCm  

FengShuiAI is a multimodal AI application that evaluates the Feng Shui of any room from a single photo. Users upload an image of their room (with optional dimensions), and the system uses a vision-language model to detect all elements in the room, analyze the layout against Feng Shui principles, generate a scored evaluation with explanations, and produce 2–3 alternative layout suggestions — all annotated directly onto the original photo.

---

## 2. Problem Statement

Feng Shui consultation is expensive, inaccessible, and subjective. A professional Feng Shui consultant charges $300–$1,000 per session, requires an in-person visit, and is unavailable to most people globally. Meanwhile, millions of people intuitively feel that their living or working spaces are not optimized — they just don't know why or how to fix it.

There is no widely available, AI-powered tool that can:
- Analyze a room photo and understand its spatial layout
- Apply structured Feng Shui principles to that layout
- Generate specific, actionable rearrangement suggestions
- Visualize those suggestions on the original room image

FengShuiAI fills this gap.

---

## 3. Solution

FengShuiAI is an end-to-end multimodal pipeline that takes a room photo as input and delivers:

1. **Element detection** — identifies all furniture, fixtures, and architectural features in the room
2. **Feng Shui scoring** — evaluates the layout against Black Hat Sect principles (Bagua map, five elements, chi flow, commanding position) and produces a score out of 100 with per-zone explanations
3. **Layout suggestions** — generates 2–3 alternative arrangements using only detected elements, with each suggestion visualized as a 2D room layout
4. **Element augmentation** — allows users to add new elements (e.g. "add a plant to the southeast corner") and re-evaluates the room with the updated layout

The system is grounded in a structured scoring rubric encoded in the model's system prompt, ensuring consistent and explainable output rather than free-form hallucination.

---

## 4. Core Features

### Feature 1 — Room Element Detection
Qwen-VL analyzes the uploaded photo and produces a structured JSON inventory of every detected element including furniture type, estimated position, orientation, and proximity to doors/windows/light sources.

### Feature 2 — Feng Shui Score Card
The system evaluates the detected layout against a structured rubric and outputs:
- An overall score out of 100
- A breakdown score per Bagua zone (Wealth, Fame, Relationships, Family, Health, Creativity, Knowledge, Career, Helpful People)
- Per-issue explanations (e.g. "Bed is in direct line with the door — this disrupts the commanding position and reduces the Career zone score by 15 points")
- A chi flow assessment (blocked, restricted, or flowing)

### Feature 3 — Layout Suggestions
The model generates 2–3 alternative room arrangements using only the elements already present in the room. Each suggestion:
- Describes specific moves in plain language
- Assigns a projected improved score
- Is visualized as a 2D room layout with directional arrows and labels overlaid

### Feature 4 — Element Augmentation & Re-evaluation
Users can type or select new elements to add to the room (e.g. "add a mirror on the north wall", "add a plant in the southeast corner"). The system appends the new element to the room context stored in session state and re-runs the Feng Shui evaluation without re-processing the original image — making re-evaluation fast and responsive.

### Feature 5 — Downloadable PDF Report
A full evaluation report is generated on demand including the original photo, score card, all suggestion layouts, and per-suggestion explanations — exportable as a styled PDF.

---

## 5. User Flow

```
1. User uploads a room photo (JPEG/PNG, up to 4K resolution)
   └── Optionally enters room dimensions (length × width × height in meters/feet)

2. System preprocesses the image
   └── EXIF rotation fix → resize → base64 encode

3. Qwen-VL performs element detection
   └── Returns structured JSON: detected objects, positions, door/window locations

4. Feng Shui scorer evaluates the layout
   └── Returns: overall score, per-zone breakdown, issue list, chi flow status

5. Frontend displays the Score Card
   └── User sees score out of 100, zone breakdown, top 3 issues flagged

6. Layout suggester generates 2–3 alternatives
   └── Each suggestion rendered as 2D room layout

7. User optionally adds elements
   └── Types "add a plant to the southeast corner"
   └── System appends to room context → re-evaluates → updated score card displayed

8. User downloads PDF report (optional)
   └── Full evaluation + all suggestion images + explanations
```

---

## 6. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      FRONTEND                           │
│           React + TailwindCSS (Vite)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Photo upload │  │  Score card  │  │  Suggestion  │  │
│  │ + dimensions │  │  + Bagua map │  │  overlays    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────┬───────────────────────────────┘
                          │ HTTP / REST
┌─────────────────────────▼───────────────────────────────┐
│                    API LAYER                            │
│              FastAPI (Python 3.11)                      │
│   /evaluate  │  /suggest  │  /add-element  │  /report  │
│                   Redis session store                   │
└────────┬──────────────────────────┬─────────────────────┘
         │                          │
┌────────▼────────┐      ┌──────────▼──────────┐
│ IMAGE PROCESSOR │      │   OUTPUT RENDERER   │
│ Pillow + OpenCV │      │ OpenCV + ReportLab  │
│ Resize/encode   │      │ Arrows + labels     │
│ Annotation Prep |      │ PDF generation      │
└────────┬────────┘      └─────────────────────┘
         │
┌────────▼──────────────────────────────────────────────┐
│                  VISION MODEL                         │
│           Qwen-VL served via vLLM                     │
│              AMD MI300X + ROCm                        │
│  Pass 1: Element detection → structured JSON          │
│  Pass 2: Feng Shui scoring → score + explanations     │
│  Pass 3: Layout suggestions → movement instructions   │
└───────────────────────────────────────────────────────┘
```

---

## 7. Tech Stack

### Frontend
| Tool | Version | Purpose |
|------|---------|---------|
| React | 18.x | UI framework |
| TailwindCSS | 3.x | Styling |
| Vite | 5.x | Build tool |
| Axios | 1.x | HTTP client |

### Backend
| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11 | Runtime |
| FastAPI | 0.110+ | REST API framework |
| Redis | 7.x | Session state store |
| Celery | 5.x | Async task queue for batch processing |
| Uvicorn | 0.29+ | ASGI server |

### Image Processing
| Tool | Version | Purpose |
|------|---------|---------|
| Pillow | 10.x | Upload normalization, EXIF fix, base64 encoding |
| OpenCV (cv2) | 4.9+ | Annotation rendering, arrow/label overlay |
| ReportLab | 4.x | PDF report generation |

### AI / Model Layer
| Tool | Version | Purpose |
|------|---------|---------|
| Qwen-VL | 7B | Primary vision-language model |
| vLLM | 0.4+ | High-throughput model serving |
| ROCm | 6.x | AMD GPU runtime |
| Hugging Face Transformers | 4.40+ | Model loading and tokenization |

### AMD Compute
| Resource | Spec | Purpose |
|----------|------|---------|
| AMD Instinct MI300X | 192GB HBM3 | Model inference + high-res image processing |
| AMD Developer Cloud | MI300X instance | Hosted compute environment |
| ROCm | 6.x | GPU-accelerated inference runtime |

---

## 8. Feng Shui Scoring System

FengShuiAI uses **Black Hat Sect (BTB) Feng Shui** — the most internationally recognized school, which does not require compass directions, making it ideal for photo-based evaluation.

### Scoring Rubric (out of 100)

| Category | Max Points | Key Rules |
|----------|-----------|-----------|
| Commanding Position | 25 | Primary furniture (bed/desk/sofa) must face the door without being in direct line with it |
| Bagua Zone Alignment | 20 | Key items placed in their corresponding Bagua zones |
| Chi Flow | 20 | Clear pathways, no clutter blocking movement through the room |
| Five Elements Balance | 15 | Mix of Wood, Fire, Earth, Metal, Water elements present |
| Light & Air | 10 | Natural light access not blocked, windows unobstructed |
| Mirror Placement | 10 | Mirrors not facing the bed, not reflecting the door directly |

### Bagua Map Application
The Bagua map is overlaid on the room floor plan using the entrance wall as the reference baseline:

```
┌─────────────┬─────────────┬─────────────┐
│  WEALTH     │    FAME     │RELATIONSHIPS│
│  (SE)       │    (S)      │    (SW)     │
├─────────────┼─────────────┼─────────────┤
│  FAMILY     │   HEALTH    │ CREATIVITY  │
│  (E)        │  (CENTER)   │    (W)      │
├─────────────┼─────────────┼─────────────┤
│  KNOWLEDGE  │   CAREER    │HELPFUL PPL  │
│  (NE)       │    (N)      │    (NW)     │
└─────────────┴──────┬──────┴─────────────┘
                     │
              ENTRANCE WALL
```

### Prompt Engineering Strategy

The Feng Shui scorer uses a two-pass prompting approach:

**Pass 1 — Element Extraction Prompt:**
```
You are a room layout analyst. Analyze this room image and return a JSON object with:
- "elements": list of detected furniture/fixtures with estimated position
  (north/south/east/west/center relative to room), orientation, and size category
- "doors": list of door locations (wall + approximate position on wall)
- "windows": list of window locations
- "light_sources": natural and artificial light sources
Return ONLY valid JSON. No explanation, no markdown.
```

**Pass 2 — Feng Shui Scoring Prompt:**
```
You are a Black Hat Sect Feng Shui expert. Given this room layout JSON:
[LAYOUT JSON]
Room dimensions: [DIMENSIONS]

Evaluate the room using this exact rubric:
- Commanding position (25pts): ...
- Bagua zone alignment (20pts): ...
[FULL RUBRIC]

Return a JSON object with:
- "total_score": integer 0-100
- "breakdown": object with score per category
- "issues": list of specific problems found, each with affected_score and explanation
- "chi_flow": "blocked" | "restricted" | "flowing"
Return ONLY valid JSON.
```

---

## 9. API Design

### `POST /evaluate`
Accepts a room photo and optional dimensions. Returns element detection results and Feng Shui score.

**Request:**
```json
{
  "image": "<base64-encoded image>",
  "dimensions": { "length": 4.5, "width": 3.8, "height": 2.7, "unit": "meters" },
  "session_id": "uuid-string"
}
```

**Response:**
```json
{
  "session_id": "uuid-string",
  "elements": [...],
  "score": {
    "total": 72,
    "breakdown": { "commanding_position": 18, "bagua_alignment": 14, ... },
    "issues": [
      { "issue": "Bed aligned with door", "zone": "Career", "score_impact": -7, "explanation": "..." }
    ],
    "chi_flow": "restricted"
  }
}
```

### `POST /suggest`
Generates 2–3 layout suggestions based on the current session's element list and score.

**Request:**
```json
{ "session_id": "uuid-string" }
```

**Response:**
```json
{
  "suggestions": [
    {
      "id": 1,
      "projected_score": 88,
      "moves": [
        { "element": "bed", "from": "north wall", "to": "east wall", "reason": "Achieves commanding position" }
      ],
      "annotated_image": "<base64-encoded annotated photo>"
    }
  ]
}
```

### `POST /add-element`
Adds a new element to the room context and returns an updated score.

**Request:**
```json
{
  "session_id": "uuid-string",
  "element": { "type": "plant", "position": "southeast corner" }
}
```

**Response:**
```json
{
  "updated_score": { "total": 79, "breakdown": {...}, "issues": [...] },
  "delta": +7
}
```

### `GET /report/{session_id}`
Returns a downloadable PDF report for the session.

---

## 10. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Qwen-VL misidentifies furniture | Medium | Medium | Add a user-editable element list so users can correct detection errors |
| Model returns malformed JSON | Medium | High | Wrap all model calls in a retry loop with output validation; fall back to regex extraction |
| Suggestions reference undetected elements | Low | High | Constrain the suggestion prompt: "only use elements from this list: [DETECTED ELEMENTS]" |
| Arrow annotations are confusing | Low | Medium | Pre-test annotation rendering on 5+ room photos before demo day |
| AMD instance setup takes too long | Low | High | Set up and test the instance on Day 0 before the hackathon officially starts |
| Demo room photo gives poor score | Low | Low | Pre-screen 3–4 room photos and select one with a mix of issues and strengths for the demo |

---

## 11. Future Extensions

**Commercial extensions beyond the hackathon:**

- **Real estate integration:** Automatically evaluate every listing photo on a property platform and surface feng shui scores as a search filter
- **AR mode:** Use a phone camera in real-time to evaluate the room as the user walks through it
- **Furniture shopping integration:** When a suggestion recommends adding a Wood element, link to specific products that would fulfill that role
- **Multi-room coherence:** Evaluate how the feng shui of connected rooms (bedroom → living room → kitchen) interact with each other
- **Historical tracking:** Re-evaluate the same room over time as the user makes changes and track score improvement

---

## 12. Preprocessing for Multiple Photos

### 1. EXIF Rotation Fix — Same as Before, Apply to All ✅

```python
from PIL import Image, ImageOps

def fix_rotation(image_path):
    img = Image.open(image_path)
    return ImageOps.exif_transpose(img)

images = [fix_rotation(p) for p in uploaded_paths]
```
Nothing new here — just apply it to every image in the batch.

### 2. Ask the User to Label Each Photo's Direction 🧭

This is the single most impactful thing you can do to prevent misinterpretation. Before processing, prompt the user:
- Photo 1: Which wall are you facing? → North / South / East / West / Not sure
- Photo 2: Which wall are you facing? → ...

Even rough labels ("facing the window wall", "facing the door") give the model a spatial anchor that dramatically reduces position conflicts. In your UI this is a simple dropdown per uploaded photo — low friction, high payoff.
If the user selects "Not sure" for everything, fall back to the multi-pass strategy below.

### 3. Deduplicate With a Two-Pass Strategy

Don't send all photos to Qwen-VL simultaneously and ask for one JSON. Instead use two deliberate passes:

**Pass 1A — Per-photo element extraction (one call per photo)**
Send each photo individually with a prompt that forces a consistent output schema and explicitly flags uncertainty:

```python
EXTRACTION_PROMPT = """
Analyze this room photo and return a JSON object.
You are looking at the room from the direction: {direction}

Return:
{{
  "elements": [
    {{
      "id": "unique short label e.g. sofa_1",
      "type": "furniture type",
      "position_relative_to_camera": "left / right / center / background",
      "wall_association": "which wall it is against, if visible",
      "partially_visible": true/false,
      "confidence": "high / medium / low"
    }}
  ],
  "architectural_features": {{
    "doors": [...],
    "windows": [...],
    "visible_walls": [...]
  }}
}}

IMPORTANT: If an element is partially cut off at the edge of the frame, 
mark partially_visible as true. Do not guess at elements outside the frame.
Return ONLY valid JSON.
"""
```

**Pass 1B — Merge and deduplicate (one LLM call)**
After getting per-photo JSONs, send all of them together to the model with a dedicated merge prompt:

```python
MERGE_PROMPT = """
You have received element detection results from {n} photos of the SAME room
taken from different angles.

Photo results:
{all_photo_jsons}

Your task: Produce ONE unified room inventory by:
1. Merging duplicate elements (same object seen from multiple angles)
2. Resolving position conflicts using the most confident detection
3. Flagging any elements that appear in only one photo as "unconfirmed"
4. Building a single coherent spatial map of the room

Return a unified JSON with:
{{
  "confirmed_elements": [...],   // seen in 2+ photos
  "unconfirmed_elements": [...], // seen in only 1 photo
  "architectural_features": {{...}},
  "spatial_conflicts": [...]     // positions that couldn't be reconciled
}}
"""
```
This two-pass approach means the merge step has full visibility across all photos, but each photo was analyzed cleanly and independently first.

### 4. Minimum and Maximum Photo Guidance

Set expectations in your UI:
- **1 (Baseline):** works but misses corners and layout context
- **2–3 (Sweet spot):** opposite corners give a complete picture
- **4 (Ideal):** one per wall gives full spatial coverage
- **5+:** Diminishing returns, higher deduplication cost

The optimal instruction to give users: "Take one photo from each corner of the room, facing the opposite corner." Four photos, four diagonal angles — you get complete coverage with minimal overlap.

### 5. Resize Before Sending Multiple Photos ⚠️

This is where resizing becomes actually necessary, unlike the single-photo case. If a user sends 4 photos at 4K each, you're base64-encoding ~50MB of image data and stuffing it into API calls. This will be slow and may hit token limits.
Apply a practical cap:

```python
from PIL import Image

def prepare_for_upload(img, max_dimension=1920):
    # Only resize if actually oversized
    if max(img.size) > max_dimension:
        img.thumbnail((max_dimension, max_dimension), Image.LANCZOS)
    return img
```
This keeps quality high enough for Qwen-VL's element detection while keeping the payload reasonable.

### 6. Consistency Prompt Engineering

Across all your prompts, enforce a fixed vocabulary to prevent the synonym problem. Inject this into every per-photo extraction prompt:

```python
ELEMENT_VOCABULARY = """
Use ONLY these furniture type labels:
bed, sofa, armchair, dining_table, coffee_table, desk, wardrobe, 
dresser, bookshelf, tv_stand, plant, lamp_floor, lamp_table, 
lamp_ceiling, mirror, rug, curtains, artwork, door, window

Do not invent new labels. If something doesn't fit, use the closest match
and note it in a "notes" field.
"""
```
Fixing vocabulary prevents "couch" and "sofa" and "loveseat" from being treated as three different elements during the merge step.

### How the Updated Pipeline Looks

```
User uploads N photos (2–4 recommended)
         ↓
Per-photo: EXIF fix + resize if >1920px + base64 encode
         ↓
User labels each photo direction (UI dropdown)
         ↓
Pass 1A: Per-photo element extraction (N parallel Qwen-VL calls)
         ↓
Pass 1B: Merge + deduplicate (1 Qwen-VL call with all N JSONs)
         ↓
Pass 2: Feng Shui scoring on unified room JSON
         ↓
Pass 3: Layout suggestions
         ↓
OpenCV: Annotation rendering on best representative photo
         ↓
PDF report output
```

### AMD Angle — Parallel Per-Photo Calls

Pass 1A is naturally parallelizable — each photo is an independent extraction call. On MI300X this is your compute showcase moment:

```python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url="http://<your-amd-instance-ip>:8000/v1",
    api_key="placeholder"
)

async def extract_elements(image_b64, direction):
    response = await client.chat.completions.create(
        model="Qwen/Qwen-VL-Chat",
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url",
                 "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
                {"type": "text",
                 "text": EXTRACTION_PROMPT.format(direction=direction)}
            ]
        }],
        max_tokens=1000
    )
    return response.choices[0].message.content

async def process_all_photos(photos_and_directions):
    tasks = [
        extract_elements(b64, direction)
        for b64, direction in photos_and_directions
    ]
    return await asyncio.gather(*tasks)  # all N photos processed in parallel
```
Four photos processed in parallel on MI300X vs sequentially — benchmark and show this delta in your demo. That's a concrete, measurable AMD advantage.
