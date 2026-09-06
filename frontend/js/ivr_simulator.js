/**
 * FASAL Interactive Toll-Free IVR Phone Simulator
 * Simulates calling 1800-FASAL-KPK with interactive phone dialer and voice prompts.
 * Adheres strictly to rules.md §16 & PRD.md §10.
 */

(function initIvrSimulator() {
    if (document.getElementById('fasal-ivr-root')) return;

    const root = document.createElement('div');
    root.id = 'fasal-ivr-root';
    root.innerHTML = `
        <div class="ivr-float-btn" id="ivrFloatBtn" title="Simulate Toll-Free Phone Booking (1800-FASAL)">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
            </svg>
            <span>1800-FASAL-KPK</span>
        </div>

        <div class="ivr-modal-overlay" id="ivrModalOverlay" style="display:none;">
            <div class="ivr-phone-handset">
                <div class="phone-top-bar">
                    <span class="carrier">FASAL Telecom (Simulated)</span>
                    <span class="battery">🔋 100%</span>
                    <button class="phone-close-btn" id="ivrCloseBtn">✕</button>
                </div>

                <div class="phone-screen" id="ivrScreen">
                    <div class="phone-header" id="ivrHeader">
                        <div class="phone-number">1800-FASAL-KPK</div>
                        <div class="phone-status" id="ivrCallStatus">Ready to Call</div>
                    </div>

                    <div class="phone-prompt-box" id="ivrPromptBox">
                        <div class="speaker-icon">🔊</div>
                        <div class="prompt-text" id="ivrPromptText">
                            Welcome to FASAL Toll-Free Farmer IVR Booking.<br>
                            Click <strong>Call</strong> to dial from your registered mobile number.
                        </div>
                    </div>

                    <div class="phone-input-display" id="ivrDisplayWrap">
                        <span id="ivrEnteredDigits"></span><span class="blinking-cursor">|</span>
                    </div>

                    <div class="phone-caller-input-wrap" id="ivrCallerWrap">
                        <label>Your Registered Mobile:</label>
                        <input type="tel" id="ivrCallerMobile" value="9826012345" maxlength="10">
                    </div>
                </div>

                <!-- Keypad -->
                <div class="phone-keypad" id="ivrKeypad">
                    <div class="key-row">
                        <button class="key-btn" data-key="1"><span class="digit">1</span><span class="sub">.</span></button>
                        <button class="key-btn" data-key="2"><span class="digit">2</span><span class="sub">ABC</span></button>
                        <button class="key-btn" data-key="3"><span class="digit">3</span><span class="sub">DEF</span></button>
                    </div>
                    <div class="key-row">
                        <button class="key-btn" data-key="4"><span class="digit">4</span><span class="sub">GHI</span></button>
                        <button class="key-btn" data-key="5"><span class="digit">5</span><span class="sub">JKL</span></button>
                        <button class="key-btn" data-key="6"><span class="digit">6</span><span class="sub">MNO</span></button>
                    </div>
                    <div class="key-row">
                        <button class="key-btn" data-key="7"><span class="digit">7</span><span class="sub">PQRS</span></button>
                        <button class="key-btn" data-key="8"><span class="digit">8</span><span class="sub">TUV</span></button>
                        <button class="key-btn" data-key="9"><span class="digit">9</span><span class="sub">WXYZ</span></button>
                    </div>
                    <div class="key-row">
                        <button class="key-btn" data-key="*"><span class="digit">*</span></button>
                        <button class="key-btn" data-key="0"><span class="digit">0</span><span class="sub">+</span></button>
                        <button class="key-btn" data-key="#"><span class="digit">#</span></button>
                    </div>
                </div>

                <!-- Call Control -->
                <div class="phone-call-actions">
                    <button class="call-btn green" id="ivrCallBtn">📞 Call 1800-FASAL</button>
                    <button class="call-btn red" id="ivrEndBtn" style="display:none;">🔴 End Call</button>
                </div>
            </div>
        </div>
    `;

    // Inject Styles for IVR
    const style = document.createElement('style');
    style.textContent = `
        .ivr-float-btn {
            position: fixed;
            bottom: 24px;
            left: 24px;
            background: #4E7A38;
            color: #fff;
            padding: 12px 18px;
            border-radius: 30px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.25);
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            z-index: 9998;
            font-family: 'Inter', sans-serif;
            font-size: 0.88rem;
            font-weight: 600;
            transition: transform 0.2s, background 0.2s;
        }
        .ivr-float-btn:hover { background: #3B2C1F; transform: translateY(-2px); }
        .ivr-modal-overlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.6);
            backdrop-filter: blur(4px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        }
        .ivr-phone-handset {
            width: 320px;
            background: #1C1E1B;
            border-radius: 36px;
            padding: 20px 16px 24px;
            box-shadow: 0 16px 40px rgba(0,0,0,0.5);
            border: 4px solid #333;
            color: #fff;
            font-family: 'Inter', sans-serif;
        }
        .phone-top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.72rem;
            color: #8CAE5C;
            margin-bottom: 12px;
            padding: 0 6px;
        }
        .phone-close-btn {
            background: none; border: none; color: #fff; font-size: 1rem; cursor: pointer;
        }
        .phone-screen {
            background: #262B23;
            border-radius: 16px;
            padding: 14px;
            margin-bottom: 14px;
            min-height: 180px;
            display: flex;
            flex-direction: column;
            border: 1px solid #3E4A38;
        }
        .phone-header { text-align: center; margin-bottom: 8px; }
        .phone-number { font-size: 1.15rem; font-weight: 700; color: #E8B54D; letter-spacing: 0.5px; }
        .phone-status { font-size: 0.75rem; color: #8CAE5C; margin-top: 2px; }
        .phone-prompt-box {
            background: #1A1E17;
            border-radius: 8px;
            padding: 10px;
            font-size: 0.8rem;
            color: #FAF8F2;
            line-height: 1.35;
            display: flex;
            gap: 8px;
            align-items: flex-start;
            flex: 1;
            overflow-y: auto;
            max-height: 110px;
        }
        .phone-prompt-box .speaker-icon { font-size: 1rem; }
        .phone-input-display {
            background: #0D0F0C;
            border-radius: 6px;
            padding: 6px 10px;
            margin-top: 8px;
            font-size: 1.1rem;
            font-family: monospace;
            color: #5C8A3A;
            text-align: right;
            min-height: 32px;
        }
        .blinking-cursor { animation: blink 1s infinite; color: #C97A2B; }
        @keyframes blink { 0%, 50% { opacity: 1; } 51%, 100% { opacity: 0; } }
        .phone-caller-input-wrap {
            margin-top: 8px;
            font-size: 0.75rem;
            color: #DCD9C6;
        }
        .phone-caller-input-wrap input {
            width: 100%;
            background: #111;
            border: 1px solid #444;
            color: #fff;
            padding: 6px 8px;
            border-radius: 4px;
            font-size: 0.85rem;
            margin-top: 3px;
        }
        .phone-keypad {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-bottom: 14px;
        }
        .key-row { display: flex; justify-content: space-between; gap: 8px; }
        .key-btn {
            flex: 1;
            height: 48px;
            background: #2D332B;
            border: none;
            border-radius: 24px;
            color: #fff;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            transition: background 0.15s, transform 0.1s;
        }
        .key-btn:active { background: #5C8A3A; transform: scale(0.95); }
        .key-btn .digit { font-size: 1.15rem; font-weight: 600; line-height: 1; }
        .key-btn .sub { font-size: 0.55rem; color: #8CAE5C; letter-spacing: 1px; }
        .phone-call-actions { display: flex; }
        .call-btn {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 24px;
            font-weight: 700;
            font-size: 0.95rem;
            cursor: pointer;
            transition: opacity 0.2s;
        }
        .call-btn.green { background: #4E7A38; color: #fff; }
        .call-btn.red { background: #A8442C; color: #fff; }
        .call-btn:hover { opacity: 0.9; }
    `;
    document.head.appendChild(style);
    document.body.appendChild(root);

    // State
    let ivrSessionId = null;
    let currentStep = 'IDLE'; // 'LANGUAGE', 'CROP', 'QUANTITY', 'CONFIRM', 'DONE'
    let enteredBuffer = '';

    const overlay = document.getElementById('ivrModalOverlay');
    const floatBtn = document.getElementById('ivrFloatBtn');
    const closeBtn = document.getElementById('ivrCloseBtn');
    const callBtn = document.getElementById('ivrCallBtn');
    const endBtn = document.getElementById('ivrEndBtn');
    const statusText = document.getElementById('ivrCallStatus');
    const promptText = document.getElementById('ivrPromptText');
    const displayEl = document.getElementById('ivrEnteredDigits');
    const callerInput = document.getElementById('ivrCallerMobile');
    const callerWrap = document.getElementById('ivrCallerWrap');

    floatBtn.addEventListener('click', () => { overlay.style.display = 'flex'; });
    closeBtn.addEventListener('click', () => { overlay.style.display = 'none'; resetCall(); });

    function resetCall() {
        ivrSessionId = null;
        currentStep = 'IDLE';
        enteredBuffer = '';
        displayEl.textContent = '';
        callerWrap.style.display = 'block';
        callBtn.style.display = 'block';
        endBtn.style.display = 'none';
        statusText.textContent = 'Ready to Call';
        promptText.innerHTML = 'Welcome to FASAL Toll-Free Farmer IVR Booking.<br>Click <strong>Call</strong> to dial from your registered mobile number.';
    }

    callBtn.addEventListener('click', async () => {
        const mobile = callerInput.value.trim();
        if (mobile.length !== 10) {
            alert('Please enter a 10-digit mobile number.');
            return;
        }

        callBtn.style.display = 'none';
        endBtn.style.display = 'block';
        callerWrap.style.display = 'none';
        statusText.textContent = 'Calling 1800-FASAL...';
        promptText.textContent = 'Connecting to FASAL IVR Interactive Exchange...';

        try {
            const res = await api.startIvrSession(mobile);
            ivrSessionId = res.data.session_id;
            statusText.textContent = 'Call Connected (00:01)';
            promptText.textContent = res.data.prompt;

            if (!res.data.is_registered) {
                currentStep = 'DONE';
            } else {
                currentStep = 'LANGUAGE';
            }
        } catch (err) {
            statusText.textContent = 'Call Failed';
            promptText.textContent = 'Unable to connect: ' + (err.message || 'Server error.');
            endBtn.style.display = 'none';
            callBtn.style.display = 'block';
        }
    });

    endBtn.addEventListener('click', () => {
        statusText.textContent = 'Call Ended';
        promptText.textContent = 'Thank you for calling FASAL IVR Service. Call disconnected.';
        setTimeout(resetCall, 2000);
    });

    // Handle Keypad Press
    document.querySelectorAll('.key-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const key = btn.dataset.key;
            if (currentStep === 'IDLE') return;

            enteredBuffer += key;
            displayEl.textContent = enteredBuffer;

            if (currentStep === 'LANGUAGE') {
                // 1 or 2
                const digit = key;
                enteredBuffer = '';
                displayEl.textContent = '';
                promptText.textContent = 'Processing language selection...';
                try {
                    const res = await api.selectIvrLanguage(ivrSessionId, digit);
                    promptText.innerHTML = res.data.prompt.replace(/\n/g, '<br>');
                    currentStep = 'CROP';
                } catch (e) {
                    promptText.textContent = e.message;
                }
            } else if (currentStep === 'CROP') {
                const digit = key;
                enteredBuffer = '';
                displayEl.textContent = '';
                promptText.textContent = 'Processing crop selection...';
                try {
                    const res = await api.selectIvrCrop(ivrSessionId, digit);
                    promptText.textContent = res.data.prompt;
                    currentStep = 'QUANTITY';
                } catch (e) {
                    promptText.textContent = e.message;
                }
            } else if (currentStep === 'QUANTITY') {
                // When # is pressed, submit entered quantity
                if (key === '#') {
                    const qtyStr = enteredBuffer.replace('#', '').trim();
                    enteredBuffer = '';
                    displayEl.textContent = '';
                    if (!qtyStr || isNaN(qtyStr)) {
                        promptText.textContent = 'Invalid quantity. Please enter digits and press #.';
                        return;
                    }
                    promptText.textContent = `You entered ${qtyStr} Quintals. Booking slot...`;
                    try {
                        const qtyRes = await api.enterIvrQuantity(ivrSessionId, qtyStr);
                        promptText.innerHTML = qtyRes.data.prompt + '<br><strong>Press 1 to Confirm Booking</strong>';
                        currentStep = 'CONFIRM';
                    } catch (e) {
                        promptText.textContent = e.message;
                    }
                }
            } else if (currentStep === 'CONFIRM') {
                if (key === '1') {
                    enteredBuffer = '';
                    displayEl.textContent = '';
                    promptText.textContent = 'Allocating slot and generating unique token...';
                    try {
                        const confirmRes = await api.confirmIvrBooking(ivrSessionId);
                        const b = confirmRes.data.booking;
                        promptText.innerHTML = `
                            🎉 <strong>Booking Confirmed!</strong><br>
                            Token: <span style="color:#E8B54D; font-weight:700;">${b.token_number}</span><br>
                            Date: ${b.assigned_date} (${b.shift})<br>
                            Center: ${b.center_name || b.center_id}<br>
                            A confirmation SMS has been printed to the terminal.
                        `;
                        currentStep = 'DONE';
                    } catch (e) {
                        promptText.textContent = 'Booking failed: ' + e.message;
                    }
                }
            }
        });
    });
})();
