from fastapi import FastAPI
from app.api.opening import router as opening_router
from app.api.puzzle import router as puzzle_router

app = FastAPI(
    title="ChessRush Opening Trainer API",
    version="0.1.0"
)

app.include_router(opening_router)
app.include_router(puzzle_router)

@app.get("/")
def root():
    return {"status": "ok"}
