(function() {
    // Basic settings
    const API_URL = "http://localhost:8000/query"; // Later change to your hosted server IP/URL

    // Inject CSS
    const css = `
        #iavc-chat-widget {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
        }

        #iavc-chat-button {
            width: 60px;
            height: 60px;
            border-radius: 30px;
            background: linear-gradient(135deg, #0052D4, #4364F7, #6FB1FC);
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            color: white;
        }

        #iavc-chat-button:hover {
            transform: scale(1.1);
        }

        #iavc-chat-button svg {
            width: 30px;
            height: 30px;
            fill: currentColor;
        }

        #iavc-chat-window {
            position: absolute;
            bottom: 80px;
            right: 0;
            width: 350px;
            height: 500px;
            background: #ffffff;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            display: none;
            flex-direction: column;
            overflow: hidden;
            border: 1px solid #eee;
            animation: iavcFadeIn 0.3s ease-out;
        }

        @keyframes iavcFadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        #iavc-chat-header {
            background: linear-gradient(135deg, #0052D4, #4364F7);
            color: white;
            padding: 15px 20px;
            font-size: 16px;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        #iavc-chat-header-close {
            cursor: pointer;
            font-size: 20px;
            line-height: 1;
            opacity: 0.8;
            transition: opacity 0.2s;
        }
        
        #iavc-chat-header-close:hover {
            opacity: 1;
        }

        #iavc-chat-messages {
            flex-grow: 1;
            padding: 15px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
            background: #fafafa;
        }

        .iavc-message {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 12px;
            font-size: 14px;
            line-height: 1.5;
            word-wrap: break-word;
        }

        .iavc-message.bot {
            align-self: flex-start;
            background: #ffffff;
            color: #333;
            border: 1px solid #eee;
            box-shadow: 0 2px 5px rgba(0,0,0,0.02);
            border-bottom-left-radius: 4px;
        }

        .iavc-message.user {
            align-self: flex-end;
            background: #4364F7;
            color: white;
            border-bottom-right-radius: 4px;
        }

        .iavc-loading {
            align-self: flex-start;
            display: flex;
            gap: 4px;
            padding: 12px 16px;
            background: #ffffff;
            border: 1px solid #eee;
            border-radius: 12px;
            border-bottom-left-radius: 4px;
            display: none;
        }

        .iavc-dot {
            width: 8px;
            height: 8px;
            background: #4364F7;
            border-radius: 50%;
            animation: iavcBounce 1.4s infinite ease-in-out both;
        }
        .iavc-dot:nth-child(1) { animation-delay: -0.32s; }
        .iavc-dot:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes iavcBounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }

        #iavc-chat-input-area {
            display: flex;
            padding: 12px;
            background: #ffffff;
            border-top: 1px solid #eee;
            gap: 8px;
        }

        #iavc-chat-input {
            flex-grow: 1;
            border: 1px solid #ddd;
            border-radius: 20px;
            padding: 10px 15px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }

        #iavc-chat-input:focus {
            border-color: #4364F7;
        }

        #iavc-chat-submit {
            background: #4364F7;
            color: white;
            border: none;
            border-radius: 20px;
            padding: 0 18px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.2s;
            font-size: 14px;
        }

        #iavc-chat-submit:hover {
            background: #0052D4;
        }
    `;

    // Inject CSS
    const styleEl = document.createElement('style');
    styleEl.innerHTML = css;
    document.head.appendChild(styleEl);

    // Create Widget DOM
    const widgetEl = document.createElement('div');
    widgetEl.id = 'iavc-chat-widget';
    
    // Icon SVG (Chat Bubble)
    const chatIcon = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2Zm0 14H6l-2 2V4h16v12Z"/></svg>`;

    widgetEl.innerHTML = `
        <div id="iavc-chat-window">
            <div id="iavc-chat-header">
                <div>IAVC World Assistant</div>
                <div id="iavc-chat-header-close">&times;</div>
            </div>
            <div id="iavc-chat-messages">
                <div class="iavc-message bot">Hallo! Ich bin dein KI-Assistent für IAVC World. Frag mich etwas über unsere Artikel!</div>
                <div class="iavc-loading" id="iavc-chat-loading">
                    <div class="iavc-dot"></div><div class="iavc-dot"></div><div class="iavc-dot"></div>
                </div>
            </div>
            <div id="iavc-chat-input-area">
                <input type="text" id="iavc-chat-input" placeholder="Stelle eine Frage..." autocomplete="off">
                <button id="iavc-chat-submit">Senden</button>
            </div>
        </div>
        <div id="iavc-chat-button">
            ${chatIcon}
        </div>
    `;

    document.body.appendChild(widgetEl);

    // Logic
    const btnBox = document.getElementById('iavc-chat-button');
    const windowBox = document.getElementById('iavc-chat-window');
    const closeBtn = document.getElementById('iavc-chat-header-close');
    const submitBtn = document.getElementById('iavc-chat-submit');
    const inputField = document.getElementById('iavc-chat-input');
    const msgContainer = document.getElementById('iavc-chat-messages');
    const loadingEl = document.getElementById('iavc-chat-loading');

    // Toggle window
    btnBox.addEventListener('click', () => {
        windowBox.style.display = windowBox.style.display === 'flex' ? 'none' : 'flex';
        inputField.focus();
    });

    closeBtn.addEventListener('click', () => {
        windowBox.style.display = 'none';
    });

    // Send Message Function
    async function sendMessage() {
        const text = inputField.value.trim();
        if(!text) return;

        // User Message UI
        const userMsg = document.createElement('div');
        userMsg.className = 'iavc-message user';
        userMsg.innerText = text;
        msgContainer.insertBefore(userMsg, loadingEl);
        
        inputField.value = '';
        msgContainer.scrollTop = msgContainer.scrollHeight;

        // Backend Request
        loadingEl.style.display = 'flex';
        msgContainer.scrollTop = msgContainer.scrollHeight;

        try {
            const res = await fetch(API_URL, {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "X-API-KEY": "your-secret-api-key-here" // Match with backend
                },
                body: JSON.stringify({ user_query: text })
            });
            const data = await res.json();
            
            // Bot Message UI
            const botMsg = document.createElement('div');
            botMsg.className = 'iavc-message bot';
            
            if(data.answer) {
                botMsg.innerText = data.answer;
                
                // Add sources if available
                if(data.sources && data.sources.length > 0) {
                    const sourceHTML = data.sources.map(s => 
                        `<a href="${s.url}" target="_blank" style="color: #4364F7; text-decoration: none; display: block; margin-top: 5px; font-size: 12px;">🔗 ${s.title} (${s.firma || 'IAVC'})</a>`
                    ).join('');
                    botMsg.innerHTML += `<div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #eee; font-size: 12px; font-weight: bold;">Quellen:</div>${sourceHTML}`;
                }
            } else {
                botMsg.innerText = "Entschuldigung, es gab einen Fehler bei der KI-Generierung.";
            }

            loadingEl.style.display = 'none';
            msgContainer.insertBefore(botMsg, loadingEl);
            msgContainer.scrollTop = msgContainer.scrollHeight;

        } catch (err) {
            loadingEl.style.display = 'none';
            const errorMsg = document.createElement('div');
            errorMsg.className = 'iavc-message bot';
            errorMsg.innerText = "Konnte keine Verbindung zum Backend herstellen.";
            msgContainer.insertBefore(errorMsg, loadingEl);
            msgContainer.scrollTop = msgContainer.scrollHeight;
        }
    }

    submitBtn.addEventListener('click', sendMessage);
    inputField.addEventListener('keypress', (e) => {
        if(e.key === 'Enter') sendMessage();
    });

})();
