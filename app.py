import random
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def initialize_board():
    """
    Inicjalizacja planszy zgodnie z zasadami Backgammon.
    Plansza jest reprezentowana jako słownik, gdzie:
      - "board" to lista 24 punktów (numerowanych od 1 do 24) – każdy punkt to lista pionków.
      - "bar" to miejsce, gdzie trafiają zbite pionki.
      - "out" to miejsce, gdzie trafiają pionki wyprowadzone z planszy.
    """
    return {
        "board": [
            ["A", "A"],  # Punkt 24: dla gracza A (białe) – 2 pionki
            [],          # Punkt 23
            [],          # Punkt 22
            [],          # Punkt 21
            [],          # Punkt 20
            ["B", "B", "B", "B", "B"],  # Punkt 19: dla gracza B (czarne) – 5 pionków
            [],          # Punkt 18
            [],          # Punkt 17 (dla gracza B chcemy 3 pionki, więc umieścimy je później)
            [],          # Punkt 16
            [],          # Punkt 15
            ["A", "A", "A", "A", "A"],  # Punkt 14 (opcjonalnie)
            ["A", "A", "A", "A", "A"],  # Punkt 13: dla gracza A – 5 pionków
            ["A", "A", "A"],            # Punkt 12: dla gracza A – 3 pionki
            [],          # Punkt 11
            [],          # Punkt 10
            [],          # Punkt 9
            ["B", "B", "B"],            # Punkt 8: dla gracza B – 3 pionki
            [],          # Punkt 7
            [],          # Punkt 6: dla gracza A – 5 pionków
            ["B", "B", "B", "B", "B"],  # Punkt 5: dla gracza B – 5 pionków
            [],          # Punkt 4
            [],          # Punkt 3
            [],          # Punkt 2
            ["B", "B"]   # Punkt 1: dla gracza B – 2 pionki
        ],
        "bar": {"A": [], "B": []},
        "out": {"A": [], "B": []}
    }

# Inicjalizacja stanu planszy
board_state = initialize_board()

current_roll = (1, 1)  # Aktualne wartości kostek
current_player = "A"   # Gracz, który ma ruch (A lub B)


@app.route("/")
def start():
    return render_template("start.html")

@app.route("/hot_seat")
def hot_seat():
    # Strona trybu hot-seat
    return render_template("hot_seat.html")

@app.route("/roll-dice", methods=["POST"])
def roll_dice():
    global current_roll
    dice1 = random.randint(1, 6)
    dice2 = random.randint(1, 6)
    current_roll = (dice1, dice2)
    return jsonify({"dice1": dice1, "dice2": dice2})

@app.route('/move', methods=['POST'])
def move():
    data = request.get_json()
    start = data.get('start')
    end = data.get('end')
    player = data.get('player')
    move_value = data.get('move_value')
    
    if start is None or end is None or move_value is None or player is None:
        return jsonify({'message': 'Błąd: Nieprawidłowe dane ruchu'}), 400

    print(f'Gracz {player} próbuje przesunąć pionek z {start} do {end} przy wartości {move_value}')
    
    # Sprawdzenie, czy ruch jest zgodny z rzutami kostkami
    dice1, dice2 = current_roll
    valid_moves = {dice1, dice2, dice1 + dice2}
    if move_value not in valid_moves:
        return jsonify({'message': 'Błąd: Nieprawidłowa wartość ruchu'}), 400

    # Sprawdzenie poprawności ruchu na planszy
    if start < 1 or start > 24 or end < 1 or end > 24:
        return jsonify({'message': 'Błąd: Ruch poza zakresem planszy'}), 400
    
    if abs(start - end) != move_value:
        return jsonify({'message': 'Błąd: Ruch nie odpowiada wartości kostek'}), 400

    # Sprawdzenie, czy na polu startowym znajduje się pionek gracza
    if not board_state['board'][start - 1] or board_state['board'][start - 1][-1] != player:
        return jsonify({'message': 'Błąd: Brak pionka gracza na polu startowym'}), 400

    # Przeniesienie pionka
    board_state['board'][start - 1].pop()
    board_state['board'][end - 1].append(player)
    return jsonify({'message': f'Ruch wykonany: {start} → {end} (wartość: {move_value})'}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=12239, debug=True)
