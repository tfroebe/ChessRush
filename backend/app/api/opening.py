from fastapi import APIRouter, HTTPException
from app.services.lichess import fetch_opening_data
from app.services.chess_utils import validate_fen
from app.schemas.opening import OpeningResponse
from app.services.lichess import normalize_opening_data

router = APIRouter(prefix="/opening", tags=["Opening"])

@router.get("/", response_model=OpeningResponse)
async def get_opening(fen: str):
    try:
        validate_fen(fen)
        raw_data = fetch_opening_data(fen)
        return normalize_opening_data(raw_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
