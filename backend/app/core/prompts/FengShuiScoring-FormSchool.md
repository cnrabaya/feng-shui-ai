# Form School (Xingshi Pai) Feng Shui Scoring

## Overview
Form School is the oldest branch of Feng Shui, originating from "The Book of Burial" by Guo Pu (Jin Dynasty). It focuses on the physical shape and form of the environment — mountains, rivers, terrain, and the shapes of furniture and rooms. It uses the Five Celestial Animals and Five Elements theory to evaluate how shapes and forms affect energy flow.

## Scoring Rubric (100 points total)

### Five Celestial Animals (30 points max)
The Five Celestial Animals represent directional guardian forces. Evaluate their presence and proper positioning:
- **Azure Dragon (East):** Green/long shapes, wood elements, left side of room (as viewed from entrance)
- **White Tiger (West):** White/round shapes, metal elements, right side of room
- **Vermilion Phoenix (South):** Red/triangular shapes, fire elements, front/forward area
- **Black Tortoise (North):** Black/water shapes, water elements, back area
- **Yellow Snake (Center):** Yellow/earth shapes, central stability, center of room

Score = (animals properly represented / 5) * 30

### Shape and Proportion (20 points max)
- Furniture shapes follow beneficial proportions (avoid sharp angles crowding round shapes)
- Room shape is balanced (avoid L-shaped, narrow corridor problems)
- Furniture not oversized for space (creates cramped energy)
- Score: 0-20 based on overall shape harmony

### Terrain and Surroundings (20 points max)
Apply to visible room context:
- **Mountain energy (stillness):** Bookshelves, wardrobes against walls, solid backing
- **Water energy (flow):** Curved furniture, flowing pathways, windows
- Balance of active (fire/water) and restful (earth/metal) zones
- Score: 0-20 based on terrain harmony

### Five Elements in Forms (20 points max)
Evaluate shapes associated with elements:
- **Wood:** Tall, vertical shapes (plants, bookshelves, trees outside)
- **Fire:** Triangular, pointed shapes (artwork frames, angled furniture)
- **Earth:** Square, stable shapes (tables, rugs, ceramic decor)
- **Metal:** Round, circular shapes (mirrors, light fixtures, round tables)
- **Water:** Flowing, wavy shapes (curtains, water features, wavy patterns)

Count distinct element shapes present:
- 5 shapes = 20 pts
- 4 shapes = 16 pts
- 3 shapes = 12 pts
- 2 shapes = 8 pts
- 1 shape = 4 pts

### Chi Flow Through Forms (10 points max)
- Clear pathways between furniture: 0-5 pts
- No sharp corners pointing at seating areas: 0-5 pts

## Element Classifications by Shape

| Element | Shapes | Typical Items |
|---------|--------|---------------|
| Wood | Tall, vertical, rectangular, pillar-like | plants, bookshelves, wardrobes, indoor trees |
| Fire | Triangular, pointed, angular | pointed art frames, angular furniture, triangular decor |
| Earth | Square, flat, stable, grounded | tables, rugs, ceramic tiles, stone |
| Metal | Round, circular, spherical | mirrors, round tables, metal bowls, light fixtures |
| Water | Wavy, flowing, curved | curtains, flowing artwork, water features, aquarium |

## Five Celestial Animals Mapping

```
┌─────────────────────────────────────┐
│                                     │
│   WHITE TIGER        AZURE DRAGON   │
│   (Right Side)         (Left Side)   │
│   Metal, West          Wood, East    │
│                                     │
│            YELLOW SNAKE             │
│              (Center)               │
│            Earth, Stability          │
│                                     │
│     VERMILION PHOENIX    BLACK      │
│       (Front/Forward)    TORTOISE   │
│          Fire, South    (Back)      │
│                         Water, North│
│                                     │
└─────────────────────────────────────┘
```

## Room Dimensions
Room dimensions (if provided): {dimensions}

Use proportions to determine if furniture is appropriately sized for the space.

## Output Schema

Return ONLY valid JSON matching this structure:

{
  "total_score": 0-100,
  "chi_flow": "flowing | restricted | blocked",
  "overall_assessment": "Brief 1-2 sentence summary of the room's Form School Feng Shui",
  "breakdown": {
    "five_celestial_animals": { "score": 0-30, "max": 30, "status": "good | needs_improvement | poor" },
    "shape_and_proportion": { "score": 0-20, "max": 20, "status": "good | needs_improvement | poor" },
    "terrain_and_surroundings": { "score": 0-20, "max": 20, "status": "good | needs_improvement | poor" },
    "five_elements_forms": { "score": 0-20, "max": 20, "status": "good | needs_improvement | poor" },
    "chi_flow_through_forms": { "score": 0-10, "max": 10, "status": "good | needs_improvement | poor" }
  },
  "issues": [
    {
      "issue": "Description of the problem",
      "category": "five_celestial_animals | shape_and_proportion | terrain_and_surroundings | five_elements_forms | chi_flow_through_forms",
      "zone": "Applicable zone (east/west/south/north/center) or N/A",
      "score_impact": -15 to 0,
      "explanation": "Detailed explanation of why this form issue affects energy"
    }
  ],
  "school_specific": {
    "celestial_animals": {
      "azure_dragon": { "present": ["item1"], "absent": true, "notes": "description" },
      "white_tiger": { "present": [], "absent": true, "notes": "description" },
      "vermilion_phoenix": { "present": [], "absent": true, "notes": "description" },
      "black_tortoise": { "present": [], "absent": true, "notes": "description" },
      "yellow_snake": { "present": [], "absent": true, "notes": "description" }
    },
    "element_shapes": {
      "wood": { "present": ["items"], "count": 0 },
      "fire": { "present": ["items"], "count": 0 },
      "earth": { "present": ["items"], "count": 0 },
      "metal": { "present": ["items"], "count": 0 },
      "water": { "present": ["items"], "count": 0 }
    },
    "form_assessment": "Description of overall form harmony"
  }
}

## Important Notes

- Focus on SHAPES and FORMS, not symbolic bagua zones
- Azure Dragon should be taller/stronger than White Tiger (left > right)
- Central area should be open and stable, not cluttered
- Sharp corners pointing at people create sha qi (negative energy)
- Return ONLY valid JSON - no explanation text before or after
