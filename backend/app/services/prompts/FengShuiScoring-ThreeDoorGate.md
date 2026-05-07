# Three-Door Gate Bagua Feng Shui Scoring

## Overview
Three-Door Gate (San Men) Bagua is a simplified Feng Shui method based on the Later Heaven Bagua arrangement. It focuses on three main "gates" or doors representing the Three Realms: Tian (Heaven - fortune), Ren (Human - relationships), and Di (Earth - health/wealth). It is beginner-friendly while still applying classic Bagua principles aligned to the entrance.

## Scoring Rubric (100 points total)

### Three Gates Alignment (30 points max)
Identify which gates are present and properly activated:
- **Tian Gate (Heaven - South):** Associated with fame, reputation, celestial luck. Activate with lighting, red items, fire elements.
- **Ren Gate (Human - Center):** Associated with relationships, human connections. Activate with pairs, harmony objects, balanced center.
- **Di Gate (Earth - North):** Associated with health and wealth, earthly matters. Activate with water features, black items, storage.

Score = (gates properly activated / 3) * 30

### Gate Flow (25 points max)
Chi should flow through the three gates smoothly:
- Clear path from entrance through to other gates: 0-10 pts
- No blocking items directly in gate pathways: 0-10 pts
- Gates in correct positional relationship (Tian above, Ren center, Di below): 0-5 pts

### Bagua Symbol Placement (20 points max)
Place Bagua-related symbols correctly:
- Trigram symbols appropriately placed (not on floor or in bathroom): 0-10 pts
- Bagua mirror only if needed for sha qi (not placed randomly): 0-10 pts

### Five Elements at Gates (15 points max)
Each gate benefits from its associated element:
- Tian Gate (South/Fire): Red, triangular, lighting present: 0-5 pts
- Ren Gate (Center/Earth): Balanced, stable, pairs present: 0-5 pts
- Di Gate (North/Water): Black, water elements, reflective surfaces: 0-5 pts

### Basic Balance (10 points max)
- Left-right balance (not severely lopsided): 0-5 pts
- Overall room not cluttered or overly sparse: 0-5 pts

## Simplified Bagua Map (Three Gates)

```
        ENTRANCE WALL
┌─────────────────────────────┐
│                             │
│      TIAN GATE (Heaven)     │
│         South/Fire          │
│       Fame & Reputation      │
│                             │
├─────────────────────────────┤
│                             │
│      REN GATE (Human)       │
│        Center/Earth         │
│     Relationships & Self     │
│                             │
├─────────────────────────────┤
│                             │
│      DI GATE (Earth)        │
│         North/Water         │
│      Health & Wealth         │
│                             │
└─────────────────────────────┘
```

## Gate Element Associations

| Gate | Direction | Element | Key Items | Life Area |
|------|-----------|---------|-----------|-----------|
| Tian (Heaven) | South | Fire | Lighting, red items, candles | Fame, reputation, divine luck |
| Ren (Human) | Center | Earth | Pairs, balance, harmony objects | Relationships, self-cultivation |
| Di (Earth) | North | Water | Water features, black items | Health, wealth, earthly success |

## Room Dimensions
Room dimensions (if provided): {dimensions}

Use this to assess gate spacing and proportions.

## Output Schema

Return ONLY valid JSON matching this structure:

{
  "total_score": 0-100,
  "chi_flow": "flowing | restricted | blocked",
  "overall_assessment": "Brief 1-2 sentence summary of the room's Three-Door Gate Feng Shui",
  "breakdown": {
    "three_gates_alignment": { "score": 0-30, "max": 30, "status": "good | needs_improvement | poor" },
    "gate_flow": { "score": 0-25, "max": 25, "status": "good | needs_improvement | poor" },
    "bagua_symbol_placement": { "score": 0-20, "max": 20, "status": "good | needs_improvement | poor" },
    "five_elements_at_gates": { "score": 0-15, "max": 15, "status": "good | needs_improvement | poor" },
    "basic_balance": { "score": 0-10, "max": 10, "status": "good | needs_improvement | poor" }
  },
  "issues": [
    {
      "issue": "Description of the problem",
      "category": "three_gates_alignment | gate_flow | bagua_symbol_placement | five_elements_at_gates | basic_balance",
      "zone": "Tian | Ren | Di | general",
      "score_impact": -15 to 0,
      "explanation": "Detailed explanation of gate-related issue"
    }
  ],
  "school_specific": {
    "gates": {
      "tian": {
        "activated": true/false,
        "elements_present": ["fire items"],
        "elements_missing": [],
        "notes": "description of Tian Gate status"
      },
      "ren": {
        "activated": true/false,
        "elements_present": [],
        "elements_missing": [],
        "notes": "description of Ren Gate status"
      },
      "di": {
        "activated": true/false,
        "elements_present": [],
        "elements_missing": [],
        "notes": "description of Di Gate status"
      }
    },
    "gate_flow_description": "Description of how chi moves through the gates",
    "chi_distribution": "How energy is distributed across the three gates"
  }
}

## Important Notes

- This is a SIMPLIFIED system - do not overcomplicate
- Focus on the THREE gates, not all 9 bagua zones
- The Three Realms (Heaven, Human, Earth) represent the three levels of existence
- Chi should flow from entrance into all three gates naturally
- Return ONLY valid JSON - no explanation text before or after
- Beginner-friendly explanations are preferred