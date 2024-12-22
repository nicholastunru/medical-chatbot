const chatHistory = document.getElementById('chat-history');
const userInput = document.getElementById('user-input');

function appendMessage(sender, message) {
  const chatMessage = document.createElement('div');
  chatMessage.classList.add('chat-message', sender);
  chatMessage.innerHTML = `<div class="message">${message}</div>`;
  chatHistory.appendChild(chatMessage);
  chatHistory.scrollTop = chatHistory.scrollHeight; // Scroll to bottom
}

function showLoadingIndicator() {
  const loading = document.createElement('div');
  loading.classList.add('loading');
  loading.id = 'loading-indicator';
  loading.innerHTML = `<span></span><span></span><span></span>`;
  chatHistory.appendChild(loading);
  chatHistory.scrollTop = chatHistory.scrollHeight;
}

function removeLoadingIndicator() {
  const loadingIndicator = document.getElementById('loading-indicator');
  if (loadingIndicator) loadingIndicator.remove();
}

async function sendMessage() {
  const message = userInput.value.trim();
  if (!message) return;

  // Display user's message
  appendMessage('user', message);
  userInput.value = '';

  // Show loading indicator
  showLoadingIndicator();

  try {
    const response = await fetch('http://127.0.0.1:5000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, user_id: 'default' }),
    });

    const data = await response.json();
    console.log("Server response:", data);

    // Remove loading indicator
    removeLoadingIndicator();

    // Handle restart command (clear chat history)
    if (message.toLowerCase() === 'restart') {
      chatHistory.innerHTML = ''; // Clear the chat history
    }

    // Append the bot's response
    appendMessage('bot', data.response || "I couldn't understand that.");
  } catch (error) {
    console.error("Error:", error);
    removeLoadingIndicator();
    appendMessage('bot', 'Error connecting to the server. Please try again.');
  }
}

// Auto-start chat session with initial question
document.addEventListener("DOMContentLoaded", async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: "restart", user_id: "default" }),
    });

    const data = await response.json();
    appendMessage('bot', data.response || "Hello! What symptom are you experiencing?");
  } catch (error) {
    console.error("Error:", error);
    appendMessage('bot', 'Error connecting to the server. Please try again.');
  }
});
