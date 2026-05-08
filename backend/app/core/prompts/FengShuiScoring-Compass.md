# Compass School (Li Qi Pai) Feng Shui Scoring

## Overview
Compass School is a collection of traditional Feng Shui techniques that use compass directions and time factors. The two main methods are Flying Star (Xuan Kong) and Eight Mansions (Ba Zhai). This school requires specific data for full calculation but can still provide partial analysis without it.

**IMPORTANT:** This school requires additional data for complete scoring:
- `building_date` (YYYY-MM-DD): Required for Flying Star calculations
- `birth_date` (YYYY-MM-DD): Required for Eight Mansions Kua calculations
- `kua_number` (1-9): Required for Eight Mansions favorable directions

If this data is not provided, return a PARTIAL score with missing_data flag. Focus scoring on form and visible elements only.

## Scoring Rubric (100 points total)

### Orientation Assessment (25 points max) - PARTIAL WITHOUT COMPASS
**Note:** Without compass reading, assess based on visible orientation clues:
- Entrance position relative to room layout (inferred): 0-10 pts
- Window positions suggesting direction (light source direction): 0-10 pts
- Furniture orientation relative to natural light flow: 0-5 pts

### Eight Mansions Basics (25 points max) - REQUIRES KUA OR BIRTH DATE
If kua_number provided:
- Determine East Group (Kua 1,3,4,9) or West Group (Kua 2,5,6,7,8)
- Evaluate if main furniture faces favorable directions: 0-15 pts
- Check if harmful directions are exposed: 0-10 pts

If kua_number NOT provided (partial):
- Evaluate general auspicious/inauspicious placements: 0-10 pts
- Return partial score with flag

### Flying Star Basics (25 points max) - REQUIRES BUILDING DATE
If building_date provided:
- Calculate current period flying star chart
- Evaluate present star combinations in key positions: 0-15 pts
- Check for sha qi (poison arrows) from star positions: 0-10 pts

If building_date NOT provided (partial):
- Evaluate visible sha qi (sharp angles pointing at property): 0-10 pts
- Return partial score with flag

### Form and Landscape (15 points max) - ALWAYS APPLICABLE
- Visible terrain features outside windows: 0-5 pts
- Building shape relative to neighbors: 0-5 pts
- Road or water flow approaching the property: 0-5 pts

### Five Elements in Compass Context (10 points max) - ALWAYS APPLICABLE
- Element balance with directional emphasis (based on visible elements): 0-10 pts

## Compass School Key Concepts

### Eight Mansions Group Determination
**East Group** (favorable directions: East, Southeast, South, North):
- Kua 1 (Water), Kua 3 (Wood), Kua 4 (Wood), Kua 9 (Fire)

**West Group** (favorable directions: West, Northwest, Southwest, Northeast):
- Kua 2 (Earth), Kua 5 (Earth - varies), Kua 6 (Metal), Kua 7 (Metal), Kua 8 (Earth)

### Flying Star Period System
- Current period: 9th Period (2004-2084)
- Each building has unique star chart based on facing direction and construction date
- 9-star grid affects fortune in different areas

### Sha Qi (Poison Arrow) Sources
- Sharp corner of another building pointing at entrance
- T-shaped intersection facing the property
- Electricity pylons near windows
- Dead trees or bare structures

## Room Dimensions
Room dimensions (if provided): {dimensions}

## Additional Data (if provided)

Building date: {building_date}
Birth date: {birth_date}
Kua number: {kua_number}

Use this data if available. If not, note as missing and provide partial score.

## Output Schema

Return ONLY valid JSON matching this structure:

{
  "total_score": 0-100,
  "chi_flow": "flowing | restricted | blocked",
  "overall_assessment": "Brief 1-2 sentence summary of the room's Compass School Feng Shui",
  "breakdown": {
    "orientation_assessment": { "score": 0-25, "max": 25, "status": "good | needs_improvement | poor" },
    "eight_mansions": { "score": 0-25, "max": 25, "status": "good | needs_improvement | partial", "note": "requires kua_number" },
    "flying_star": { "score": 0-25, "max": 25, "status": "good | needs_improvement | partial", "note": "requires building_date" },
    "form_and_landscape": { "score": 0-15, "max": 15, "status": "good | needs_improvement | poor" },
    "five_elements_compass": { "score": 0-10, "max": 10, "status": "good | needs_improvement | poor" }
  },
  "missing_data": ["building_date", "birth_date", "kua_number"],
  "issues": [
    {
      "issue": "Description of the problem",
      "category": "orientation | eight_mansions | flying_star | form_landscape | five_elements",
      "score_impact": -15 to 0,
      "explanation": "Detailed explanation"
    }
  ],
  "school_specific": {
    "compass_school_type": "flying_star | eight_mansions | mixed",
    "facing_direction": "estimated or unknown",
    "eight_mansions": {
      "kua_number": 0,
      "group": "east | west | unknown",
      "favorable_directions": ["east", "southeast"],
      "unfavorable_directions": ["west", "northwest"],
      "main_door_facing": "favorable | unfavorable | unknown"
    },
    "flying_star": {
      "building_date": "provided or unknown",
      "period": 9,
      "mountain_star": 0,
      "water_star": 0,
      "current_period_stars": {}
    },
    "sha_qi_sources": [
      {
        "source": "description",
        "direction_from": "direction",
        "affected_area": "area affected"
      }
    ]
  }
}

## Important Notes

- Compass School is the MOST COMPLEX traditional Feng Shui system
- Without proper data, complete scoring is NOT possible
- Always return missing_data array listing what is needed for full score
- Provide as complete a score as possible with available information
- Focus on VISIBLE sha qi sources even without full compass data
- Eight Mansions and Flying Star are separate but often used together
- Return ONLY valid JSON - no explanation text before or after