from pydantic import BaseModel

class PuzzleMove(BaseModel):
    uci: str
    san: str

class PuzzleResponse(BaseModel):
    fen: str
    moves: list[PuzzleMove]

class MoveSubmission(BaseModel):
    fen: str
    move: str
