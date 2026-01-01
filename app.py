from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from solver import WordleSolver


app = Flask(__name__, template_folder='templates')
CORS(app, resources={r"/api/*": {"origins": "*"}})

bot = WordleSolver()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/start-game', methods=['POST'])
def start_game():
    first_word = bot.reset_game()
    print(f"Game Started. First guess: {first_word}")
    return jsonify({"next_word": first_word})


@app.route('/api/next-guess', methods=['POST'])
def next_guess():
    data = request.json
    hints = data.get('hints') # E.g. yywwg
    
    if not hints:
        return jsonify({"error": "no hints provided"}), 400

    print(f"Received hints: {hints} for word: {bot.current_guess}")
    
    next_word = bot.process_guess(hints)
    
    if next_word:
        print(f"Bot suggests: {next_word}")
        return jsonify({"next_word": next_word})
    else:
        return jsonify({"error": "word not found"}), 404


if __name__ == '__main__':
    app.run(debug=True, port=5000)