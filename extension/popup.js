
const root = document.getElementById('root');
root.innerHTML = `
  <h2>UC Library Chat</h2>
  <input id="chatInput" type="text" placeholder="Ask about a field of study..." style="width:80%" />
  <button id="sendBtn">Send</button>
  <div id="messages" style="margin-top:16px;"></div>
`;

// Change this if your backend is deployed elsewhere (and update host_permissions in manifest.json)
const API_BASE = 'http://127.0.0.1:8000';

async function queryBackend(input) {
  try {
    const url = `${API_BASE}/search?q=${encodeURIComponent(input)}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Backend error');
    return await response.json();
  } catch (err) {
    return { error: err.message };
  }
}

function addMessage(text, style) {
  const div = document.createElement('div');
  div.textContent = text;
  Object.assign(div.style, style);
  document.getElementById('messages').appendChild(div);
  return div;
}

function addResult(paper) {
  const div = document.createElement('div');
  div.style.marginBottom = '8px';
  const title = document.createElement(paper.url ? 'a' : 'strong');
  title.textContent = paper.title;
  if (paper.url) {
    title.href = paper.url;
    title.target = '_blank';
  }
  const meta = document.createElement('div');
  meta.style.color = 'gray';
  meta.textContent = [paper.author, paper.year, paper.source].filter(Boolean).join(' · ');
  div.append(title, meta);
  document.getElementById('messages').appendChild(div);
}

document.getElementById('sendBtn').onclick = async () => {
  const input = document.getElementById('chatInput').value;
  if (!input.trim()) return;
  addMessage(input, { textAlign: 'right' });
  document.getElementById('chatInput').value = '';
  const status = addMessage('Searching...', { color: 'gray' });
  const result = await queryBackend(input);
  status.remove();
  const error = result.error ? result : (Array.isArray(result) && result.find(r => r && r.error));
  if (error) {
    addMessage(`Error: ${error.error}${error.error_code ? ` (${error.error_code})` : ''}`, { color: 'red' });
  } else {
    result.forEach(addResult);
  }
};
