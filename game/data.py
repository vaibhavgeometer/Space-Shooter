import os
import pickle
from .constants import Difficulty, DIFFICULTY_PARAMS
from . import globals

import shutil

SAVE_FILE__NAME = "save_data.dat"

# Determine path based on OS to hide the save file
if os.name == 'nt':
    # Windows: %LOCALAPPDATA%\SpaceShooter
    save_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'SpaceShooter')
else:
    # Unix-like: ~/.local/share/SpaceShooter
    save_dir = os.path.join(os.path.expanduser('~'), '.local', 'share', 'SpaceShooter')

# Ensure directory exists
os.makedirs(save_dir, exist_ok=True)

SAVE_FILE = os.path.join(save_dir, SAVE_FILE__NAME)
OLD_SAVE_FILE = SAVE_FILE__NAME

# Migrate legacy save file if it exists in the root directory
if os.path.exists(OLD_SAVE_FILE):
    try:
        # If destination exists (and source also exists), we might want to keep the newer one? 
        # For simplicity, if destination doesn't exist, we move. 
        # If destination exists, we might ignore the old one or overwrite.
        # Let's assume if target exists, it's the valid one. Only move if target missing.
        if not os.path.exists(SAVE_FILE):
            shutil.move(OLD_SAVE_FILE, SAVE_FILE)
            print(f"Migrated save file to: {SAVE_FILE}")
        else:
            # If both exist, check which is newer.
            # This handles the case where the user played and saved to the old location
            # after we created the new location but before restarting the game.
            old_mtime = os.path.getmtime(OLD_SAVE_FILE)
            new_mtime = os.path.getmtime(SAVE_FILE)
            
            if old_mtime > new_mtime:
                try:
                    # Remove old destination to allow move
                    os.remove(SAVE_FILE)
                    shutil.move(OLD_SAVE_FILE, SAVE_FILE)
                    print(f"Updated hidden save with newer file from root.")
                except Exception as e:
                    print(f"Failed to update hidden save: {e}")
            else:
                try:
                    os.remove(OLD_SAVE_FILE)
                    print("Removed redundant save file from root.")
                except:
                    pass
    except Exception as e:
        print(f"Failed to migrate save file: {e}")

def update_globals_from_data():
    key = globals.current_difficulty.name
    globals.high_score = globals.game_data[key]["high_score"]
    globals.games_played = globals.game_data[key]["games_played"]

def load_game_data():
    # Initialize defaults first
    for diff in Difficulty:
        globals.game_data[diff.name] = {"high_score": 0, "games_played": 0}

    # Try to load from file
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "rb") as f:
                saved_data = pickle.load(f)
                # Merge saved data purely to be safe, or just replace
                # We'll valid keys to avoid corruption issues
                for key in globals.game_data:
                    if key in saved_data:
                        globals.game_data[key] = saved_data[key]
        except Exception as e:
            print(f"Error loading save data: {e}")

    # Set current globals based on current difficulty
    update_globals_from_data()

def save_game_data():
    # Update current session data into storage
    key = globals.current_difficulty.name
    
    if globals.score > globals.game_data[key]["high_score"]:
        globals.game_data[key]["high_score"] = globals.score
        
    globals.game_data[key]["games_played"] += 1
    
    # Write to file
    try:
        with open(SAVE_FILE, "wb") as f:
            pickle.dump(globals.game_data, f)
    except Exception as e:
        print(f"Error saving game data: {e}")

def change_difficulty(direction):
    difficulty_keys = list(DIFFICULTY_PARAMS.keys())
    idx = difficulty_keys.index(globals.current_difficulty)
    new_idx = (idx + direction) % len(difficulty_keys)
    globals.current_difficulty = difficulty_keys[new_idx]
    update_globals_from_data()
