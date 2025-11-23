const chat = document.getElementById('chat');
const form = document.getElementById('chat-form');
const messageInput = document.getElementById('message');

// Get user_id from URL query parameters, default to 1 if not present
const urlParams = new URLSearchParams(window.location.search);
const userId = parseInt(urlParams.get('user_id')) || 1;

function appendMessage(text, cls) {
  const el = document.createElement('div');
  el.className = 'message ' + cls;
  el.textContent = text;
  chat.appendChild(el);
  chat.scrollTop = chat.scrollHeight;
}

async function loadHistory() {
  try {
    const res = await fetch(`/history/${userId}`);
    if (!res.ok) throw new Error('Failed to load history');
    const data = await res.json();
    
    data.history.forEach(msg => {
      // Map 'chatbot' to 'bot' class for styling
      const cls = msg.sender === 'chatbot' ? 'bot' : 'user';
      appendMessage(msg.message, cls);
    });
  } catch (err) {
    console.error('Error loading history:', err);
    appendMessage('Error loading history.', 'bot');
  }
}

// Load history on page load
loadHistory();

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const msg = messageInput.value.trim();
  if (!msg) return;
  appendMessage(msg, 'user');
  messageInput.value = '';

  appendMessage('...', 'bot');
  const botPlaceholder = chat.lastElementChild;

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg, user_id: userId }),
    });
    if (!res.ok) throw new Error('Server error');
    const data = await res.json();
    botPlaceholder.textContent = data.reply;
  } catch (err) {
    botPlaceholder.textContent = 'Error: ' + err.message;
  }
});