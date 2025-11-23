const chat = document.getElementById('chat');
const form = document.getElementById('chat-form');
const messageInput = document.getElementById('message');
const fileInput = document.getElementById('file-input');
const attachBtn = document.getElementById('attach-btn');
const filePreview = document.getElementById('file-preview');

// Get user_id from URL query parameters, default to 1 if not present
const urlParams = new URLSearchParams(window.location.search);
const userId = parseInt(urlParams.get('user_id')) || 1;

let selectedFile = null;

// Attach Button Click
attachBtn.addEventListener('click', () => {
  fileInput.click();
});

// File Input Change
fileInput.addEventListener('change', (e) => {
  if (e.target.files.length > 0) {
    selectedFile = e.target.files[0];
    filePreview.textContent = `Selected: ${selectedFile.name}`;
    filePreview.style.display = 'block';
  } else {
    selectedFile = null;
    filePreview.style.display = 'none';
  }
});

function appendMessage(text, cls, filePath = null, mediaType = null) {
  const el = document.createElement('div');
  el.className = 'message ' + cls;

  // Text content
  const textNode = document.createElement('div');
  textNode.textContent = text;
  el.appendChild(textNode);

  // Media content
  if (filePath && mediaType) {
    if (mediaType.startsWith('image/')) {
      const img = document.createElement('img');
      // In a real app, we'd serve this via a static route or blob URL. 
      // Since we are local, we might need a way to serve the uploaded file.
      // The backend saves to "upload file" dir. We need to make sure this dir is served.
      // We'll assume the backend serves it or we use a relative path if served via static.
      // Wait, "upload file" dir is NOT served by StaticFiles in main.py.
      // I need to update main.py to serve this directory or move uploads to static/uploads.
      // For now, I'll assume I'll fix main.py in the next step or use a placeholder.
      // Actually, I should fix main.py to serve the uploads directory.
      // Let's assume I will mount "/uploads" to "upload file".
      const relativePath = filePath.split('\\').pop().split('/').pop();
      img.src = `/uploads/${relativePath}`;
      img.className = 'chat-image';
      el.appendChild(img);
    } else {
      const link = document.createElement('a');
      const relativePath = filePath.split('\\').pop().split('/').pop();
      link.href = `/uploads/${relativePath}`;
      link.textContent = `📎 Attached File (${mediaType})`;
      link.className = 'chat-file';
      link.target = '_blank';
      el.appendChild(link);
    }
  }

  chat.appendChild(el);
  chat.scrollTop = chat.scrollHeight;
}

async function loadHistory() {
  try {
    const res = await fetch(`/history/${userId}`);
    if (!res.ok) throw new Error('Failed to load history');
    const data = await res.json();

    data.history.forEach(msg => {
      const cls = msg.sender === 'chatbot' ? 'bot' : 'user';
      appendMessage(msg.message, cls, msg.file_path, msg.media_type);
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
  if (!msg && !selectedFile) return;

  // Upload file first if exists
  let uploadedFilePath = null;
  let uploadedMediaType = null;

  if (selectedFile) {
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const uploadRes = await fetch('/upload', {
        method: 'POST',
        body: formData
      });
      if (!uploadRes.ok) throw new Error('Upload failed');
      const uploadData = await uploadRes.json();
      uploadedFilePath = uploadData.file_path;
      uploadedMediaType = uploadData.media_type;
    } catch (err) {
      console.error('Upload error:', err);
      alert('Failed to upload file.');
      return;
    }
  }

  // Display user message immediately
  appendMessage(msg, 'user', uploadedFilePath, uploadedMediaType);

  // Clear input
  messageInput.value = '';
  fileInput.value = '';
  selectedFile = null;
  filePreview.style.display = 'none';

  appendMessage('...', 'bot');
  const botPlaceholder = chat.lastElementChild;

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: msg,
        user_id: userId,
        file_path: uploadedFilePath,
        media_type: uploadedMediaType
      }),
    });
    if (!res.ok) throw new Error('Server error');
    const data = await res.json();

    // Remove placeholder and show actual reply
    chat.removeChild(botPlaceholder);
    appendMessage(data.reply, 'bot');

  } catch (err) {
    botPlaceholder.textContent = 'Error: ' + err.message;
  }
});