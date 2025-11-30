// Basic chat popup logic placeholder
const root = document.getElementById('root');
root.innerHTML = `
  <h2>UC Library Chat</h2>
  <input id="chatInput" type="text" placeholder="Ask about a field of study..." style="width:80%" />
  <button id="sendBtn">Send</button>
  <div id="messages" style="margin-top:16px;"></div>
`;

document.getElementById('sendBtn').onclick = () => {
  const input = document.getElementById('chatInput').value;
  if (!input.trim()) return;
  const messages = document.getElementById('messages');
  messages.innerHTML += `<div style='text-align:right;'>${input}</div>`;
  document.getElementById('chatInput').value = '';
  // TODO: Connect to backend API and display response
};
