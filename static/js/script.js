/* ════════════════════════════════════════════════
   AURA-X — Main JavaScript
   Phase 1: Foundation + UI interactions
════════════════════════════════════════════════ */

/* ─────────────────────────────────────────────
   1. GLOBAL STATE
───────────────────────────────────────────── */
const AURA = {
    sessionId: null,
    currentDocId: null,
    isLoading: false,
    selectedImageFile: null,
    selectedResumeFile: null,
    selectedJDFile: null,
    jdMode: 'upload'  // 'upload' or 'paste'
};


/* ─────────────────────────────────────────────
   2. INITIALIZATION
───────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', function () {
    initializeApp();
});


function initializeApp() {
    // Generate or restore session ID
    AURA.sessionId = getSessionId();

    // Check server status
    checkServerStatus();

    // Set active nav link
    setActiveNavLink();

    // Initialize page-specific features
    const path = window.location.pathname;

    if (path === '/' || path === '/index') {
        initHomePage();
    } else if (path === '/document-chat') {
        initDocumentChatPage();
    } else if (path === '/resume-builder') {
        initResumePage();
    } else if (path === '/manage-people') {
        initManagePeoplePage();
    }

    console.log('✅ AURA-X initialized | Session:', AURA.sessionId);
}


/* ─────────────────────────────────────────────
   3. SESSION MANAGEMENT
───────────────────────────────────────────── */
function getSessionId() {
    let sessionId = localStorage.getItem('aura_session_id');
    if (!sessionId) {
        sessionId = 'session_' + Date.now() + '_' +
                    Math.random().toString(36).substr(2, 9);
        localStorage.setItem('aura_session_id', sessionId);
    }
    return sessionId;
}


/* ─────────────────────────────────────────────
   4. SERVER STATUS CHECK
───────────────────────────────────────────── */
async function checkServerStatus() {
    const dot = document.getElementById('statusDot');
    const text = document.getElementById('statusText');

    try {
        const response = await fetch('/api/health');
        const data = await response.json();

        if (data.status === 'healthy') {
            const lmRunning = data.lm_studio && data.lm_studio.running;

            if (lmRunning) {
                // Both Flask and LM Studio running
                if (dot) {
                    dot.classList.add('online');
                    dot.classList.remove('offline');
                }
                const modelName = data.lm_studio.model || 'Model loaded';
                if (text) text.textContent = 'AI Ready';
                if (text) text.title = modelName;
            } else {
                // Flask running but LM Studio offline
                if (dot) {
                    dot.style.background = 'var(--color-warning)';
                    dot.style.boxShadow = '0 0 8px var(--color-warning)';
                }
                if (text) text.textContent = 'LM Studio Offline';
                if (text) text.style.color = 'var(--color-warning)';

                // Show warning in chat
                showLMStudioWarning();
            }
        }
    } catch (error) {
        if (dot) {
            dot.classList.add('offline');
            dot.classList.remove('online');
        }
        if (text) text.textContent = 'Server Offline';
    }
}
/* ─────────────────────────────────────────────
   5. NAVIGATION
───────────────────────────────────────────── */
function setActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        link.classList.remove('active');
        const href = link.getAttribute('href');
        if (href === currentPath ||
            (currentPath === '/' && href === '/')) {
            link.classList.add('active');
        }
    });
}


function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}


/* ─────────────────────────────────────────────
   6. HOME PAGE INIT
───────────────────────────────────────────── */
function initHomePage() {
    setupChatInput();
    setupImageUpload();

    // Load previous chat history
    loadChatHistory();

    // Re-check status every 30 seconds
    setInterval(checkServerStatus, 30000);
}


/* ─────────────────────────────────────────────
   7. CHAT FUNCTIONALITY
───────────────────────────────────────────── */
function setupChatInput() {
    const input = document.getElementById('chatInput');
    if (input) {
        input.addEventListener('input', () => autoResizeTextarea(input));
    }
}


function handleChatKeydown(event) {
    // Send on Enter, new line on Shift+Enter
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

async function checkServerStatus() {
    const dot = document.getElementById('statusDot');
    const text = document.getElementById('statusText');

    try {
        const response = await fetch('/api/health');
        const data = await response.json();

        if (data.status === 'healthy') {
            const lmRunning = data.lm_studio && data.lm_studio.running;

            if (lmRunning) {
                // Both Flask and LM Studio running
                if (dot) {
                    dot.classList.add('online');
                    dot.classList.remove('offline');
                }
                const modelName = data.lm_studio.model || 'Model loaded';
                if (text) text.textContent = 'AI Ready';
                if (text) text.title = modelName;
            } else {
                // Flask running but LM Studio offline
                if (dot) {
                    dot.style.background = 'var(--color-warning)';
                    dot.style.boxShadow = '0 0 8px var(--color-warning)';
                }
                if (text) text.textContent = 'LM Studio Offline';
                if (text) text.style.color = 'var(--color-warning)';

                // Show warning in chat
                showLMStudioWarning();
            }
        }
    } catch (error) {
        if (dot) {
            dot.classList.add('offline');
            dot.classList.remove('online');
        }
        if (text) text.textContent = 'Server Offline';
    }
}


function showLMStudioWarning() {
    const chatWindow = document.getElementById('chatWindow');
    if (!chatWindow) return;

    // Check if warning already shown
    if (document.getElementById('lmWarning')) return;

    const warning = document.createElement('div');
    warning.id = 'lmWarning';
    warning.style.cssText = `
        background: rgba(255, 170, 0, 0.1);
        border: 1px solid rgba(255, 170, 0, 0.3);
        border-radius: 12px;
        padding: 16px;
        margin: 8px;
        font-size: 0.85rem;
        color: var(--color-warning);
        line-height: 1.6;
    `;
    warning.innerHTML = `
        ⚠️ <strong>LM Studio not detected</strong><br>
        Please open LM Studio, load a model, and start the server.<br>
        Then refresh this page.
        <br><br>
        <strong>Steps:</strong><br>
        1. Open LM Studio app<br>
        2. Download/select a model<br>
        3. Click "Start Server" (port 1234)<br>
        4. Refresh this page
    `;
    chatWindow.appendChild(warning);
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input ? input.value.trim() : '';

    if (!message || AURA.isLoading) return;

    // Clear input
    input.value = '';
    autoResizeTextarea(input);

    // Display user message
    displayMessage('user', message);

    // Show typing indicator
    showTyping('typingIndicator');

    // Disable send button
    setLoading(true, 'sendBtn');
    AURA.isLoading = true;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                session_id: AURA.sessionId
            })
        });

        const data = await response.json();

        hideTyping('typingIndicator');

        if (data.status === 'success') {
            displayMessage('aura', data.data.response);
        } else {
            displayMessage('aura',
                '⚠️ Sorry, I encountered an error. ' +
                'Please make sure LM Studio is running.');
        }

    } catch (error) {
        hideTyping('typingIndicator');
        displayMessage('aura',
            '⚠️ Cannot connect to server. ' +
            'Please check if Flask is running.');
        console.error('Chat error:', error);
    } finally {
        AURA.isLoading = false;
        setLoading(false, 'sendBtn');
    }
}


function displayMessage(role, content) {
    const chatWindow = document.getElementById('chatWindow');
    if (!chatWindow) return;

    const isUser = role === 'user';
    const time = new Date().toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
    });

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'aura-message'}`;

    // Format the message content
    const formattedContent = formatMessage(content);

    messageDiv.innerHTML = `
        <div class="message-avatar">${isUser ? 'U' : 'A'}</div>
        <div class="message-content">
            <div class="message-text">${formattedContent}</div>
            <div class="message-time">${time}</div>
        </div>
    `;

    chatWindow.appendChild(messageDiv);

    // Animate in
    messageDiv.style.opacity = '0';
    messageDiv.style.transform = 'translateY(10px)';
    setTimeout(() => {
        messageDiv.style.transition = 'all 0.3s ease';
        messageDiv.style.opacity = '1';
        messageDiv.style.transform = 'translateY(0)';
    }, 10);

    scrollChatToBottom('chatWindow');
}


function formatMessage(text) {
    if (!text) return '';

    // Escape HTML first
    let formatted = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    // Convert markdown to HTML
    formatted = formatted
        // Bold: **text**
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Italic: *text*
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        // Inline code: `code`
        .replace(/`([^`]+)`/g, '<code style="background:rgba(108,99,255,0.15);padding:2px 6px;border-radius:4px;font-size:0.85em;">$1</code>')
        // Headers: ### text
        .replace(/^### (.*?)$/gm, '<strong style="font-size:1.05em;color:var(--accent-cyan);">$1</strong>')
        .replace(/^## (.*?)$/gm, '<strong style="font-size:1.1em;color:var(--accent-purple);">$1</strong>')
        // Bullet points: - item
        .replace(/^[-•] (.*?)$/gm, '&nbsp;&nbsp;• $1')
        // Numbered list: 1. item
        .replace(/^\d+\. (.*?)$/gm, (match, p1, offset, str) => {
            const num = match.match(/^(\d+)/)[1];
            return `&nbsp;&nbsp;${num}. ${p1}`;
        })
        // Line breaks
        .replace(/\n/g, '<br>');

    return formatted;
}

function showTyping(indicatorId) {
    const indicator = document.getElementById(indicatorId);
    if (indicator) indicator.style.display = 'flex';
}


function hideTyping(indicatorId) {
    const indicator = document.getElementById(indicatorId);
    if (indicator) indicator.style.display = 'none';
}


async function clearChat() {
    try {
        await fetch('/api/chat/clear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: AURA.sessionId
            })
        });
    } catch (error) {
        console.error('Clear chat error:', error);
    }

    const chatWindow = document.getElementById('chatWindow');
    if (chatWindow) {
        chatWindow.innerHTML = `
            <div class="message aura-message">
                <div class="message-avatar">A</div>
                <div class="message-content">
                    <div class="message-text">
                        Chat cleared! I'm ready for a fresh conversation.
                        How can I help you? 😊
                    </div>
                    <div class="message-time">Just now</div>
                </div>
            </div>
        `;
    }

    showToast('Chat cleared successfully', 'success');
}

function askQuickQuestion(question) {
    const input = document.getElementById('chatInput');
    if (input) {
        input.value = question;
        input.focus();
        sendMessage();
    }
}

function scrollChatToBottom(windowId) {
    const chatWindow = document.getElementById(windowId);
    if (chatWindow) {
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
}
async function loadChatHistory() {
    if (!AURA.sessionId) return;

    try {
        const response = await fetch(
            `/api/chat/history/${AURA.sessionId}`
        );
        const data = await response.json();

        if (data.status === 'success') {
            const messages = data.data.messages || [];

            if (messages.length === 0) return;

            // Clear default welcome message
            const chatWindow = document.getElementById('chatWindow');
            if (chatWindow && messages.length > 0) {
                chatWindow.innerHTML = '';

                // Display each message from history
                messages.forEach(msg => {
                    displayMessage(
                        msg.role === 'user' ? 'user' : 'aura',
                        msg.content
                    );
                });

                scrollChatToBottom('chatWindow');
            }
        }
    } catch (error) {
        console.error('Load history error:', error);
    }
}

/* ─────────────────────────────────────────────
   8. IMAGE UPLOAD & ANALYSIS
───────────────────────────────────────────── */
function setupImageUpload() {
    const uploadArea = document.getElementById('imageUploadArea');
    if (!uploadArea) return;

    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleImageDrop);
}


function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('drag-over');
}


function handleDragLeave(event) {
    event.currentTarget.classList.remove('drag-over');
}


function handleImageDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');

    const files = event.dataTransfer.files;
    if (files.length > 0) {
        processImageFile(files[0]);
    }
}


function handleImageSelect(event) {
    const file = event.target.files[0];
    if (file) processImageFile(file);
}


function processImageFile(file) {
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
    if (!allowedTypes.includes(file.type)) {
        showToast('Please upload a valid image (JPG, PNG, WEBP)', 'error');
        return;
    }

    // Validate file size (max 16MB)
    if (file.size > 16 * 1024 * 1024) {
        showToast('Image too large. Maximum size is 16MB', 'error');
        return;
    }

    AURA.selectedImageFile = file;

    // Show preview
    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = document.getElementById('imagePreview');
        const previewArea = document.getElementById('imagePreviewArea');
        const uploadArea = document.getElementById('imageUploadArea');

        if (preview) preview.src = e.target.result;
        if (previewArea) previewArea.style.display = 'block';
        if (uploadArea) uploadArea.style.display = 'none';
    };
    reader.readAsDataURL(file);

    // Clear previous results
    clearImageResults();
}
/* ════════════════════════════════════════════════
   PHASE 3 ADDITIONS — Image Analysis JS
════════════════════════════════════════════════ */


/* ─────────────────────────────────────────────
   REPLACE analyzeImage function
───────────────────────────────────────────── */
async function analyzeImage() {
    if (!AURA.selectedImageFile) {
        showToast('Please select an image first', 'warning');
        return;
    }

    // Show loading state
    const loadingEl = document.getElementById('analysisLoading');
    const resultsEl = document.getElementById('analysisResults');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const previewArea = document.getElementById('imagePreviewArea');

    if (loadingEl) loadingEl.style.display = 'flex';
    if (resultsEl) {
        resultsEl.style.display = 'none';
        resultsEl.innerHTML = '';
    }
    if (analyzeBtn) {
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<span class="loading-spinner small"></span> Analyzing...';
    }

    try {
        // Create FormData with image
        const formData = new FormData();
        formData.append('image', AURA.selectedImageFile);

        // Send to backend
        const response = await fetch('/api/analyze-image', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        // Hide loading
        if (loadingEl) loadingEl.style.display = 'none';
        if (analyzeBtn) {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '◈ Analyze Face';
        }

        if (data.status === 'success') {
            displayImageResults(data.data);
            showToast(
                data.data.summary || 'Analysis complete!',
                'success'
            );
        } else {
            showToast(
                data.message || 'Analysis failed',
                'error'
            );
        }

    } catch (error) {
        if (loadingEl) loadingEl.style.display = 'none';
        if (analyzeBtn) {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '◈ Analyze Face';
        }
        showToast('Failed to connect to server', 'error');
        console.error('❌ Image analysis error:', error);
    }
}


/* ─────────────────────────────────────────────
   REPLACE displayImageResults function
───────────────────────────────────────────── */
function displayImageResults(data) {
    const resultsEl = document.getElementById('analysisResults');
    if (!resultsEl) return;

    const faceCount = data.faces_detected || 0;
    const faces = data.faces || [];
    const summary = data.summary || '';
    const annotatedUrl = data.annotated_image_url;

    let html = '';

    // ─── Summary Header ───
    html += `
        <div style="
            background: rgba(108,99,255,0.08);
            border: 1px solid rgba(108,99,255,0.2);
            border-radius: 12px;
            padding: 12px 16px;
            margin-bottom: 12px;
            font-size: 0.88rem;
            color: var(--text-secondary);
        ">
            📊 ${summary}
        </div>
    `;

    // ─── No Faces ───
    if (faceCount === 0) {
        html += `
            <div style="
                text-align: center;
                padding: 24px;
                color: var(--text-muted);
                font-size: 0.9rem;
            ">
                <div style="font-size: 3rem; margin-bottom: 12px;">🔍</div>
                <strong>No faces detected</strong><br>
                <span style="font-size: 0.8rem;">
                    Try uploading a clearer photo with 
                    visible faces and good lighting.
                </span>
            </div>
        `;
    } else {
        // ─── Each Face Card ───
        faces.forEach((face, idx) => {
            const emotion = face.emotion_display || 'Unknown';
            const emoji = face.emotion_emoji || '😐';
            const confidence = face.emotion_confidence || 0;
            const age = face.age_range || 'Unknown';
            const gender = face.gender || 'Unknown';
            const genderConf = face.gender_confidence || 0;
            const identity = face.identity || 'Unknown';
            const scores = face.emotion_scores || {};

            html += `
                <div class="face-result-card" style="
                    background: var(--bg-input);
                    border: 1px solid var(--border-color);
                    border-radius: 12px;
                    padding: 16px;
                    margin-bottom: 12px;
                ">
                    <!-- Face Header -->
                    <div style="
                        display: flex;
                        align-items: center;
                        gap: 10px;
                        margin-bottom: 14px;
                        padding-bottom: 10px;
                        border-bottom: 1px solid var(--border-color);
                    ">
                        <span style="
                            background: linear-gradient(135deg, #6c63ff, #00d4ff);
                            color: white;
                            padding: 2px 10px;
                            border-radius: 20px;
                            font-size: 0.75rem;
                            font-weight: 600;
                        ">Face ${idx + 1}</span>
                        <span style="font-size: 1.5rem;">${emoji}</span>
                        <span style="
                            font-weight: 600;
                            color: var(--accent-cyan);
                        ">${emotion}</span>
                    </div>

                    <!-- Analysis Rows -->
                    <div style="
                        display: flex;
                        flex-direction: column;
                        gap: 10px;
                    ">
                        <!-- Emotion Row with Bar -->
                        <div>
                            <div style="
                                display: flex;
                                justify-content: space-between;
                                margin-bottom: 4px;
                                font-size: 0.85rem;
                            ">
                                <span style="color: var(--text-secondary);">
                                    ${emoji} Emotion
                                </span>
                                <span style="
                                    font-weight: 600;
                                    color: var(--accent-cyan);
                                ">
                                    ${emotion} ${confidence}%
                                </span>
                            </div>
                            <div style="
                                height: 5px;
                                background: var(--bg-card);
                                border-radius: 10px;
                                overflow: hidden;
                            ">
                                <div style="
                                    height: 100%;
                                    width: ${confidence}%;
                                    background: linear-gradient(90deg, #6c63ff, #00d4ff);
                                    border-radius: 10px;
                                    transition: width 1s ease;
                                "></div>
                            </div>
                        </div>

                        <!-- Age Row -->
                        <div style="
                            display: flex;
                            justify-content: space-between;
                            font-size: 0.88rem;
                        ">
                            <span style="color: var(--text-secondary);">
                                🎂 Age Range
                            </span>
                            <span style="font-weight: 600;">
                                ~${age} years
                            </span>
                        </div>

                        <!-- Gender Row -->
                        <div style="
                            display: flex;
                            justify-content: space-between;
                            font-size: 0.88rem;
                        ">
                            <span style="color: var(--text-secondary);">
                                👤 Gender
                            </span>
                            <span style="font-weight: 600;">
                                ${gender}
                                ${genderConf > 0 ? 
                                    `<span style="color:var(--text-muted);
                                                  font-size:0.8rem;">
                                        (${genderConf}%)
                                    </span>` : ''}
                            </span>
                        </div>

                        <!-- Identity Row -->
                        <div style="
                            display: flex;
                            justify-content: space-between;
                            font-size: 0.88rem;
                        ">
                            <span style="color: var(--text-secondary);">
                                🔍 Identity
                            </span>
                            <span style="
                                font-weight: 600;
                                color: ${identity !== 'Unknown' ? 
                                    'var(--color-success)' : 
                                    'var(--text-muted)'};
                            ">
                                ${identity}
                            </span>
                        </div>

                        <!-- All Emotion Scores -->
                        ${Object.keys(scores).length > 0 ? 
                            buildEmotionScores(scores) : ''}
                    </div>
                </div>
            `;
        });
    }

    // ─── Annotated Image ───
    if (annotatedUrl) {
        html += `
            <div style="margin-top: 12px;">
                <div style="
                    font-size: 0.8rem;
                    color: var(--text-muted);
                    margin-bottom: 6px;
                ">Annotated Result:</div>
                <img 
                    src="${annotatedUrl}" 
                    alt="Annotated"
                    style="
                        width: 100%;
                        border-radius: 10px;
                        border: 1px solid var(--border-color);
                        max-height: 200px;
                        object-fit: cover;
                    "
                    onerror="this.style.display='none'"
                >
            </div>
        `;
    }

    resultsEl.innerHTML = html;
    resultsEl.style.display = 'block';
}


/* ─────────────────────────────────────────────
   BUILD EMOTION SCORES BAR CHART
───────────────────────────────────────────── */
function buildEmotionScores(scores) {
    const emotionEmojis = {
        happy: '😊', sad: '😢', angry: '😠',
        surprise: '😲', fear: '😨',
        disgust: '🤢', neutral: '😐'
    };

    // Sort by score descending
    const sorted = Object.entries(scores)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5); // Show top 5

    let html = `
        <div style="
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid var(--border-color);
        ">
            <div style="
                font-size: 0.75rem;
                color: var(--text-muted);
                margin-bottom: 8px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            ">All Emotions</div>
    `;

    sorted.forEach(([emotion, score]) => {
        const emoji = emotionEmojis[emotion] || '😐';
        const roundedScore = Math.round(score);
        html += `
            <div style="
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 5px;
                font-size: 0.8rem;
            ">
                <span style="width: 20px;">${emoji}</span>
                <span style="
                    width: 65px;
                    color: var(--text-secondary);
                    text-transform: capitalize;
                ">${emotion}</span>
                <div style="
                    flex: 1;
                    height: 4px;
                    background: var(--bg-card);
                    border-radius: 10px;
                    overflow: hidden;
                ">
                    <div style="
                        height: 100%;
                        width: ${roundedScore}%;
                        background: linear-gradient(
                            90deg, #6c63ff, #00d4ff
                        );
                        border-radius: 10px;
                    "></div>
                </div>
                <span style="
                    width: 35px;
                    text-align: right;
                    color: var(--text-muted);
                ">${roundedScore}%</span>
            </div>
        `;
    });

    html += `</div>`;
    return html;
}


/* ─────────────────────────────────────────────
   REPLACE processImageFile function
───────────────────────────────────────────── */
function processImageFile(file) {
    // Validate file type
    const allowedTypes = [
        'image/jpeg',
        'image/png',
        'image/webp',
        'image/gif',
        'image/bmp'
    ];

    if (!allowedTypes.includes(file.type)) {
        showToast(
            'Please upload a valid image (JPG, PNG, WEBP)',
            'error'
        );
        return;
    }

    // Validate file size (max 16MB)
    if (file.size > 16 * 1024 * 1024) {
        showToast('Image too large. Maximum size is 16MB', 'error');
        return;
    }

    AURA.selectedImageFile = file;

    // Show file info
    const sizeText = formatBytes(file.size);
    showToast(`Image selected: ${file.name} (${sizeText})`, 'info');

    // Show preview
    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = document.getElementById('imagePreview');
        const previewArea = document.getElementById('imagePreviewArea');
        const uploadArea = document.getElementById('imageUploadArea');

        if (preview) preview.src = e.target.result;
        if (previewArea) previewArea.style.display = 'block';
        if (uploadArea) uploadArea.style.display = 'none';
    };
    reader.readAsDataURL(file);

    // Clear previous results
    clearImageResults();
}

async function analyzeImage() {
    if (!AURA.selectedImageFile) {
        showToast('Please select an image first', 'warning');
        return;
    }

    // Show loading
    const loadingEl = document.getElementById('analysisLoading');
    const resultsEl = document.getElementById('analysisResults');
    const analyzeBtn = document.getElementById('analyzeBtn');

    if (loadingEl) loadingEl.style.display = 'flex';
    if (resultsEl) resultsEl.style.display = 'none';
    if (analyzeBtn) analyzeBtn.disabled = true;

    try {
        const formData = new FormData();
        formData.append('image', AURA.selectedImageFile);

        const response = await fetch('/api/analyze-image', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (loadingEl) loadingEl.style.display = 'none';
        if (analyzeBtn) analyzeBtn.disabled = false;

        if (data.status === 'success') {
            displayImageResults(data.data);
        } else {
            showToast(data.message || 'Analysis failed', 'error');
        }

    } catch (error) {
        if (loadingEl) loadingEl.style.display = 'none';
        if (analyzeBtn) analyzeBtn.disabled = false;
        showToast('Failed to analyze image', 'error');
        console.error('Image analysis error:', error);
    }
}


function displayImageResults(data) {
    const resultsEl = document.getElementById('analysisResults');
    if (!resultsEl) return;

    const faces = data.faces || [];
    const faceCount = data.faces_detected || 0;

    let html = `
        <div class="face-result-card">
            <div class="face-result-header">
                <span class="face-badge">${faceCount} Face${faceCount !== 1 ? 's' : ''} Detected</span>
            </div>
    `;

    if (faceCount === 0) {
        html += `
            <div style="text-align:center; padding: 20px; color: var(--text-muted);">
                No faces detected in this image.
                Try a clearer photo with visible faces.
            </div>
        `;
    } else {
        faces.forEach((face, index) => {
            html += `
                <div style="margin-bottom: 16px;">
                    <div style="font-size: 0.8rem; color: var(--text-muted);
                                margin-bottom: 8px;">
                        Face ${index + 1}
                    </div>
                    <div class="result-rows">
                        <div class="result-row">
                            <span class="result-label">😊 Emotion</span>
                            <span class="result-value highlight">
                                ${face.emotion || 'N/A'}
                                ${face.emotion_confidence ?
                                    `(${face.emotion_confidence}%)` : ''}
                            </span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">🎂 Age Range</span>
                            <span class="result-value">${face.age_range || 'N/A'}</span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">👤 Gender</span>
                            <span class="result-value">${face.gender || 'N/A'}</span>
                        </div>
                        <div class="result-row">
                            <span class="result-label">🔍 Identity</span>
                            <span class="result-value ${face.identity !== 'Unknown' ? 'success' : ''}">
                                ${face.identity || 'Unknown'}
                            </span>
                        </div>
                    </div>
                </div>
            `;
        });
    }

    html += `</div>`;

    resultsEl.innerHTML = html;
    resultsEl.style.display = 'block';
}


function clearImageAnalysis() {
    AURA.selectedImageFile = null;

    const uploadArea = document.getElementById('imageUploadArea');
    const previewArea = document.getElementById('imagePreviewArea');
    const imageInput = document.getElementById('imageInput');

    if (uploadArea) uploadArea.style.display = 'flex';
    if (previewArea) previewArea.style.display = 'none';
    if (imageInput) imageInput.value = '';

    clearImageResults();
}


function clearImageResults() {
    const resultsEl = document.getElementById('analysisResults');
    const loadingEl = document.getElementById('analysisLoading');

    if (resultsEl) {
        resultsEl.innerHTML = '';
        resultsEl.style.display = 'none';
    }
    if (loadingEl) loadingEl.style.display = 'none';
}


/* ─────────────────────────────────────────────
   9. DOCUMENT CHAT PAGE
───────────────────────────────────────────── */
function initDocumentChatPage() {
    setupDocUpload();
}


function setupDocUpload() {
    const uploadArea = document.getElementById('docUploadArea');
    if (!uploadArea) return;
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDocDrop);
}


function handleDocDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');
    const files = event.dataTransfer.files;
    if (files.length > 0) processDocFile(files[0]);
}


function handleDocSelect(event) {
    const file = event.target.files[0];
    if (file) processDocFile(file);
}


function processDocFile(file) {
    const allowedTypes = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword',
        'text/plain'
    ];

    if (!allowedTypes.includes(file.type)) {
        showToast('Please upload PDF, DOCX, or TXT file', 'error');
        return;
    }

    // Show doc info
    const docInfoCard = document.getElementById('docInfoCard');
    const docName = document.getElementById('docName');
    const docMeta = document.getElementById('docMeta');

    if (docName) docName.textContent = file.name;
    if (docMeta) {
        const ext = file.name.split('.').pop().toUpperCase();
        const size = formatBytes(file.size);
        docMeta.textContent = `${ext} · ${size}`;
    }
    if (docInfoCard) docInfoCard.style.display = 'flex';

    // Upload document
    uploadDocument(file);
}


async function uploadDocument(file) {
    const docStatus = document.getElementById('docStatus');

    try {
        const formData = new FormData();
        formData.append('document', file);

        const response = await fetch('/api/upload-document', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.status === 'success') {
            AURA.currentDocId = data.data.doc_id;

            if (docStatus) {
                docStatus.innerHTML = '✅ Ready';
                docStatus.style.color = 'var(--color-success)';
            }

            // Enable chat
            const docInput = document.getElementById('docChatInput');
            if (docInput) {
                docInput.disabled = false;
                docInput.placeholder = 'Ask anything about your document...';
            }

            showToast('Document uploaded successfully!', 'success');

            // Auto message
            addDocChatMessage('aura',
                `Document "${file.name}" uploaded! I've processed it and I'm ready to answer your questions. What would you like to know?`);
        } else {
            if (docStatus) {
                docStatus.innerHTML = '❌ Failed';
                docStatus.style.color = 'var(--color-error)';
            }
            showToast(data.message || 'Upload failed', 'error');
        }

    } catch (error) {
        if (docStatus) {
            docStatus.innerHTML = '❌ Error';
        }
        showToast('Failed to upload document', 'error');
        console.error('Upload error:', error);
    }
}


function handleDocChatKeydown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendDocMessage();
    }
}


async function sendDocMessage() {
    if (!AURA.currentDocId) {
        showToast('Please upload a document first', 'warning');
        return;
    }

    const input = document.getElementById('docChatInput');
    const message = input ? input.value.trim() : '';

    if (!message) return;

    input.value = '';
    addDocChatMessage('user', message);
    showTyping('docTypingIndicator');
    setLoading(true, 'docSendBtn');

    try {
        const response = await fetch('/api/document-chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: message,
                doc_id: AURA.currentDocId,
                session_id: AURA.sessionId
            })
        });

        const data = await response.json();
        hideTyping('docTypingIndicator');

        if (data.status === 'success') {
            addDocChatMessage('aura', data.data.answer);
        } else {
            addDocChatMessage('aura',
                '⚠️ Could not answer from document. Please try again.');
        }

    } catch (error) {
        hideTyping('docTypingIndicator');
        addDocChatMessage('aura', '⚠️ Connection error. Please check server.');
        console.error('Doc chat error:', error);
    } finally {
        setLoading(false, 'docSendBtn');
    }
}


function addDocChatMessage(role, content) {
    const chatWindow = document.getElementById('docChatWindow');
    if (!chatWindow) return;

    const isUser = role === 'user';
    const time = new Date().toLocaleTimeString([], {
        hour: '2-digit', minute: '2-digit'
    });

    const div = document.createElement('div');
    div.className = `message ${isUser ? 'user-message' : 'aura-message'}`;
    div.innerHTML = `
        <div class="message-avatar">${isUser ? 'U' : 'A'}</div>
        <div class="message-content">
            <div class="message-text">${formatMessage(content)}</div>
            <div class="message-time">${time}</div>
        </div>
    `;

    chatWindow.appendChild(div);
    scrollChatToBottom('docChatWindow');
}


function setDocQuestion(question) {
    const input = document.getElementById('docChatInput');
    if (input) {
        input.value = question;
        input.focus();
    }
}


function clearDocChat() {
    const chatWindow = document.getElementById('docChatWindow');
    if (chatWindow) {
        chatWindow.innerHTML = `
            <div class="message aura-message">
                <div class="message-avatar">A</div>
                <div class="message-content">
                    <div class="message-text">
                        Chat cleared! Upload a document to continue.
                    </div>
                    <div class="message-time">Now</div>
                </div>
            </div>
        `;
    }
}


/* ─────────────────────────────────────────────
   10. RESUME BUILDER PAGE
───────────────────────────────────────────── */
function initResumePage() {
    // Page is ready for uploads
}


function switchJDTab(tab) {
    AURA.jdMode = tab;

    const tabs = document.querySelectorAll('.jd-tab');
    tabs.forEach(t => t.classList.remove('active'));

    const uploadTab = document.getElementById('jdUploadTab');
    const pasteTab = document.getElementById('jdPasteTab');

    if (tab === 'upload') {
        if (uploadTab) uploadTab.style.display = 'block';
        if (pasteTab) pasteTab.style.display = 'none';
        tabs[0].classList.add('active');
    } else {
        if (uploadTab) uploadTab.style.display = 'none';
        if (pasteTab) pasteTab.style.display = 'block';
        tabs[1].classList.add('active');
    }
}


function handleResumeSelect(event) {
    const file = event.target.files[0];
    if (file) processResumeFile(file);
}


function handleResumeDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');
    const files = event.dataTransfer.files;
    if (files.length > 0) processResumeFile(files[0]);
}


function processResumeFile(file) {
    AURA.selectedResumeFile = file;

    const fileInfo = document.getElementById('resumeFileInfo');
    const fileName = document.getElementById('resumeFileName');

    if (fileName) fileName.textContent = file.name;
    if (fileInfo) fileInfo.style.display = 'flex';

    showToast('Resume selected!', 'success');
}


function clearResumeFile() {
    AURA.selectedResumeFile = null;
    const fileInfo = document.getElementById('resumeFileInfo');
    const resumeInput = document.getElementById('resumeInput');
    if (fileInfo) fileInfo.style.display = 'none';
    if (resumeInput) resumeInput.value = '';
}


function handleJDSelect(event) {
    const file = event.target.files[0];
    if (file) processJDFile(file);
}


function handleJDDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');
    const files = event.dataTransfer.files;
    if (files.length > 0) processJDFile(files[0]);
}


function processJDFile(file) {
    AURA.selectedJDFile = file;

    const fileInfo = document.getElementById('jdFileInfo');
    const fileName = document.getElementById('jdFileName');

    if (fileName) fileName.textContent = file.name;
    if (fileInfo) fileInfo.style.display = 'flex';

    showToast('Job description selected!', 'success');
}


function clearJDFile() {
    AURA.selectedJDFile = null;
    const fileInfo = document.getElementById('jdFileInfo');
    const jdInput = document.getElementById('jdInput');
    if (fileInfo) fileInfo.style.display = 'none';
    if (jdInput) jdInput.value = '';
}


async function analyzeResume() {
    // Validate inputs
    if (!AURA.selectedResumeFile) {
        showToast('Please upload your resume first', 'warning');
        return;
    }

    const jdText = document.getElementById('jdTextarea') ?
                   document.getElementById('jdTextarea').value.trim() : '';

    if (AURA.jdMode === 'paste' && !jdText) {
        showToast('Please paste the job description', 'warning');
        return;
    }

    if (AURA.jdMode === 'upload' && !AURA.selectedJDFile) {
        showToast('Please upload the job description', 'warning');
        return;
    }

    // Show loading
    const loadingEl = document.getElementById('resumeLoading');
    const resultsEl = document.getElementById('resumeResults');
    const analyzeBtn = document.getElementById('analyzeResumeBtn');

    if (loadingEl) loadingEl.style.display = 'flex';
    if (resultsEl) resultsEl.style.display = 'none';
    if (analyzeBtn) analyzeBtn.disabled = true;

    try {
        const formData = new FormData();
        formData.append('resume', AURA.selectedResumeFile);

        if (AURA.jdMode === 'upload' && AURA.selectedJDFile) {
            formData.append('jd_file', AURA.selectedJDFile);
        } else {
            formData.append('jd_text', jdText);
        }

        const response = await fetch('/api/analyze-resume', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (loadingEl) loadingEl.style.display = 'none';
        if (analyzeBtn) analyzeBtn.disabled = false;

        if (data.status === 'success') {
            displayResumeResults(data.data);
        } else {
            showToast(data.message || 'Analysis failed', 'error');
        }

    } catch (error) {
        if (loadingEl) loadingEl.style.display = 'none';
        if (analyzeBtn) analyzeBtn.disabled = false;
        showToast('Failed to analyze resume', 'error');
        console.error('Resume analysis error:', error);
    }
}


function displayResumeResults(data) {
    const resultsEl = document.getElementById('resumeResults');
    if (!resultsEl) return;

    // Match score
    const score = data.match_score || 0;
    const scoreNumber = document.getElementById('scoreNumber');
    const scoreFill = document.getElementById('scoreFill');

    if (scoreNumber) scoreNumber.textContent = `${score}%`;
    if (scoreFill) {
        setTimeout(() => { scoreFill.style.width = `${score}%`; }, 100);
    }

    // Color score circle based on score
    const scoreCircle = document.getElementById('scoreCircle');
    if (scoreCircle) {
        if (score >= 70) {
            scoreCircle.style.background =
                'linear-gradient(135deg, #00ff88, #00d4ff)';
        } else if (score >= 40) {
            scoreCircle.style.background =
                'linear-gradient(135deg, #ffaa00, #ff6b9d)';
        } else {
            scoreCircle.style.background =
                'linear-gradient(135deg, #ff4444, #ff9f43)';
        }
    }

    // Missing keywords
    const missingEl = document.getElementById('missingKeywords');
    if (missingEl) {
        const missing = data.missing_keywords || [];
        missingEl.innerHTML = missing.length > 0
            ? missing.map(k => `
                <span class="keyword-tag missing">${k}</span>
              `).join('')
            : '<span style="color: var(--color-success)">No major gaps found!</span>';
    }

    // Matched keywords
    const matchedEl = document.getElementById('matchedKeywords');
    if (matchedEl) {
        const matched = data.matched_keywords || [];
        matchedEl.innerHTML = matched.length > 0
            ? matched.map(k => `
                <span class="keyword-tag matched">${k}</span>
              `).join('')
            : '<span style="color: var(--text-muted)">No matches found</span>';
    }

    // Suggestions
    const suggestionsEl = document.getElementById('suggestionsContent');
    if (suggestionsEl) {
        suggestionsEl.textContent = data.suggestions ||
            'No suggestions available.';
    }

    resultsEl.style.display = 'block';
    resultsEl.scrollIntoView({ behavior: 'smooth' });
}


function downloadReport() {
    showToast('Report download coming in Phase 5!', 'info');
}


/* ─────────────────────────────────────────────
   11. MANAGE PEOPLE PAGE
───────────────────────────────────────────── */
function initManagePeoplePage() {
    loadPeople();
}


function previewPersonPhoto(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = document.getElementById('personPhotoPreview');
        const placeholder = document.getElementById('photoPreviewArea');

        if (preview) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        }
        if (placeholder) placeholder.style.display = 'none';
    };
    reader.readAsDataURL(file);
}


async function addPerson(event) {
    event.preventDefault();

    const name = document.getElementById('personName').value.trim();
    const role = document.getElementById('personRole').value.trim();
    const skills = document.getElementById('personSkills').value.trim();
    const notes = document.getElementById('personNotes').value.trim();
    const photoInput = document.getElementById('personPhotoInput');

    if (!name) {
        showToast('Name is required', 'warning');
        return;
    }

    setLoading(true, 'addPersonBtn');

    try {
        const formData = new FormData();
        formData.append('name', name);
        formData.append('role', role);
        formData.append('skills', skills);
        formData.append('notes', notes);

        if (photoInput && photoInput.files[0]) {
            formData.append('photo', photoInput.files[0]);
        }

        const response = await fetch('/api/people/add', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.status === 'success') {
            showToast(`${name} added successfully!`, 'success');
            resetAddPersonForm();
            loadPeople();
        } else {
            showToast(data.message || 'Failed to add person', 'error');
        }

    } catch (error) {
        showToast('Error adding person', 'error');
        console.error('Add person error:', error);
    } finally {
        setLoading(false, 'addPersonBtn');
    }
}


async function loadPeople() {
    const loadingEl = document.getElementById('peopleLoading');
    const emptyEl = document.getElementById('emptyState');
    const gridEl = document.getElementById('peopleGrid');
    const countEl = document.getElementById('peopleCount');

    if (loadingEl) loadingEl.style.display = 'flex';
    if (emptyEl) emptyEl.style.display = 'none';
    if (gridEl) gridEl.innerHTML = '';

    try {
        const response = await fetch('/api/people/list');
        const data = await response.json();

        if (loadingEl) loadingEl.style.display = 'none';

        if (data.status === 'success') {
            const people = data.data.people || [];

            if (countEl) {
                countEl.textContent =
                    `${people.length} ${people.length === 1 ? 'person' : 'people'}`;
            }

            if (people.length === 0) {
                if (emptyEl) emptyEl.style.display = 'block';
            } else {
                people.forEach(person => {
                    if (gridEl) gridEl.appendChild(createPersonCard(person));
                });
            }
        }

    } catch (error) {
        if (loadingEl) loadingEl.style.display = 'none';
        showToast('Failed to load people', 'error');
        console.error('Load people error:', error);
    }
}


function createPersonCard(person) {
    const card = document.createElement('div');
    card.className = 'person-card';
    card.setAttribute('data-id', person.person_id);

    const photoHtml = person.photo_path
        ? `<img src="/${person.photo_path}" alt="${person.name}">`
        : `<span>${person.name.charAt(0).toUpperCase()}</span>`;

    card.innerHTML = `
        <div class="person-card-photo">${photoHtml}</div>
        <div class="person-card-name">${person.name}</div>
        <div class="person-card-role">${person.role || 'No role specified'}</div>
        <div class="person-card-skills">${person.skills || ''}</div>
        <button class="person-card-delete"
                onclick="deletePerson('${person.person_id}', '${person.name}')">
            🗑 Remove
        </button>
    `;

    return card;
}


async function deletePerson(personId, name) {
    if (!confirm(`Remove ${name} from known people?`)) return;

    try {
        const response = await fetch(`/api/people/delete/${personId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.status === 'success') {
            showToast(`${name} removed`, 'success');
            loadPeople();
        } else {
            showToast(data.message || 'Failed to remove', 'error');
        }

    } catch (error) {
        showToast('Error removing person', 'error');
        console.error('Delete person error:', error);
    }
}


function resetAddPersonForm() {
    document.getElementById('personName').value = '';
    document.getElementById('personRole').value = '';
    document.getElementById('personSkills').value = '';
    document.getElementById('personNotes').value = '';

    const preview = document.getElementById('personPhotoPreview');
    const placeholder = document.getElementById('photoPreviewArea');
    const photoInput = document.getElementById('personPhotoInput');

    if (preview) { preview.src = ''; preview.style.display = 'none'; }
    if (placeholder) placeholder.style.display = 'flex';
    if (photoInput) photoInput.value = '';
}


/* ─────────────────────────────────────────────
   12. UTILITY FUNCTIONS
───────────────────────────────────────────── */

// Auto resize textarea as user types
function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}


// Show/hide loading state on button
function setLoading(isLoading, buttonId) {
    const btn = document.getElementById(buttonId);
    if (!btn) return;

    if (isLoading) {
        btn.disabled = true;
        btn.dataset.originalText = btn.innerHTML;
        btn.innerHTML = '<span class="loading-spinner small"></span>';
    } else {
        btn.disabled = false;
        if (btn.dataset.originalText) {
            btn.innerHTML = btn.dataset.originalText;
        }
    }
}


// Format bytes to readable size
function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}


// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    if (!toast) return;

    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.className = 'toast';
    }, 3500);
}


// API helper function
async function apiCall(url, method = 'GET', body = null) {
    const options = {
        method,
        headers: {}
    };

    if (body && !(body instanceof FormData)) {
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(body);
    } else if (body) {
        options.body = body;
    }

    const response = await fetch(url, options);
    return response.json();
}