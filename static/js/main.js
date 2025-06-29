const chatWindow = document.getElementById('chat-window');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');

let messages = [
    {
        role: "system",
        content: "You are a helpful geography expert. Answer questions about Earth, geography, countries, landforms, and provide the latest statistics if possible. If you are unsure or your information may be outdated, mention it."
    }
];

function appendMessage(role, content) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message ' + (role === 'user' ? 'user' : 'bot');
    msgDiv.textContent = content;
    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const userMsg = userInput.value.trim();
    if (!userMsg) return;
    appendMessage('user', userMsg);
    messages.push({ role: 'user', content: userMsg });
    userInput.value = '';
    appendMessage('bot', '...');
    chatWindow.scrollTop = chatWindow.scrollHeight;

    // Keep only last 6 messages + system
    if (messages.length > 7) {
        messages = [messages[0]].concat(messages.slice(-6));
    }

    try {
        const res = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ messages })
        });
        const data = await res.json();
        // Remove the '...' placeholder
        chatWindow.removeChild(chatWindow.lastChild);
        appendMessage('bot', data.response);
        messages.push({ role: 'assistant', content: data.response });
    } catch (err) {
        chatWindow.removeChild(chatWindow.lastChild);
        appendMessage('bot', 'Error: Could not reach the chatbot.');
    }
});
