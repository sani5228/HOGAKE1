/**
 * FASAL AI & Rule-Based FAQ Chatbot Widget
 * Injected automatically or manually on any portal page.
 */

(function initChatbot() {
    // Only initialize once
    if (document.getElementById('fasal-chatbot-root')) return;

    const root = document.createElement('div');
    root.id = 'fasal-chatbot-root';
    root.innerHTML = `
        <div class="chatbot-bubble" id="chatbotToggle" title="Need help? Ask FASAL Assistant">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
        </div>

        <div class="chatbot-window" id="chatbotWindow">
            <div class="chat-header">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.2rem;">🌾</span>
                    <span>FASAL Sahayak (Assistant)</span>
                </div>
                <button id="chatbotClose" style="background:none; border:none; color:#fff; font-size:1.2rem; cursor:pointer;">✕</button>
            </div>
            
            <div class="chat-body" id="chatBody">
                <div class="chat-msg bot">
                    Namaste! I am the FASAL Assistant. How can I help you with slot booking, centers, MSP rates, or payments today?
                </div>
                <div id="quickIntentsContainer" class="chat-quick-intents">
                    <!-- Populated dynamically -->
                </div>
            </div>

            <div class="chat-footer">
                <input type="text" id="chatInput" placeholder="Type your query here..." autocomplete="off">
                <button id="chatSendBtn">Send</button>
            </div>
        </div>
    `;

    document.body.appendChild(root);

    const toggleBtn = document.getElementById('chatbotToggle');
    const closeBtn = document.getElementById('chatbotClose');
    const windowEl = document.getElementById('chatbotWindow');
    const bodyEl = document.getElementById('chatBody');
    const inputEl = document.getElementById('chatInput');
    const sendBtn = document.getElementById('chatSendBtn');
    const intentsContainer = document.getElementById('quickIntentsContainer');

    function toggleChat() {
        const isActive = windowEl.classList.toggle('active');
        if (isActive) {
            inputEl.focus();
            bodyEl.scrollTop = bodyEl.scrollHeight;
        }
    }

    toggleBtn.addEventListener('click', toggleChat);
    closeBtn.addEventListener('click', toggleChat);

    function addMessage(text, isUser = false) {
        const msg = document.createElement('div');
        msg.className = `chat-msg ${isUser ? 'user' : 'bot'}`;
        msg.textContent = text;
        bodyEl.appendChild(msg);
        bodyEl.scrollTop = bodyEl.scrollHeight;
    }

    async function handleSend(queryText = null) {
        const query = (queryText || inputEl.value).trim();
        if (!query) return;

        addMessage(query, true);
        if (!queryText) inputEl.value = '';

        try {
            const res = await api.queryChatbot(query);
            if (res.data && res.data.response) {
                addMessage(res.data.response, false);
            } else {
                addMessage("I'm sorry, I couldn't find an answer for that. Please contact our toll-free helpline at 1800-FASAL-2026.", false);
            }
        } catch (err) {
            addMessage("Unable to reach assistant service at the moment. Please try again later.", false);
        }
    }

    sendBtn.addEventListener('click', () => handleSend());
    inputEl.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSend();
    });

    // Load initial quick FAQ intents
    async function loadIntents() {
        try {
            const res = await api.getChatbotIntents();
            if (res.data && Array.isArray(res.data)) {
                intentsContainer.innerHTML = '';
                res.data.slice(0, 4).forEach(item => {
                    const btn = document.createElement('button');
                    btn.className = 'intent-btn';
                    btn.textContent = item.label || item.query;
                    btn.addEventListener('click', () => handleSend(item.query || item.label));
                    intentsContainer.appendChild(btn);
                });
            }
        } catch (e) {
            // Default fallback chips
            const fallbackQueries = [
                "How is my slot scheduled?",
                "How is MSP payment calculated?",
                "Can I cancel or rebook?",
                "What is the IVR toll-free number?"
            ];
            intentsContainer.innerHTML = '';
            fallbackQueries.forEach(q => {
                const btn = document.createElement('button');
                btn.className = 'intent-btn';
                btn.textContent = q;
                btn.addEventListener('click', () => handleSend(q));
                intentsContainer.appendChild(btn);
            });
        }
    }

    loadIntents();
})();
