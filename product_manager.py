import os
from textblob import TextBlob
from panda_brain_v1 import PandaCharacter,PandaBrain
from personality import PandyVoice
from dotenv import load_dotenv

load_dotenv()
brain = PandaBrain()


# Your other imports (like json, time, etc.) go down here...

def process_pandy_logic(user_input,chat_history=[]):
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
    history_context = ""
    if chat_history:
         history_context = "Recent Conversation History:\n"
         for exchange in chat_history:
             history_context += f"User said: '{exchange['user']}' -> Pandy responded: '{exchange['pandy']}'\n"
         history_context += "\n"

    # 2. Combine the history context with the system rules and the NEW input
    system_instruction = (
        "You are an AI routing system for a virtual panda pet named Pandy.\n"
        "Analyze the user's intent based on the conversation history and the new input.\n"
        "Output 'ACTION: PLAY' if they want to play a game, 'ACTION: SLEEP' for sleep, etc.\n\n"
    )
    
    # Construct the final massive payload for Gemini
    final_prompt = (
        "=== SYSTEM ARCHITECTURE RULES ===\n"
        "You are an AI routing backend. Your ONLY job is to output a single, precise action tag.\n"
        "Do NOT have a conversation. Do NOT reply with random sentences.\n"
        "Available Action Tags:\n"
        "- If user wants to play/have fun: 'ACTION: PLAY'\n"
        "- If user wants to check status/vitals: 'ACTION: STATUS'\n"
        "- If user wants Pandy to sleep/rest: 'ACTION: SLEEP'\n"
        "=================================\n\n"
        
        "=== CONVERSATION LOGS (FOR CONTEXT ONLY) ===\n"
        f"{history_context}"
        "============================================\n\n"
        
        "=== CURRENT EXECUTION TASK ===\n"
        f"NEW_USER_INPUT: {user_input}\n"
        "YOUR TARGET OUTPUT (Choose exactly ONE tag from the rules above): "
    )
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
        '1':lambda: active_panda.status,
        '2':lambda: active_panda.get_temp,
        '3': lambda:active_panda.feedpanda,
        '4': lambda:active_panda.manual_metabolism,
        '5': lambda:active_panda.play_game,
        '6':lambda: active_panda.sleep,
        '7': lambda:active_panda.mood_now,
        '8':lambda:active_panda.show_log,
        'nlp':lambda:active_panda.make,
        '9':lambda:brain.handle_chat_session(active_panda)
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
            raw_result = process_pandy_logic(user_choice, active_panda.chat_history)
            print(f"\n[DEBUG AI RESPONSE]: {raw_result}") 
            
            # B. CHECK 1: Is Gemini just trying to talk back to us? (Reassurance)
            if "REASSURANCE" in raw_result.upper():
                print(raw_result) # Prints Pandy's conversational reply directly!
                action_code = None
            
            # C. CHECK 2: If it's an action, look for the keywords
            else:
                combined_text = (raw_result + " " + user_choice).upper()
                action_code = None
                
                if "PLAY" in combined_text or "FUN" in combined_text:
                    print("🎮 Pandy is playing and having fun!")
                    action_code = '5'
                elif "SLEEP" in combined_text or "REST" in combined_text:
                    print("💤 Putting Pandy to sleep...")
                    action_code = '6'
                elif "STATUS" in combined_text or "VITALS" in combined_text:
                    action_code = '1'
                elif "GET" in combined_text: 
                    action_code = '2'
                elif "FEED" in combined_text: 
                    action_code = '3'
                elif "MANUAL" in combined_text: 
                    action_code = '4'
                elif "MOOD" in combined_text: 
                    action_code = '7'
                elif "LOGS" in combined_text: 
                    action_code = '8'
                elif "NLP" in combined_text: 
                    action_code = 'nlp'
                elif "ASK" in combined_text: 
                    action_code = '9'

            # D. EXECUTION: Run the mapped action code if one was found
            if action_code and action_code in action_map:
                execution_result = action_map[action_code]()
                if execution_result is True:
                    print("🔌 Router loop broken. Hard execution halt.")
                    break
            elif "REASSURANCE" not in raw_result.upper():
                # Only print the error fallback if it wasn't a valid reassurance message
                print("🐼 Panda: 'I don't understand that!'")

            # E. Update rolling chat history log
            active_panda.update_chat_history(user_choice, raw_result)
            
        # Run your post-turn vitals check
        active_panda.check_hunger(active_panda)
        # 1. Get the raw text from your Gemini processing function
           
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
    # 3. Trigger the defensive gatekeeper check
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("\n[CRITICAL ERROR]: System boot aborted.")
        print("Reason: 'GEMINI_API_KEY' is missing from the environment configuration.\n")
        exit()

    
    print("[SYSTEM]: Environment verified. Booting Panda AI Engine...")
    brain=PandaBrain()
    main_lobby()  # 👈 Just run your lobby directly here now!