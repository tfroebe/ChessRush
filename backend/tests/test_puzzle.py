import pytest
from unittest.mock import patch

from app.services.puzzle import (
    generate_puzzle,
    public_puzzle_view,
    evaluate_player_move,
)

# -----------------------------
# Test Fixtures
# -----------------------------

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

MOCK_LICHESS_DATA = {
    "moves": [
        {
            "uci": "e2e4",
            "san": "e4",
            "white": 0.55,
            "draw": 0.25,
            "games": 12000,
        },
        {
            "uci": "d2d4",
            "san": "d4",
            "white": 0.54,
            "draw": 0.26,
            "games": 9000,
        },
        {
            "uci": "g1f3",
            "san": "Nf3",
            "white": 0.50,
            "draw": 0.30,
            "games": 200,   # Below MIN_GAMES threshold
        },
        {
            "uci": "a2a4",
            "san": "a4",
            "white": 0.40,
            "draw": 0.20,
            "games": 5000,  # Bad but popular
        },
    ]
}


# -----------------------------
# Core Logic Tests
# -----------------------------

def test_generate_puzzle_hybrid_logic():
    """
    Ensures hybrid logic:
    - Accepts strong statistical moves
    - Rejects weak popular moves
    - Rejects low-sample moves
    """

    with patch("app.services.puzzle.fetch_opening_data") as fetch_mock, \
         patch("app.services.puzzle.normalize_opening_data") as normalize_mock, \
         patch("app.services.puzzle.evaluate_position_after_move") as eval_mock:

        fetch_mock.return_value = {}
        normalize_mock.return_value = MOCK_LICHESS_DATA
        eval_mock.return_value = None  # Stockfish disabled for this test

        puzzle = generate_puzzle(START_FEN)

        correct_moves = puzzle["correct_moves"]

        assert "e2e4" in correct_moves
        assert "d2d4" in correct_moves

        # Below MIN_GAMES → rejected
        assert "g1f3" not in correct_moves

        # Popular but bad → rejected
        assert "a2a4" not in correct_moves


def test_stockfish_fallback_accepts_rare_strong_move():
    """
    Ensures Stockfish fallback allows a rare but engine-approved move.
    """

    rare_strong_move = {
        "uci": "h2h4",
        "san": "h4",
        "white": 0.48,
        "draw": 0.30,
        "games": 3000,
    }

    data = {"moves": MOCK_LICHESS_DATA["moves"] + [rare_strong_move]}

    with patch("app.services.puzzle.fetch_opening_data"), \
         patch("app.services.puzzle.normalize_opening_data", return_value=data), \
         patch("app.services.puzzle.evaluate_position_after_move", return_value=0.10):

        puzzle = generate_puzzle(START_FEN)

        assert "h2h4" in puzzle["correct_moves"]


# -----------------------------
# Public View Safety Test
# -----------------------------

def test_public_puzzle_view_hides_answers():
    puzzle = {
        "fen": START_FEN,
        "moves": [
            {"uci": "e2e4", "san": "e4"},
            {"uci": "d2d4", "san": "d4"},
        ],
        "correct_moves": ["e2e4"],
    }

    public = public_puzzle_view(puzzle)

    assert "correct_moves" not in public
    assert "moves" in public
    assert len(public["moves"]) == 2


# -----------------------------
# Player Move Evaluation Tests
# -----------------------------

def test_evaluate_player_move_correct():
    puzzle = {
        "fen": START_FEN,
        "correct_moves": ["e2e4", "d2d4"],
    }

    result = evaluate_player_move(puzzle, "e2e4")

    assert result["correct"] is True
    assert "e2e4" in result["correct_moves"]


def test_evaluate_player_move_incorrect():
    puzzle = {
        "fen": START_FEN,
        "correct_moves": ["e2e4", "d2d4"],
    }

    result = evaluate_player_move(puzzle, "a2a4")

    assert result["correct"] is False
