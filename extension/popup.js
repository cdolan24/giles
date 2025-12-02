
const root = document.getElementById('root');
root.innerHTML = `
  <h2>UC Library Chat</h2>
  <input id="chatInput" type="text" placeholder="Ask about a field of study..." style="width:80%" />
  <button id="sendBtn">Send</button>
  <div id="messages" style="margin-top:16px;"></div>
`;

async function queryBackend(input) {
  try {
    // Change the URL if your backend is deployed elsewhere
    const url = `http://127.0.0.1:8000/search?q=${encodeURIComponent(input)}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Backend error');
    const data = await response.json();
    return data;
  } catch (err) {
    return { error: err.message };
  }
}

document.getElementById('sendBtn').onclick = async () => {
  const input = document.getElementById('chatInput').value;
  if (!input.trim()) return;
  const messages = document.getElementById('messages');
  messages.innerHTML += `<div style='text-align:right;'>${input}</div>`;
  document.getElementById('chatInput').value = '';
  messages.innerHTML += `<div style='color:gray;'>Searching...</div>`;
  const result = await queryBackend(input);
  if (result.error) {
    messages.innerHTML += `<div style='color:red;'>Error: ${result.error}</div>`;
  } else {
    messages.innerHTML += `<div style='text-align:left;'><pre>${JSON.stringify(result, null, 2)}</pre></div>`;
  }
};
