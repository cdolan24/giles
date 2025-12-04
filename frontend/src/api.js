// API utility for frontend to connect to backend

export async function searchPapers(query, filters = {}) {
  const params = new URLSearchParams({ q: query });
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== '' && value !== null && value !== undefined) {
      params.append(key, value);
    }
  });
  const res = await fetch(`http://127.0.0.1:8000/api/search?${params.toString()}`);
  return res.json();
}

export async function getMetadata(paperId, library) {
  const params = new URLSearchParams({ library });
  const res = await fetch(`http://127.0.0.1:8000/metadata/${paperId}?${params.toString()}`);
  return res.json();
}
