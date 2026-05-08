Analyze this room photo and return a JSON object.
Room dimensions: {room_dimensions}
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
