import chess

def validate_fen(fen: str) -> None:
    try:
        chess.Board(fen)
    except ValueError:
        raise ValueError("Invalid FEN string")