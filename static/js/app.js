//
// Global state
let state = {
    sessionId: null,
    currentStep: 1,
    posts: [],
    selectedPost: null,
    iterationCount: 0
};

// DOM elements
const screens = {
    1: document.getElementById('screen-1'),
    2: document.getElementById('screen-2'),
    3: document.getElementById('screen-3')
};

const steps = {
    1: document.getElementById('step-1'),
    2: document.getElementById('step-2'),
    3: document.getElementById('step-3')
};

const inputText = document.getElementById('input-text');
const generateBtn = document.getElementById('generate-btn');
const loading = document.getElementById('loading');
const postsContainer = document.getElementById('posts-container');
const selectedPostDisplay = document.getElementById('selected-post-display');
const feedbackText = document.getElementById('feedback-text');
const regenerateBtn = document.getElementById('regenerate-btn');
const finishBtn = document.getElementById('finish-btn');
const resetBtn = document.getElementById('reset-btn');
const sessionIdDisplay = document.getElementById('session-id');
const iterationCountDisplay = document.getElementById('iteration-count');

// Helper functions
function showScreen(step) {
    Object.values(screens).forEach(screen => screen.classList.remove('active'));
    screens[step].classList.add('active');
    
    Object.values(steps).forEach(s => s.classList.remove('active'));
    for (let i = 1; i <= step; i++) {
        steps[i].classList.add('active');
    }
    
    state.currentStep = step;
}

function showLoading(show) {
    loading.style.display = show ? 'block' : 'none';
    generateBtn.disabled = show;
    regenerateBtn.disabled = show;
}

function showError(message) {
    alert('Error: ' + message);
}

// API calls
async function generatePosts() {
    const input = inputText.value.trim();
    
    if (!input) {
        showError('Please enter an idea or sample post');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Generation failed');
        }
        
        const data = await response.json();
        state.sessionId = data.session_id;
        state.posts = data.posts;
        state.iterationCount++;
        
        displayPosts(data.posts);
        updateSessionInfo();
        showScreen(2);
    } catch (error) {
        showError(error.message);
    } finally {
        showLoading(false);
    }
}

async function regeneratePosts() {
    const feedback = feedbackText.value.trim();
    
    if (!feedback) {
        showError('Please provide feedback for regeneration');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/regenerate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: state.sessionId,
                feedback: feedback,
                selected_post: state.selectedPost
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Regeneration failed');
        }
        
        const data = await response.json();
        state.posts = data.posts;
        state.iterationCount++;
        
        displayPosts(data.posts);
        updateSessionInfo();
        feedbackText.value = '';
        showScreen(2);
    } catch (error) {
        showError(error.message);
    } finally {
        showLoading(false);
    }
}

// Display functions
function displayPosts(posts) {
    postsContainer.innerHTML = '';
    
    posts.forEach((post, index) => {
        const card = document.createElement('div');
        card.className = 'post-card';
        card.innerHTML = `
            <span class="post-badge">#${index + 1}</span>
            <h3>${escapeHtml(post.title)}</h3>
            <p>${escapeHtml(post.content)}</p>
        `;
        card.addEventListener('click', () => selectPost(post));
        postsContainer.appendChild(card);
    });
}

function selectPost(post) {
    state.selectedPost = post;
    selectedPostDisplay.innerHTML = `
        <h3>${escapeHtml(post.title)}</h3>
        <p>${escapeHtml(post.content)}</p>
    `;
    showScreen(3);
}

function updateSessionInfo() {
    sessionIdDisplay.textContent = state.sessionId || '-';
    iterationCountDisplay.textContent = state.iterationCount;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function finishPost() {
    const finalText = `Title: ${state.selectedPost.title}\n\n${state.selectedPost.content}`;
    
    navigator.clipboard.writeText(finalText)
        .then(() => alert(' Post copied to clipboard!'))
        .catch(() => alert(' Post finalized! Please copy it manually.'));
}

function reset() {
    state = {
        sessionId: null,
        currentStep: 1,
        posts: [],
        selectedPost: null,
        iterationCount: 0
    };
    inputText.value = '';
    feedbackText.value = '';
    updateSessionInfo();
    showScreen(1);
}

// Event listeners
generateBtn.addEventListener('click', generatePosts);
regenerateBtn.addEventListener('click', regeneratePosts);
finishBtn.addEventListener('click', finishPost);
resetBtn.addEventListener('click', reset);

// Enter key support
inputText.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        generatePosts();
    }
});
