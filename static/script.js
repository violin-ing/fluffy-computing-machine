const ROWS = 6;
const COLS = 5;
let currentRowIndex = 0; 
let isGameOver = false; 
const STATE_CYCLE = ['absent', 'present', 'correct'];

const submitBtn = document.getElementById('submit-hints');
const restartBtn = document.getElementById('restart-btn');
const modal = document.getElementById('modal-overlay');
const modalTitle = document.getElementById('modal-title');
const modalMsg = document.getElementById('modal-msg');

function initBoard() {
    const board = document.getElementById('board-container');
    board.innerHTML = ''; 
    
    for (let r = 0; r < ROWS; r++) {
        const rowDiv = document.createElement('div');
        rowDiv.className = 'row';
        for (let c = 0; c < COLS; c++) {
            const tile = document.createElement('div');
            tile.className = 'tile';
            tile.id = `tile-${r}-${c}`;
            tile.setAttribute('data-state', 'empty');
            
            // Allow clicking only on active row
            tile.addEventListener('click', () => toggleTileState(tile, r));
            
            rowDiv.appendChild(tile);
        }
        board.appendChild(rowDiv);
    }
}

function toggleTileState(tile, rowIdx) {
    // If game over, lock everything
    if (isGameOver) return;

    // Prevent changing empty tiles
    if (tile.innerText === '') return;

    // Only allow clicking active row
    if (rowIdx !== currentRowIndex - 1) return;

    // Cycle colors: gray -> yellow -> green
    const currentState = tile.getAttribute('data-state');
    let nextState = 'absent';
    
    if (currentState !== 'empty') {
        const currentIndex = STATE_CYCLE.indexOf(currentState);
        const nextIndex = (currentIndex + 1) % STATE_CYCLE.length;
        nextState = STATE_CYCLE[nextIndex];
    }
    tile.setAttribute('data-state', nextState);
}

function generateHintString() {
    if (currentRowIndex === 0) return null;
    const activeRow = currentRowIndex - 1;
    let hintString = "";
    
    for (let i = 0; i < COLS; i++) {
        const tile = document.getElementById(`tile-${activeRow}-${i}`);
        const state = tile.getAttribute('data-state');
        
        if (state === 'correct') hintString += 'g';
        else if (state === 'present') hintString += 'y';
        else hintString += 'w'; 
    }
    return hintString;
}

function botGuess(word) {
    if (currentRowIndex >= ROWS) return;
    word = word.toUpperCase();
    
    // Lock the previous row visually
    if (currentRowIndex > 0) {
        const prevRow = currentRowIndex - 1;
        for(let i=0; i<COLS; i++) {
            document.getElementById(`tile-${prevRow}-${i}`).classList.add('locked');
        }
    }

    // Fill the new row
    for (let i = 0; i < COLS; i++) {
        const tile = document.getElementById(`tile-${currentRowIndex}-${i}`);
        tile.innerText = word[i];
        tile.setAttribute('data-state', 'absent'); 
        tile.classList.remove('locked');
    }
    currentRowIndex++;
}

// --- GAME STATE & MODALS ---

function handleGameOver() {
    isGameOver = true; 
    submitBtn.style.display = 'none'; 
    restartBtn.style.display = 'inline-block'; 
    
    // Visually lock the last row
    const lastRow = currentRowIndex - 1;
    for(let i=0; i<COLS; i++) {
        const tile = document.getElementById(`tile-${lastRow}-${i}`);
        if(tile) tile.classList.add('locked');
    }
}

function showModal(type, msg) {
    modalTitle.className = '';
    
    if (type === 'win') {
        modalTitle.innerText = "VICTORY!";
        modalTitle.classList.add('text-win');
        modalMsg.innerText = msg || "The bot found the word!";
    } else if (type === 'loss') {
        modalTitle.innerText = "SORRY";
        modalTitle.classList.add('text-loss');
        modalMsg.innerText = msg || "The bot ran out of guesses.";
    } else {
        modalTitle.innerText = "ERROR";
        modalTitle.classList.add('text-error');
        modalMsg.innerText = msg || "Something went wrong.";
    }

    modal.classList.remove('hidden');
}

function closeModal() {
    modal.classList.add('hidden');
}

// RESTART BUTTON EVENT
restartBtn.addEventListener('click', () => {
    currentRowIndex = 0;
    isGameOver = false;
    
    // Reset UI
    restartBtn.style.display = 'none';
    submitBtn.style.display = 'inline-block';
    submitBtn.disabled = false;
    submitBtn.innerText = "Send Hints";
    
    initBoard(); 
    startGame();
});

// SUBMIT BUTTON EVENT
submitBtn.addEventListener('click', () => {
    const resultString = generateHintString();
    if (!resultString) return;

    // Check for success
    if (resultString === 'ggggg') {
        showModal('win', "Bot found the word!");
        handleGameOver();
        return;
    }

    // 2. Check for failure
    if (currentRowIndex === ROWS) {
        showModal('loss', "Bot failed to solve it within 6 tries.");
        handleGameOver();
        return;
    }

    // Normal turn
    submitBtn.innerText = "Thinking...";
    submitBtn.disabled = true;

    fetch('/api/next-guess', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ hints: resultString })
    })
    .then(res => res.json())
    .then(data => {
        if(data.error) {
            showModal('error', data.error);
            handleGameOver();
        } else {
            botGuess(data.next_word);
        }
    })
    .catch(err => {
        showModal('error', "Could not connect to backend.");
    })
    .finally(() => {
        if (!isGameOver) {
            submitBtn.innerText = "Send Hints";
            submitBtn.disabled = false;
        }
    });
});

// --- INITIALIZATION ---

function startGame() {
    fetch('/api/start-game', { method: 'POST' })
    .then(res => res.json())
    .then(data => {
        botGuess(data.next_word);
    })
    .catch(err => {
        console.error(err);
        showModal('error', "Is the backend running?");
    });
}

const instructionModal = document.getElementById('instruction-modal');
const startBtn = document.getElementById('start-btn');

// When the user clicks "Got it", hide the instructions
startBtn.addEventListener('click', () => {
    instructionModal.classList.add('hidden');
});

const hasSeenInstructions = localStorage.getItem('seenInstructions');

if (hasSeenInstructions) {
    instructionModal.classList.add('hidden');
}

startBtn.addEventListener('click', () => {
    instructionModal.classList.add('hidden');
    localStorage.setItem('seenInstructions', 'true');
});

initBoard();
startGame();
