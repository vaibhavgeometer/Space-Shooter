import os
import json
from .constants import HIGH_SCORE_FILE, Difficulty, DIFFICULTY_PARAMS
from . import globals

def update_globals_from_data():
    key = globals.current_difficulty.name
    globals.high_score = globals.game_data[key]["high_score"]
    globals.games_played = globals.game_data[key]["games_played"]

def load_game_data():
    # Initialize defaults
    for diff in Difficulty:
        globals.game_data[diff.name] = {"high_score": 0, "games_played": 0}

    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, 'r') as f:
                loaded = json.load(f)
                
                # Check if legacy format (no "NORMAL" key)
                if "high_score" in loaded:
                     # Migrate legacy to NORMAL
                     globals.game_data["NORMAL"]["high_score"] = loaded.get("high_score", 0)
                     globals.game_data["NORMAL"]["games_played"] = loaded.get("games_played", 0)
                else:
                    # New format
                    for key in loaded:
                        if key in globals.game_data:
                            globals.game_data[key] = loaded[key]
        except:
            pass
            
    # Set current globals based on current difficulty
    update_globals_from_data()

def save_game_data():
    # Update current session data into storage
    key = globals.current_difficulty.name
    
    if globals.score > globals.game_data[key]["high_score"]:
        globals.game_data[key]["high_score"] = globals.score
        
    globals.game_data[key]["games_played"] += 1
        
    try:
        with open(HIGH_SCORE_FILE, 'w') as f:
            json.dump(globals.game_data, f, indent=4)
    except:
        pass

def change_difficulty(direction):
    difficulty_keys = list(DIFFICULTY_PARAMS.keys())
    idx = difficulty_keys.index(globals.current_difficulty)
    new_idx = (idx + direction) % len(difficulty_keys)
    globals.current_difficulty = difficulty_keys[new_idx]
    update_globals_from_data()
