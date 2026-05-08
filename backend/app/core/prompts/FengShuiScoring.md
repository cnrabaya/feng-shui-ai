# Black Hat Sect (BTB) Feng Shui Scoring

## Overview
The Black Hat Sect (also known as BTB or Western Feng Shui) is a modern school created by Thomas Lin Yun that focuses on symbolic Feng Shui without requiring compass directions. It uses the Later Heaven Bagua (Post-Natal arrangement) overlaid on the room with the entrance wall as the reference baseline.

## Scoring Rubric (100 points total)

### Commanding Position (25 points max)
**Rule:** Primary furniture (bed, sofa, desk) must face the entrance door without being directly in line with it.
- Direct line with door = 0 pts for this category
- Does not face entrance = 10 pts
- Faces entrance properly = 25 pts

### Bagua Zone Alignment (20 points max)
The 9 life areas are mapped to the room using the entrance wall as the anchor. Align items to their corresponding zones:
- Wealth (SE): plants, aquariums, money symbols
- Fame (S): artwork, lighting, red items
- Relationships (SW): pairs of items, love symbols, pink/red
- Family (E): plants, green items, wood furniture
- Health (Center): open space, central location
- Creativity (W): art, crystals, metal items
- Knowledge (NE): books, desk, computer
- Career (N): water features, black items, mirrors
- Helpful People (NW): metal objects, crystals, round shapes

Score = (correctly placed items / total placed items) * 20

### Chi Flow (20 points max)
- Center of room is clear (no blocking items): 0-7 pts
- Entrance area is not blocked: 0-7 pts
- Furniture count reasonable (not congested): 0-6 pts

### Five Elements Balance (15 points max)
Classify detected furniture into elements:
- Wood: plants, bookshelves, wardrobes, green items
- Fire: lamps, TV, fireplace, electronics, red items
- Earth: crystals, ceramics, rugs, yellow/brown items
- Metal: mirrors, metal furniture, white items
- Water: windows, aquariums, reflective surfaces, black items

Count distinct elements present:
- 5 elements = 15 pts
- 4 elements = 12 pts
- 3 elements = 9 pts
- 2 elements = 6 pts
- 1 element = 3 pts
- 0 elements = 0 pts

### Light and Air (10 points max)
- Number of windows: 2+ = 5 pts, 1 = 3 pts, 0 = 0 pts
- Windows unobstructed: yes = 5 pts, partially = 2 pts, no = 0 pts

### Mirror Placement (10 points max)
- No mirrors: 10 pts
- Mirrors not facing bed or reflecting door: 10 pts
- Mirror facing bed: -5 pts each
- Mirror reflecting door: -4 pts each

## Element Classifications

| Element | Furniture Types |
|---------|----------------|
| Wood | plant, bookshelf, wardrobe, dresser, green items, wooden furniture |
| Fire | lamp, floor_lamp, table_lamp, tv, tv_stand, fireplace, electronics, red items |
| Earth | rug, carpet, crystal, ceramics, stone, yellow/brown items |
| Metal | mirror, metal_furniture, white items, floor_lamp |
| Water | window, curtain, aquarium, water_feature, reflective_surface, black items |

## Bagua Zone Mapping (Later Heaven - Entrance Aligned)

```
        ENTRANCE WALL
┌─────────┬─────────┬─────────┐
│ WEALTH  │  FAME   │RELATION-│
│   (SE)  │   (S)   │  SHIPS  │
│         │         │   (SW)  │
├─────────┼─────────┼─────────┤
│ FAMILY  │ HEALTH  │CREATIV- │
│   (E)   │ CENTER  │   ITY   │
│         │         │   (W)   │
├─────────┼─────────┼─────────┤
│KNOWLEDGE│ CAREER  │HELPFUL  │
│   (NE)  │   (N)   │ PEOPLE  │
│         │         │   (NW)  │
└─────────┴─────────┴─────────┘
```

## Room Dimensions
Room dimensions (if provided): {dimensions}

Use this information to assess the proportion and scale of furniture placement relative to room size.

## Output Schema

Return ONLY valid JSON matching this structure:

{
  "total_score": 0-100,
  "chi_flow": "flowing | restricted | blocked",
  "overall_assessment": "Brief 1-2 sentence summary of the room's Feng Shui",
  "breakdown": {
    "commanding_position": { "score": 0-25, "max": 25, "status": "good | needs_improvement | poor" },
    "bagua_alignment": { "score": 0-20, "max": 20, "status": "good | needs_improvement | poor" },
    "chi_flow": { "score": 0-20, "max": 20, "status": "good | needs_improvement | poor" },
    "five_elements_balance": { "score": 0-15, "max": 15, "status": "good | needs_improvement | poor" },
    "light_and_air": { "score": 0-10, "max": 10, "status": "good | needs_improvement | poor" },
    "mirror_placement": { "score": 0-10, "max": 10, "status": "good | needs_improvement | poor" }
  },
  "issues": [
    {
      "issue": "Description of the problem",
      "category": "commanding_position | bagua_alignment | chi_flow | five_elements_balance | light_and_air | mirror_placement",
      "zone": "Bagua zone affected (e.g., Wealth, Career, etc.) or N/A",
      "score_impact": -15 to 0,
      "explanation": "Detailed explanation of why this is an issue and its impact on the room's energy"
    }
  ],
  "school_specific": {
    "bagua_map": {
      "wealth": { "present": ["item1", "item2"], "missing": [], "score_contribution": 0-7 },
      "fame": { "present": [], "missing": ["artwork"], "score_contribution": 0-7 },
      "relationships": { "present": [], "missing": [], "score_contribution": 0-7 },
      "family": { "present": [], "missing": [], "score_contribution": 0-7 },
      "health": { "present": [], "missing": [], "score_contribution": 0-7 },
      "creativity": { "present": [], "missing": [], "score_contribution": 0-7 },
      "knowledge": { "present": [], "missing": [], "score_contribution": 0-7 },
      "career": { "present": [], "missing": [], "score_contribution": 0-7 },
      "helpful_people": { "present": [], "missing": [], "score_contribution": 0-7 }
    },
    "entrance_direction": "detected entrance wall direction or unknown",
    "chi_flow_description": "Description of how chi moves through the space"
  }
}

## Important Notes

- Score each category independently based on the rubric
- Issues should be specific and actionable
- Each issue's score_impact should sum with other issues in the same category to equal (max - actual_score) for that category
- Return ONLY valid JSON - no explanation text before or after
- Be strict in applying the rubric - consistent scoring is more important than generous scoring
