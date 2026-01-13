from typing import List, Dict, Optional

from app.services.lichess import (
    fetch_opening_data,
    normalize_opening_data,
)
from app.services.stockfish import (
    evaluate_position_after_move,
)

# -----------------------------
# Theory Detection Parameters
# -----------------------------

WIN_RATE_DELTA = 0.02       # Accept moves within 2% of best win score
MIN_GAMES = 500             # Ignore moves with tiny sample sizes
MAX_EVAL_LOSS = 0.25        # Stockfish: max acceptable pawn loss
USE_STOCKFISH_FALLBACK = True


# -----------------------------
# Core Puzzle Generation Logic
# -----------------------------

def generate_puzzle(fen: str) -> Dict:
    """
    Generates an internal puzzle object for a given FEN.

    Internal puzzle includes:
    - fen
    - all candidate moves
    - list of correct moves (hidden from frontend)
    """

    raw_data = fetch_opening_data(fen)
    data = normalize_opening_data(raw_data)

    moves = data["moves"]

    if not moves:
        raise ValueError("No opening data available for this position")

    # Compute win score: win + 0.5 * draw
    for move in moves:
        move["win_score"] = move["white"] + 0.5 * move["draw"]

    best_win_score = max(m["win_score"] for m in moves)

    acceptable_moves: List[str] = []

    for move in moves:
        # Skip statistically insignificant moves
        if move["games"] < MIN_GAMES:
            continue

        # Rule 1: Lichess statistical strength
        if move["win_score"] >= best_win_score - WIN_RATE_DELTA:
            acceptable_moves.append(move["uci"])
            continue

        # Rule 2: Stockfish fallback (rare but strong theory)
        if USE_STOCKFISH_FALLBACK:
            eval_loss = evaluate_position_after_move(
                fen=fen,
                uci_move=move["uci"]
            )

            if eval_loss is not None and eval_loss <= MAX_EVAL_LOSS:
                acceptable_moves.append(move["uci"])

    return {
        "fen": fen,
        "moves": moves,               # Full move metadata (internal only)
        "correct_moves": acceptable_moves,
    }


# -----------------------------
# Public Puzzle View
# -----------------------------

def public_puzzle_view(puzzle: Dict) -> Dict:
    """
    Converts internal puzzle data into a safe, public-facing format.

    - Removes correct move list
    - Exposes only what the frontend needs
    """

    return {
        "fen": puzzle["fen"],
        "moves": [
            {
                "uci": move["uci"],
                "san": move["san"],
            }
            for move in puzzle["moves"]
        ],
    }


# -----------------------------
# Puzzle Evaluation
# -----------------------------

def evaluate_player_move(
    puzzle: Dict,
    uci_move: str
) -> Dict:
    """
    Evaluates a player's submitted move.
    """

    correct_moves = puzzle["correct_moves"]

    return {
        "correct": uci_move in correct_moves,
        "correct_moves": correct_moves,
    }