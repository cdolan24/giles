// API utility for frontend to connect to backend

const API_BASE = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

export async function searchPapers(query, filters = {}) {
  const params = new URLSearchParams({ q: query });
  Object.entries(filters).forEach(([key, value]) => {
    // Unchecked checkboxes mean "no filter", not "must be false"
    if (value !== '' && value !== null && value !== undefined && value !== false) {
      params.append(key, value);
    }
  });
  const res = await fetch(`${API_BASE}/search?${params.toString()}`);
  return res.json();
}

export async function getMetadata(paperId, library) {
  const params = new URLSearchParams({ library });
  const res = await fetch(`${API_BASE}/metadata/${encodeURIComponent(paperId)}?${params.toString()}`);
  return res.json();
}
