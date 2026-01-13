from pydantic import BaseModel

class OpeningMove(BaseModel):
    uci: str
    san: str
    play_rate: float
    white_win_rate: float
    black_win_rate: float

class OpeningResponse(BaseModel):
    total_games: int
    moves: list[OpeningMove]
