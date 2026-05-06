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
