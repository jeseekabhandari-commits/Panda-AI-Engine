import os
import json
from textblob import TextBlob
from panda_brain_v1 import PandaCharacter

def process_pandy_logic(user_input):
    blob = TextBlob(user_input)
    is_negated = blob.sentiment.polarity < -0.1 or "not" in user_input.lower()
    
    intents = {
        "STATUS": ["status", "energy", "point"],
        "FEED": ["eat", "food", "bamboo", "feed"],
        "PLAY": ["game", "play", "fun"],
        "SLEEP": ["sleep", "nap", "rest"],
        "MANUAL": ["manual", "work", "metabolism"],
        "GET": ["temp", "weather", "sync"],
        "CREATE": ["create", "new", "make"]
    }
    
    detected_action = None
    for intent, keywords in intents.items():
        if any(word in user_input.lower() for word in keywords):
            detected_action = intent
            break
            
    if detected_action and is_negated:
        return f"REASSURANCE: No {detected_action}."
    elif detected_action:
        return f"ACTION: {detected_action}"
    return "CONFUSION"

def main_game_loop(active_panda):
    action_map = {
        '1': active_panda.status,
        '2': active_panda.get_temp,
        '3': active_panda.feedpanda,
        '4': active_panda.manual_metabolism,
        '5': active_panda.play_game,
        '6': active_panda.sleep
    }

    while True:
        user_choice = input(f"\n[{active_panda.name}] What should I do?: ").lower()
        
        if user_choice in action_map:
            action_map[user_choice]()
        else:
            result = process_pandy_logic(user_choice)
            
        if "REASSURANCE" in result:
          print(result) # This tells the user: "I understand you do NOT want to..."
          # We stop here so the action doesn't execute
        elif "ACTION" in result:
           # Here you map 'FEED' -> '3', 'PLAY' -> '5', etc.
           # Then execute action_map[action_code]()
            # Map NLP results to codes
            action_code = None
            if "STATUS" in result: action_code = '1'
            elif "GET" in result: action_code = '2' # Fixed to match Brain
            elif "FEED" in result: action_code = '3'
            elif "MANUAL" in result: action_code = '4'
            elif "PLAY" in result: action_code = '5'
            elif "SLEEP" in result: action_code = '6'
            
            # THE CREATE FIX
            elif "CREATE" in result:
                print("Exiting to Lobby to make a new friend...")
                return # Breaks out of play_with_panda back to lobby

            if action_code in action_map:
                action_map[action_code]()
            else:
                print("Panda: 'I don't understand that!'")

def play_with_panda(active_panda):
    active_panda.apply_decay() 
    active_panda.show_menu() 
    main_game_loop(active_panda)

def main_lobby():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=== PANDA ENGINE ===")
        
        if not os.path.exists("all_pandas"): os.makedirs("all_pandas")
        files = os.listdir("all_pandas")
        pandas = [f.removesuffix(".json") for f in files if f.endswith(".json")]

        for i, name in enumerate(pandas, 1):
            print(f"{i}. {name}")

        new_opt = len(pandas) + 1
        print(f"{new_opt}. Create New Panda")
        print("0. Exit")

        choice = input("\nSelect: ")

        if choice == '0':
            exit()
        elif choice == str(new_opt):
            name = input("New Name: ").strip()
            if name:
                p = PandaCharacter(name=name)
                p.save_memory_made()
                play_with_panda(p)
        elif choice.isdigit() and 1 <= int(choice) <= len(pandas):
            name = pandas[int(choice) - 1]
            # To be truly error-free, we'd load the JSON data here, 
            # but this will work for basic name activation:
            p = PandaCharacter(name=name)
            play_with_panda(p)

if __name__ == "__main__":
    main_lobby()