import json
import requests
from requests.exceptions import RequestException

import chess.pgn

def apicall(url):
    try:
        response = requests.get(url, timeout=10,
                    headers={"User-Agent": "MyChessApp/1.0 (https://github.com/chiteshmalhotra/WCC26_Analysis)"})
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        print(f"API call to {url} failed: {e}")
        return None
    
def pgn_2_jsonl(input_file, output_file, size = 1000):
    buffer = []
    count  = 0
    
    with open(input_file, 'r') as file_pgn, \
        open(output_file, 'w', encoding='utf-8') as file_json:
        while (game := chess.pgn.read_game(file_pgn)) is not None:
            game_data = dict(game.headers)
            game_data['Moves'] = str(game.mainline_moves())
            buffer.append(game_data)

            count += 1
            print(f"\rProgress: {count}", end="", flush=True)

            if len(buffer) >= size:
                file_json.writelines(json.dumps(entry)+'\n' for entry in buffer)             
                print(f"\rFinished: {count}", flush=True)
                buffer.clear()
                
        if buffer:
            file_json.writelines(json.dumps(entry)+'\n' for entry in buffer)

    print("Processing complete.")

def run_pipeline():
    # 1. API Data Extraction
    playerids = {"GukeshDommaraju": "gukeshdommaraju", "JavokhirSindarov": "javokhir_sindarov05"}
    games = {}

    for player, pid in playerids.items():
        archives = apicall(f"https://api.chess.com/pub/player/{pid}/games/archives")["archives"]
        print(f"Extracting games of {player}")

        games[player] = []
        for url in archives:
            result = apicall(url)
            if result: games[player].extend(result["games"])
                
    with open("data/games.json", "w") as f:
        json.dump(games, f, indent=4)

    # 2. PGN Processing
    pgn_2_jsonl('data/expert_ELO2400.pgn','data/OTB.jsonl')

if __name__ == "__main__":
    run_pipeline()