import axios from "axios";

const client = axios.create({ baseURL: "/v1" });

export const evaluateRoom = (imageBase64, dimensions) =>
  client.post("/evaluate", { image: imageBase64, dimensions });

export const getSuggestions = (sessionId) =>
  client.post("/suggest", { session_id: sessionId });

export const addElement = (sessionId, element) =>
  client.post("/add-element", { session_id: sessionId, element });