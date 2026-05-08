# Five Elements (Wu Xing) Feng Shui Scoring

## Overview
Five Elements Feng Shui focuses purely on the balance of the five elemental energies: Wood, Fire, Earth, Metal, and Water. Unlike other schools that use Bagua zones, this approach evaluates a room solely based on the elemental composition and interactions. The goal is harmonious elemental balance where no single element dominates or is completely absent.

## Element Interactions

### Generating Cycle (Promoting)
Each element nurtures the next:
- Wood feeds Fire
- Fire creates Earth (ash)
- Earth bears Metal
- Metal collects Water
- Water nourishes Wood

### Controlling Cycle (Subduing)
Each element can control another:
- Wood parts Earth
- Earth blocks Water
- Water extinguishes Fire
- Fire melts Metal
- Metal cuts Wood

A balanced room should have elements in healthy generating relationships, not fighting each other.

## Scoring Rubric (100 points total)

### Element Presence (30 points max)
Count how many of the five elements are present in the room:
- Wood: plants, flowers, green items, wood furniture, bamboo, bookshelves
- Fire: lamps, candles, fireplace, red items, electronics, TV
- Earth: crystals, ceramics, stone, pottery, rugs, brown/yellow items
- Metal: mirrors, metal furniture, white items, silver/gold decor, knives
- Water: windows, water features, aquarium, black items, reflective surfaces

Score:
- 5 elements = 30 pts
- 4 elements = 24 pts
- 3 elements = 18 pts
- 2 elements = 12 pts
- 1 element = 6 pts
- 0 elements = 0 pts

### Element Distribution Balance (25 points max)
Elements should be distributed, not clustered in one area:
- No single element dominating one corner: 0-10 pts
- Elements spread across room: 0-10 pts
- Each element has breathing space (not crowded): 0-5 pts

### Generating Cycle Harmony (20 points max)
Check if elements support each other in the generating cycle:
- Wood near Fire (wood feeds fire): 0-5 pts
- Fire near Earth (fire creates ash): 0-5 pts
- Earth near Metal (earth bears metal): 0-5 pts
- Metal near Water (metal collects water): 0-5 pts
- Water near Wood (water nourishes wood): 0-5 pts

### Controlling Cycle Avoidance (15 points max)
Ensure no elements are in conflict:
- Wood not directly clashing with Metal: 0-5 pts
- Fire not directly clashing with Water: 0-5 pts
- Earth not directly clashing with Wood: 0-5 pts

### Color and Shape Harmony (10 points max)
- Colors match their element (Wood=green, Fire=red, Earth=yellow, Metal=white, Water=black): 0-5 pts
- Shapes match their element (Wood=tall/vertical, Fire=triangular, Earth=square, Metal=round, Water=wavy): 0-5 pts

## Element Classifications

| Element | Colors | Shapes | Furniture Types |
|---------|--------|--------|----------------|
| Wood | Green, brown | Tall, vertical, pillar | plant, bookshelf, wardrobe, dresser, indoor tree |
| Fire | Red, orange, purple | Triangular, pointed, angular | lamp, candle, fireplace, tv, red decor |
| Earth | Yellow, brown, terracotta | Square, flat, stable | rug, ceramic, crystal, stone, pottery |
| Metal | White, silver, gold | Round, circular, spherical | mirror, metal table, metal frame, white decor |
| Water | Black, blue | Wavy, flowing, curved | window, aquarium, water feature, black decor |

## Room Dimensions
Room dimensions (if provided): {dimensions}

Use proportions to check if one element is oversized for the space.

## Output Schema

Return ONLY valid JSON matching this structure:

{
  "total_score": 0-100,
  "chi_flow": "flowing | restricted | blocked",
  "overall_assessment": "Brief 1-2 sentence summary of the room's Five Elements balance",
  "breakdown": {
    "element_presence": { "score": 0-30, "max": 30, "status": "good | needs_improvement | poor" },
    "element_distribution": { "score": 0-25, "max": 25, "status": "good | needs_improvement | poor" },
    "generating_cycle": { "score": 0-20, "max": 20, "status": "good | needs_improvement | poor" },
    "controlling_cycle": { "score": 0-15, "max": 15, "status": "good | needs_improvement | poor" },
    "color_shape_harmony": { "score": 0-10, "max": 10, "status": "good | needs_improvement | poor" }
  },
  "issues": [
    {
      "issue": "Description of the problem",
      "category": "element_presence | element_distribution | generating_cycle | controlling_cycle | color_shape_harmony",
      "element_affected": "wood | fire | earth | metal | water | multiple",
      "score_impact": -15 to 0,
      "explanation": "Detailed explanation of how this elemental imbalance affects the room"
    }
  ],
  "school_specific": {
    "elements": {
      "wood": {
        "present": true/false,
        "items": ["sofa", "plant"],
        "dominant": true/false,
        "color_match": true/false,
        "shape_match": true/false
      },
      "fire": {
        "present": true/false,
        "items": [],
        "dominant": true/false,
        "color_match": true/false,
        "shape_match": true/false
      },
      "earth": {
        "present": true/false,
        "items": [],
        "dominant": true/false,
        "color_match": true/false,
        "shape_match": true/false
      },
      "metal": {
        "present": true/false,
        "items": [],
        "dominant": true/false,
        "color_match": true/false,
        "shape_match": true/false
      },
      "water": {
        "present": true/false,
        "items": [],
        "dominant": true/false,
        "color_match": true/false,
        "shape_match": true/false
      }
    },
    "cycle_analysis": {
      "generating_pairs": [["wood", "fire"], ["fire", "earth"]],
      "conflicting_pairs": [],
      "missing_generating_links": []
    },
    "dominant_element": "wood | fire | earth | metal | water | balanced",
    "missing_elements": ["fire"]
  }
}

## Important Notes

- Focus purely on the FIVE ELEMENTS - no bagua zones
- Elemental harmony is more important than having all elements
- A dominant element is not necessarily bad (depends on room purpose)
- Watch for conflict pairs: Wood-Metal, Fire-Water, Earth-Wood
- A balanced room has all 5 elements in proportion
- Return ONLY valid JSON - no explanation text before or after
