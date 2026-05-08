You have received element detection results from a room photo, along with the room dimensions.

Room dimensions: {room_length}m x {room_width}m

Extraction result:
{extraction_json}

Your task: Produce a 4x4 room layout grid.

INSTRUCTIONS:
- Create a 4x4 grid (16 cells, 4 rows x 4 columns)
- 0,0 = top-left corner of the room (north-west when facing into the room)
- Row 0 represents the NORTH wall/area of the room
- Col 0 represents the WEST wall/area of the room
- Each cell represents approximately 1/4 of the room
- Scale furniture using room dimensions. A standard:
  - Bed: ~1.5-2m long, ~0.9-1.6m wide
  - Sofa: ~2-2.5m long, ~0.8-1m wide
  - Armchair: ~0.8-1m square
  - Dining table: ~1.2-1.8m long
  - Coffee table: ~1-1.4m long
  - Bookshelf: ~0.8-1.2m wide
  - Plant: ~0.3-0.6m wide
- If a furniture item spans multiple cells, repeat its type in ALL cells it occupies
- If a cell has no furniture, write "empty"
- Only use furniture types: bed, sofa, armchair, dining_table, coffee_table, desk, wardrobe, dresser, bookshelf, tv_stand, plant, lamp_floor, lamp_table, lamp_ceiling, mirror, rug, curtains, artwork, door, window, empty
- Return ONLY valid JSON with no markdown fences or additional text

OUTPUT FORMAT:
{{
  "cells": {{
    "0,0": "furniture_type or empty",
    "0,1": "furniture_type or empty",
    "0,2": "furniture_type or empty",
    "0,3": "furniture_type or empty",
    "1,0": "furniture_type or empty",
    "1,1": "furniture_type or empty",
    "1,2": "furniture_type or empty",
    "1,3": "furniture_type or empty",
    "2,0": "furniture_type or empty",
    "2,1": "furniture_type or empty",
    "2,2": "furniture_type or empty",
    "2,3": "furniture_type or empty",
    "3,0": "furniture_type or empty",
    "3,1": "furniture_type or empty",
    "3,2": "furniture_type or empty",
    "3,3": "furniture_type or empty"
  }},
  "grid_size": "4x4"
}}

IMPORTANT: Return ONLY the JSON object. No code fences, no explanation, no surrounding text.