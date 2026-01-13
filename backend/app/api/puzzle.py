from fastapi import APIRouter, HTTPException
from app.services.puzzle import generate_puzzle, public_puzzle_view
from app.schemas.puzzle import PuzzleResponse
import chess
from app.schemas.puzzle import MoveSubmission

router = APIRouter(prefix="/puzzle", tags=["Puzzle"])

@router.get("/", response_model=PuzzleResponse)
async def get_puzzle(fen: str):
    puzzle = generate_puzzle(fen)
    return public_puzzle_view(puzzle)

@router.post("/submit")
async def submit_move(payload: MoveSubmission):
    puzzle = generate_puzzle(payload.fen)

    board = chess.Board(payload.fen)
    try:
        move = chess.Move.from_uci(payload.move)
        if move not in board.legal_moves:
            raise ValueError
    except ValueError:
        raise HTTPException(status_code=400, detail="Illegal move")

    correct = payload.move in puzzle["correct_moves"]

    return {
        "correct": correct,
        "correct_moves": puzzle["correct_moves"],
    }