import random
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def initialize_board():
    """
    Inicjalizacja planszy zgodnie z zasadami Backgammon.
    Plansza jest reprezentowana jako słownik z trzema kluczami:
      - "board": lista 24 punktów (indeksy 0-23 odpowiadają punktom 1-24).
        Ustawienia:
          Gracz A (białe) (dolna część planszy – punkty 12 do 1):
            • Punkt 1 (index 0): 5 pionków
            • Punkt 6 (index 5): 5 pionków
            • Punkt 8 (index 7): 3 pionki
            • Punkt 12 (index 11): 5 pionków
          Gracz B (czarne) (górna część planszy – punkty 13 do 24):
            • Punkt 13 (index 12): 5 pionków
            • Punkt 17 (index 16): 3 pionki
            • Punkt 19 (index 18): 5 pionków
            • Punkt 24 (index 23): 5 pionków
      - "bar": miejsce dla zbitych pionków, osobno dla obu graczy.
      - "out": miejsce, gdzie trafiają pionki wyprowadzone z planszy.
    """
    board = [[] for _ in range(24)]
    
    # Ustawienia dla gracza A (białe) – dolna część planszy (punkty 1, 6, 8, 12)
    board[0]   = ["A"] * 5    # Punkt 1 (index 0)
    board[5]   = ["A"] * 5    # Punkt 6 (index 5)
    board[7]   = ["A"] * 3    # Punkt 8 (index 7)
    board[11]  = ["A"] * 5    # Punkt 12 (index 11)
    
    # Ustawienia dla gracza B (czarne) – górna część planszy (punkty 13, 17, 19, 24)
    board[12]  = ["B"] * 5    # Punkt 13 (index 12)
    board[16]  = ["B"] * 3    # Punkt 17 (index 16)
    board[18]  = ["B"] * 5    # Punkt 19 (index 18)
    board[23]  = ["B"] * 5    # Punkt 24 (index 23)
    
    return {
        "board": board,
        "bar": {"A": [], "B": []},
        "out": {"A": [], "B": []}
    }

# Inicjalizacja stanu planszy
board_state = initialize_board()

current_roll = (1, 1)  # Domyślne wartości kostek (aktualizowane przez endpoint /roll-dice)
current_player = "A"   # Początkowo ruch ma gracz A (białe)

@app.route("/")
def start():
    return render_template("start.html")

@app.route("/hot_seat")
def hot_seat():
    return render_template("hot_seat.html")

@app.route("/roll-dice", methods=["POST"])
def roll_dice():
    global current_roll
    dice1 = random.randint(1, 6)
    dice2 = random.randint(1, 6)
    current_roll = (dice1, dice2)
    return jsonify({"dice1": dice1, "dice2": dice2})

@app.route("/move", methods=["POST"])
def move():
    data = request.get_json()
    start = data.get("start")     # Numer punktu startowego (1-24)
    end = data.get("end")         # Numer punktu docelowego (1-24)
    player = data.get("player")   # Identyfikator gracza ("A" lub "B")
    move_value = data.get("move_value")  # Liczba pól, o które ma zostać przesunięty pionek
    dice1 = data.get("dice1Python")   # Identyfikator gracza ("A" lub "B")
    dice2 = data.get("dice2Python")
    
    if start is None or end is None or move_value is None or player is None:
        return jsonify({"message": "Błąd: Nieprawidłowe dane ruchu"}), 400

    print(f"Gracz {player} próbuje przesunąć pionek z {start} do {end} przy wartości {move_value}")

    # Sprawdzenie, czy move_value odpowiada jednej z wyrzuconych kostek (lub ich sumie)
    dice1, dice2 = current_roll
    valid_moves = {dice1, dice2, dice1 + dice2}
    print(dice1)
    print(dice2)
    print(current_roll)
    print(valid_moves)
    print(move_value)
    if move_value not in valid_moves:
        return jsonify({"message": "Błąd: Nieprawidłowa wartość ruchu"}), 400

    # Sprawdzenie zakresu punktów
    if start < 1 or start > 24 or end < 1 or end > 24:
        return jsonify({"message": "Błąd: Ruch poza zakresem planszy"}), 400

    # Sprawdzenie, czy różnica między punktami odpowiada move_value
    if abs(start - end) != move_value:
        return jsonify({"message": "Błąd: Ruch nie odpowiada wartości kostek"}), 400

    # Sprawdzenie, czy na punkcie startowym znajduje się pionek danego gracza
    
    # Wykonanie ruchu: usunięcie (pop) ostatniego pionka z punktu startowego i dodanie go do punktu docelowego
    board_state["board"][start - 1].pop()
    board_state["board"][end - 1].append(player)
    
    return jsonify({"message": f"Ruch wykonany: {start} → {end} (wartość: {move_value})"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=12239, debug=True)
