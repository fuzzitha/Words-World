# app.py
from flask import Flask, request, jsonify, session, render_template
from flask_cors import CORS
import random
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'hangman-secret-key-2024'  # Change this to a secure secret key

# Configure CORS properly for local development
CORS(app, supports_credentials=True, origins=['http://localhost:5000', 'http://127.0.0.1:5000', '*'])

class HangmanGame:
    def __init__(self):
        self.categories = {
            "animals": {
                "easy": ["elephant", "giraffe", "rhinoceros", "hippopotamus", "crocodile"],
                "medium": ["tiger", "zebra", "panda", "koala", "whale"],
                "hard": ["cat", "dog", "rat", "owl", "fox"]
            },
            "fruits": {
                "easy": ["watermelon", "pineapple", "strawberry", "blueberry", "dragonfruit"],
                "medium": ["apple", "banana", "orange", "grape", "mango"],
                "hard": ["fig", "kiwi", "plum", "lime", "date"]
            },
            "countries": {
                "easy": ["australia", "argentina", "venezuela", "bangladesh", "switzerland"],
                "medium": ["india", "japan", "brazil", "france", "canada"],
                "hard": ["usa", "uk", "cuba", "peru", "chad"]
            },
            "technology": {
                "easy": ["computer", "smartphone", "internet", "keyboard", "monitor"],
                "medium": ["robot", "drone", "server", "cloud", "wifi"],
                "hard": ["cpu", "gpu", "ram", "ssd", "api"]
            },
            "sports": {
                "easy": ["basketball", "football", "volleyball", "badminton", "swimming"],
                "medium": ["tennis", "soccer", "hockey", "boxing", "golf"],
                "hard": ["ski", "surf", "dive", "run", "jump"]
            }
        }
        
        # Robot breakdown stages (ASCII art for backend)
        self.breakdown_stages = self._generate_robot_art()
        self.win_art = self._generate_win_art()
        self.reset_game("fruits", "medium")

    def _generate_robot_art(self):
        return [
            # Stage 0: Perfect Robot
            r"""
  ╔═══════╗
  ║ ◉  ◉ ║
  ║  ▼  ║
  ╚═══════╝
    ╔═══╗
    ║   ║
    ║ ▓ ║
    ╚═══╝
    ╔═════╗
    ║     ║
    ╚═════╝
     █  █
    ███ ███
""",
            # Stage 1: Screen flicker
            r"""
  ╔═══════╗
  ║ ◉  ◉ ║
  ║  ▼  ║
  ╚═══════╝
    ╔═══╗
    ║ ⚠ ║
    ║ ▓ ║
    ╚═══╝
    ╔═════╗
    ║     ║
    ╚═════╝
     █  █
    ███ ███
""",
            # Stage 2: One eye damaged
            r"""
  ╔═══════╗
  ║ ✗  ◉ ║
  ║  ▼  ║
  ╚═══════╝
    ╔═══╗
    ║ ⚠ ║
    ║ ▓ ║
    ╚═══╝
    ╔═════╗
    ║     ║
    ╚═════╝
     █  █
    ███ ███
""",
            # Stage 3: Both eyes damaged
            r"""
  ╔═══════╗
  ║ ✗  ✗ ║
  ║  ▼  ║
  ╚═══════╝
    ╔═══╗
    ║ ⚠ ║
    ║ ▓ ║
    ╚═══╝
    ╔═════╗
    ║     ║
    ╚═════╝
     █  █
    ███ ███
""",
            # Stage 4: Arm damage
            r"""
  ╔═══════╗
  ║ ✗  ✗ ║
  ║  ▼  ║
  ╚═══════╝
    ╔═══╗
    ║ ⚠ ║
    ║ ▓ ║
    ╚═══╝
    ╔═════╗
    ║ ✗   ║
    ╚═════╝
     █  █
    ███ ███
""",
            # Stage 5: Leg damage
            r"""
  ╔═══════╗
  ║ ✗  ✗ ║
  ║  ▼  ║
  ╚═══════╝
    ╔═══╗
    ║ ⚠ ║
    ║ ▓ ║
    ╚═══╝
    ╔═════╗
    ║ ✗   ║
    ╚═════╝
     ✗  █
    ███ ███
""",
            # Stage 6: Complete malfunction
            r"""
  ╔═══════╗
  ║ ✗  ✗ ║
  ║  ✗  ║
  ╚═══════╝
    ╔═══╗
    ║ ☠ ║
    ║ ✗ ║
    ╚═══╝
    ╔═════╗
    ║ ✗   ║
    ╚═════╝
     ✗  ✗
    ███ ███
"""
        ]
    
    def _generate_win_art(self):
        return r"""
        /\\
       /  \\
      |    |
  <-- |    | -->
      |    |
       \\  /
        \\/
"""

    def reset_game(self, category, difficulty="medium"):
        if category not in self.categories:
            category = "fruits"
        if difficulty not in ["easy", "medium", "hard"]:
            difficulty = "medium"
            
        self.selected_category = category
        self.selected_difficulty = difficulty
        self.secret_word = random.choice(self.categories[category][difficulty])
        self.guessed_letters = []
        self.incorrect_guesses = 0
        self.attempts_left = 6
        self.game_status = "playing"
        self.hint_used = False
        self.score = 0
        self.start_time = datetime.now()

    def calculate_score(self):
        if self.game_status == "won":
            base_score = len(self.secret_word) * 10
            difficulty_bonus = {"easy": 1, "medium": 1.5, "hard": 2}[self.selected_difficulty]
            attempts_bonus = (6 - self.incorrect_guesses) * 10
            hint_penalty = 10 if self.hint_used else 0
            return max(0, int((base_score + attempts_bonus) * difficulty_bonus - hint_penalty))
        return 0

    def get_hint(self):
        if not self.hint_used and self.game_status == "playing":
            available_letters = [l for l in self.secret_word if l not in self.guessed_letters]
            if available_letters:
                self.hint_used = True
                hint_letter = random.choice(available_letters)
                # Auto-guess the hint letter
                self.make_guess(hint_letter)
                return f"Hint used! The letter '{hint_letter.upper()}' was a good choice!"
        return "No more hints available or game is over."

    def make_guess(self, letter):
        letter = letter.lower()
        message = ""
        is_correct = False
        
        if letter in self.guessed_letters:
            message = "Already guessed!"
        else:
            self.guessed_letters.append(letter)
            if letter in self.secret_word:
                message = f"Good guess! '{letter.upper()}' is in the word!"
                is_correct = True
            else:
                self.incorrect_guesses += 1
                self.attempts_left -= 1
                message = f"Wrong guess! '{letter.upper()}' is not in the word!"

        display_word = [l if l in self.guessed_letters else "_" for l in self.secret_word]
        
        # Check for win/loss conditions
        if "_" not in display_word:
            self.game_status = "won"
            self.score = self.calculate_score()
            message = f"Robot saved! You win! Score: {self.score}"
        elif self.attempts_left <= 0:
            self.game_status = "lost"
            message = "Robot malfunctioned! Game Over!"
            
        robot_art = self.breakdown_stages[self.incorrect_guesses]
        
        return {
            "display_word": display_word,
            "attempts_left": self.attempts_left,
            "game_status": self.game_status,
            "guessed_letters": self.guessed_letters,
            "robot_art": robot_art,
            "secret_word": self.secret_word if self.game_status != "playing" else None,
            "selected_category": self.selected_category,
            "selected_difficulty": self.selected_difficulty,
            "message": message,
            "score": self.score,
            "hint_used": self.hint_used,
            "is_correct_guess": is_correct
        }

# Simplified session management
games = {}
def get_game():
    session_id = request.remote_addr + str(request.headers.get('User-Agent', ''))[:20]
    if session_id not in games:
        games[session_id] = HangmanGame()
    return games[session_id]

# --- Flask Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hangman/start', methods=['POST'])
def start_game():
    data = request.json
    category = data.get("category", "fruits")
    difficulty = data.get("difficulty", "medium")
    
    game = get_game()
    game.reset_game(category, difficulty)
    
    return jsonify({
        "word_length": len(game.secret_word),
        "attempts_left": game.attempts_left,
        "robot_art": game.breakdown_stages[0],
        "win_art": game.win_art,
        "display_word": ["_"] * len(game.secret_word),
        "selected_category": game.selected_category,
        "selected_difficulty": game.selected_difficulty,
        "hint_used": False,
        "score": 0,
        "guessed_letters": []
    })

@app.route('/hangman/guess', methods=['POST'])
def make_guess():
    data = request.json
    letter = data['letter']
    game = get_game()
    return jsonify(game.make_guess(letter))

@app.route('/hangman/hint', methods=['GET'])
def get_hint_route():
    game = get_game()
    message = game.get_hint()
    return jsonify({
        "message": message,
        "hint_used": game.hint_used,
        "game_state": game.make_guess("dummy") # A trick to get the updated state after a hint
    })

@app.route('/hangman/categories', methods=['GET'])
def get_categories():
    game = get_game()
    return jsonify({
        "categories": list(game.categories.keys()),
        "difficulties": ["easy", "medium", "hard"]
    })

if __name__ == '__main__':
    print("🎮 Starting Word Rescue Game...")
    print("🌐 Open your browser and go to: http://localhost:5000")
    print("🤖 Ready to rescue some robots!")
    app.run(debug=True, host='0.0.0.0', port=5000)