You have received element detection results from a room photo, along with the room dimensions.

Room dimensions: {room_length}m x {room_width}m

Extraction result:
{extraction_json}

Your task: Produce a {grid_size} room layout grid.

INSTRUCTIONS:
- Create a {grid_size} grid ({N} rows x {N} columns)
- 0,0 = top-left corner of the room (north-west when facing into the room)
- Row 0 represents the NORTH wall/area of the room
- Col 0 represents the WEST wall/area of the room
- {scale_note}
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
{cells_json}

IMPORTANT: Return ONLY the JSON object. No code fences, no explanation, no surrounding text.