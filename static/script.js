const ROWS = 6;
const COLS = 5;
let currentRowIndex = 0; 
let isGameOver = false; 
const STATE_CYCLE = ['absent', 'present', 'correct'];

const submitBtn = document.getElementById('submit-hints');
const restartBtn = document.getElementById('restart-btn');

// Error/Game Over modals
const modal = document.getElementById('modal-overlay');
const modalTitle = document.getElementById('modal-title');
const modalMsg = document.getElementById('modal-msg');

// Instruction modal 
const instructionModal = document.getElementById('instruction-modal');
const startBtn = document.getElementById('start-btn'); 


// === GAME BOARD ===

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
            tile.addEventListener('click', () => toggleTileState(tile, r));
            rowDiv.appendChild(tile);
        }
        board.appendChild(rowDiv);
    }
}

function toggleTileState(tile, rowIdx) {
    if (isGameOver) return;
    if (tile.innerText === '') return;
    if (rowIdx !== currentRowIndex - 1) return;

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
    
    if (currentRowIndex > 0) {
        const prevRow = currentRowIndex - 1;
        for(let i=0; i<COLS; i++) {
            document.getElementById(`tile-${prevRow}-${i}`).classList.add('locked');
        }
    }

    for (let i = 0; i < COLS; i++) {
        const tile = document.getElementById(`tile-${currentRowIndex}-${i}`);
        tile.innerText = word[i];
        tile.setAttribute('data-state', 'absent'); 
        tile.classList.remove('locked');
    }
    currentRowIndex++;
}


// === MODALS + GAME STATE ===

function handleGameOver() {
    isGameOver = true; 
    submitBtn.style.display = 'none'; 
    restartBtn.style.display = 'inline-block'; 
    
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


// === EVENT LISTENERS ===

// Instructions
if (startBtn) {
    startBtn.addEventListener('click', () => {
        if(instructionModal) instructionModal.classList.add('hidden');
    });
}

// Restart button
restartBtn.addEventListener('click', () => {
    currentRowIndex = 0;
    isGameOver = false;
    restartBtn.style.display = 'none';
    submitBtn.style.display = 'inline-block';
    submitBtn.disabled = false;
    submitBtn.innerText = "Send Hints";
    initBoard(); 
    startGame();
});

// Submit button
submitBtn.addEventListener('click', () => {
    const resultString = generateHintString();
    if (!resultString) return;

    if (resultString === 'ggggg') {
        showModal('win', "Bot found the word!");
        handleGameOver();
        return;
    }

    if (currentRowIndex === ROWS) {
        showModal('loss', "WordNotFound error.");
        handleGameOver();
        return;
    }

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

// Enter button
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        // If modal is open -> enter to close
        if (instructionModal && !instructionModal.classList.contains('hidden')) {
            startBtn.click();
            return;
        }

        if (!modal.classList.contains('hidden')) {
            closeModal();
            return;
        }

        // If game is active -> send hints
        if (!submitBtn.disabled && submitBtn.style.display !== 'none') {
            submitBtn.click();
        }
    }
});


// === INITIALIZATION ===

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

initBoard();
startGame();