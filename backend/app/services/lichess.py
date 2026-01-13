import requests

LICHESS_EXPLORER_URL = "https://explorer.lichess.ovh/lichess"

def fetch_opening_data(
    fen: str,
    moves: int = 8,
    speeds: list[str] | None = None,
    ratings: list[int] | None = None
):
    params = {
        "fen": fen,
        "moves": moves,
    }

    if speeds:
        params["speeds"] = ",".join(speeds)

    if ratings:
        params["ratings"] = ",".join(map(str, ratings))

    response = requests.get(LICHESS_EXPLORER_URL, params=params, timeout=5)
    response.raise_for_status()

    return response.json()


def normalize_opening_data(raw_data: dict):
    total_games = raw_data.get("white", 0) + raw_data.get("black", 0) + raw_data.get("draws", 0)

    moves = []
    for move in raw_data.get("moves", []):
        move_total = move["white"] + move["black"] + move["draws"]

        moves.append({
            "uci": move["uci"],
            "san": move["san"],
            "play_rate": move_total / total_games if total_games else 0,
            "white_win_rate": move["white"] / move_total if move_total else 0,
            "black_win_rate": move["black"] / move_total if move_total else 0,
        })

    return {
        "total_games": total_games,
        "moves": sorted(moves, key=lambda m: m["play_rate"], reverse=True)
    }
