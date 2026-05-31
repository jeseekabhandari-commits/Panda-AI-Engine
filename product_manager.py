import os
from textblob import TextBlob
from panda_brain_v1 import PandaCharacter
from personality import PandyVoice
from dotenv import load_dotenv
from panda_brain_v1 import PandaBrain


# Your other imports (like json, time, etc.) go down here...

def process_pandy_logic(user_input):
    blob = TextBlob(user_input)
    is_negated = blob.sentiment.polarity < -0.1 or "not" in user_input.lower()

    intents = {
        "STATUS": ["status", "energy"],
        "FEED": ["eat", "food", "feed"],
        "PLAY": ["game", "play"],
        "SLEEP": ["sleep", "nap"],
        "MANUAL": ["work", "manual"],
        "GET": ["temp", "weather"],
        "CREATE": ["create", "new"],
        "MOOD": ["mood", "cpu"],
        "LOGS":["log","logs"],
        "NLP":["nlp","nl","np","chat","let's","let"],
        "ASK":["talk","ask","lets","sure"]
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
        '6': active_panda.sleep,
        '7': active_panda.mood_now,
        '8':active_panda.show_log,
        'nlp':active_panda.make,
        '9':brain.handle_chat_session(active_panda)
    }

    while True:
        result = ""
         # Ensure result is always defined
        active_panda.background_monitor()
        active_panda.show_menu()
        print(f"Current Energy: {active_panda.energy}%")
        active_panda.hunger_check()
        execution_result = None
        # 4. Check if we need to force a feed (The Hunger Wall)

        user_choice = input(f"\n[{active_panda.name}] Choice: ").lower().strip()
        noemood=active_panda.new.get_mood()
        if noemood =="stressed":
         {
           active_panda.make()
         }
        if user_choice in action_map:
          execution_result =  action_map[user_choice]()
        else:
            result = process_pandy_logic(user_choice)
            
            if "REASSURANCE" in result:
                print(result)
            elif "ACTION" in result:
                action_code = None
                if "STATUS" in result: action_code = '1'
                elif "GET" in result: action_code = '2'
                elif "FEED" in result: action_code = '3'
                elif "MANUAL" in result: action_code = '4'
                elif "PLAY" in result: action_code = '5'
                elif "SLEEP" in result:
                    action_code = '6'

                elif "MOOD" in result: action_code = '7'
                elif "LOGS" in result :action_code = '8'
                elif "NLP" in result :action_code = 'nlp'
                elif "ASK" in result : action_code='9'

                elif "CREATE" in result: return # Back to lobby
                else:
                   print("Panda: 'I don't understand that!'")
           
                if action_code in action_map:
                    execution_result = action_map[action_code]()
                if execution_result is True:
                 print("🔌 Router loop broken. Hard execution halt.")
                 break # This breaks your main while True loop cleanly!
                
            else:
                print("Panda: 'I don't understand that!'")
            active_panda.check_hunger(active_panda)
def play_with_panda(active_panda):
    active_panda.apply_decay() 
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
        print(f"{new_opt}. Create New Panda | 0. Exit")

        choice = input("\nSelect: ")
        if choice == '0': break
        elif choice == str(new_opt):
            name = input("New Name: ").strip()
            if name:
                p = PandaCharacter(name=name)
                p.check_first_boot()
                p.save_memory_made()
                play_with_panda(p)
        elif choice.isdigit() and 1 <= int(choice) <= len(pandas):
            name = pandas[int(choice) - 1]
            p = PandaCharacter(name=name)
             # Simplified load
            p.check_first_boot()
            play_with_panda(p)
        # In your main loop or a choice menu
    input("\nPress Enter to go back...")

if __name__ == "__main__":
    # 1. Load the environment variables instantly
    load_dotenv()

    # 2. Extract the key from memory
    api_key = os.environ.get("GEMINI_API_KEY")

    # 3. Trigger the defensive gatekeeper check
    if not api_key:
        print("\n[CRITICAL ERROR]: System boot aborted.")
        print("Reason: 'GEMINI_API_KEY' is missing from the environment configuration.")
        print("Action Required: Check your local .env file.\n")
        exit()

    # 4. If it passes, your existing code runs safely below this line
    print("[SYSTEM]: Environment verified. Booting Panda AI Engine...")
    # Your engine initialization or menu loop goes here
    brain=PandaBrain()
    main_lobby()