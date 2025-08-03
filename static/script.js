// script.js

const API_URL = '';
let currentGame = null;

const elements = {
    logo: document.getElementById('logo'),
    categories: document.getElementById('categories'),
    difficulty: document.getElementById('difficulty'),
    startBtn: document.getElementById('start-btn'),
    hintBtn: document.getElementById('hint-btn'),
    livesCounter: document.getElementById('lives-counter'),
    scoreCounter: document.getElementById('score-counter'),
    currentCategory: document.getElementById('current-category'),
    currentDifficulty: document.getElementById('current-difficulty'),
    robotArt: document.getElementById('robot-art'),
    wordDisplay: document.getElementById('word-display'),
    keyboard: document.getElementById('keyboard'),
    message: document.getElementById('message'),
    modal: document.getElementById('game-modal'),
    modalTitle: document.getElementById('modal-title'),
    modalRobotArt: document.getElementById('modal-robot-art'),
    modalMessage: document.getElementById('modal-message'),
    modalScore: document.getElementById('modal-score'),
    playAgainBtn: document.getElementById('play-again-btn'),
    soundCorrect: document.getElementById('sound-correct'),
    soundWrong: document.getElementById('sound-wrong'),
    soundWin: document.getElementById('sound-win'),
    soundLose: document.getElementById('sound-lose')
};

// ASCII Logo
const LOGO = `
      ██╗    ██╗ ██████╗ ██████╗ ██████╗ ███████╗    ██╗    ██╗ ██████╗ ██████╗ ██╗     ██████╗ 
      ██║    ██║██╔═══██╗██╔══██╗██╔══██╗██╔════╝    ██║    ██║██╔═══██╗██╔══██╗██║     ██╔══██╗
      ██║ █╗ ██║██║   ██║██████╔╝██║  ██║███████╗    ██║ █╗ ██║██║   ██║██████╔╝██║     ██║  ██║
      ██║███╗██║██║   ██║██╔══██╗██║  ██║╚════██║    ██║███╗██║██║   ██║██╔══██╗██║     ██║  ██║
      ╚███╔███╔╝╚██████╔╝██║  ██║██████╔╝███████║    ╚███╔███╔╝╚██████╔╝██║  ██║███████╗██████╔╝
       ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚══════╝     ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═════╝ 
`;

document.addEventListener('DOMContentLoaded', () => {
    elements.logo.textContent = LOGO;
    loadCategories();
    initKeyboard();
    
    elements.startBtn.addEventListener('click', startGame);
    elements.hintBtn.addEventListener('click', useHint);
    elements.playAgainBtn.addEventListener('click', () => {
        elements.modal.style.display = 'none';
        startGame();
    });

    document.addEventListener('keydown', (e) => {
        if (/^[a-z]$/i.test(e.key) && currentGame && currentGame.game_status === 'playing') {
            const key = document.getElementById(`key-${e.key.toLowerCase()}`);
            if (key && !key.disabled) {
                makeGuess(e.key.toLowerCase());
            }
        }
    });
});

function playSound(soundElement) {
    if (soundElement) {
        soundElement.currentTime = 0;
        soundElement.play().catch(e => console.error("Error playing sound:", e));
    }
}

async function loadCategories() {
    try {
        const response = await fetch('/hangman/categories');
        const { categories } = await response.json();
        
        elements.categories.innerHTML = '<option value="">SELECT CATEGORY</option>';
        categories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat;
            option.textContent = cat.toUpperCase();
            elements.categories.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading categories:', error);
        elements.message.textContent = 'Error connecting to server!';
    }
}

async function startGame() {
    const category = elements.categories.value;
    const difficulty = elements.difficulty.value;
    
    if (!category) {
        elements.message.textContent = 'Please select a category first!';
        return;
    }
    
    try {
        const response = await fetch('/hangman/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ category, difficulty })
        });
        
        currentGame = await response.json();
        updateUI();
        resetKeyboard();
        elements.hintBtn.disabled = false;
        elements.hintBtn.textContent = 'EMERGENCY HINT';
        elements.message.textContent = 'Rescue mission started! Guess letters to save the robot!';
    } catch (error) {
        console.error('Error starting game:', error);
        elements.message.textContent = 'Error starting game!';
    }
}

async function makeGuess(letter) {
    if (!currentGame || currentGame.game_status !== 'playing') return;
    
    try {
        const response = await fetch('/hangman/guess', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ letter })
        });
        
        const result = await response.json();
        currentGame = result;
        
        updateUI();
        updateKeyboardFeedback(letter, result);
        checkGameEnd(result);
    } catch (error) {
        console.error('Error making guess:', error);
    }
}

function updateUI() {
    if (!currentGame) return;
    
    elements.robotArt.textContent = currentGame.robot_art || '';
    elements.wordDisplay.innerHTML = currentGame.display_word ? currentGame.display_word.map(l => `<span>${l === '_' ? '' : l}</span>`).join('') : '';
    elements.livesCounter.textContent = currentGame.attempts_left || 0;
    elements.scoreCounter.textContent = currentGame.score || 0;
    elements.currentCategory.textContent = (currentGame.selected_category || '').toUpperCase();
    elements.currentDifficulty.textContent = (currentGame.selected_difficulty || '').toUpperCase();
    elements.message.textContent = currentGame.message || '';
}

function updateKeyboardFeedback(letter, result) {
    const key = document.getElementById(`key-${letter}`);
    if (key) {
        key.classList.add('used');
        if (result.is_correct_guess) {
            key.classList.add('correct');
            playSound(elements.soundCorrect);
        } else {
            key.classList.add('incorrect');
            playSound(elements.soundWrong);
        }
    }
}

function checkGameEnd(result) {
    if (!currentGame) return;
    
    elements.robotArt.classList.remove('win-animation');
    elements.modalRobotArt.classList.remove('win', 'lose');

    if (result.game_status === 'won') {
        playSound(elements.soundWin);
        elements.robotArt.classList.add('win-animation');
        elements.modal.style.display = 'block';
        elements.modalTitle.textContent = 'ROBOT RESCUED! 🤖✨';
        elements.modalRobotArt.textContent = result.win_art;
        elements.modalRobotArt.classList.add('win');
        elements.modalMessage.textContent = 'Congratulations! You saved the robot!';
        elements.modalScore.textContent = `Final Score: ${result.score}`;
        disableKeyboard();
    } else if (result.game_status === 'lost') {
        playSound(elements.soundLose);
        elements.modal.style.display = 'block';
        elements.modalTitle.textContent = 'ROBOT MALFUNCTION! ⚠️';
        elements.modalRobotArt.textContent = result.robot_art;
        elements.modalRobotArt.classList.add('lose');
        elements.modalMessage.textContent = `The robot couldn't be saved. The word was: ${result.secret_word.toUpperCase()}`;
        elements.modalScore.textContent = 'Better luck next time!';
        disableKeyboard();
    }
}

async function useHint() {
    elements.hintBtn.disabled = true;
    elements.hintBtn.textContent = 'HINT USED';
    
    try {
        const response = await fetch('/hangman/hint');
        const result = await response.json();
        
        if (result.game_state) {
            currentGame = result.game_state;
            updateUI();
            
            // The hint route now returns the guessed letter directly
            const hintedLetter = result.game_state.guessed_letters[result.game_state.guessed_letters.length - 1];
            const key = document.getElementById(`key-${hintedLetter}`);
            if (key) {
                key.classList.add('correct');
                key.classList.add('used');
            }
            
            elements.message.textContent = result.message;
            checkGameEnd(currentGame);
        } else {
            elements.message.textContent = result.message;
        }
    } catch (error) {
        console.error('Error getting hint:', error);
    }
}

function initKeyboard() {
    elements.keyboard.innerHTML = '';
    const letters = 'abcdefghijklmnopqrstuvwxyz'.split('');
    letters.forEach(letter => {
        const key = document.createElement('button');
        key.id = `key-${letter}`;
        key.className = 'key';
        key.textContent = letter.toUpperCase();
        key.addEventListener('click', () => {
            if (!key.disabled) {
                makeGuess(letter);
            }
        });
        elements.keyboard.appendChild(key);
    });
}

function resetKeyboard() {
    document.querySelectorAll('.key').forEach(key => {
        key.classList.remove('used', 'correct', 'incorrect');
        key.disabled = false;
    });
}

function disableKeyboard() {
    document.querySelectorAll('.key').forEach(key => key.disabled = true);
}