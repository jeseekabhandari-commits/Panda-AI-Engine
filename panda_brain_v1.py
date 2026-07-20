import os
import json
import requests
import random
import datetime
from vitals_engine import VitalsEngine
from personality import PandyVoice
import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai
from pathlib import Path
import streamlit as st

class PandaCharacter:
  
    def __init__(self, name, energy=0, logs=None, video_history=None, last_check=None,user_profile=None):
       # 1. Define the basics first
        self.name = name
        self.video_history = []
        self.new=VitalsEngine()
        self.made=PandyVoice()
        self.date_format="%Y-%m-%d %H:%M:%S"
        self.user_profile={"name": "Unknown","goal": "None","joined_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        self.save_path = f"all_pandas/{self.name}.json"
    
        
        # 2. Try to LOAD from the file
        try:
            with open(self.save_path, 'r') as f:
                data = json.load(f)
                # If we get here, the file is GOOD. Use the data!
                self.energy = data.get('energy', 100)
                self.logs = data.get('logs', [])
                self.last_check = data.get('last_check', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                self.chat_history = data.get('chat_history', [])
                self.user_profile=data.get('user_profile',{"name": "Unknown", "goal": "None"})
        except (json.JSONDecodeError, FileNotFoundError, ValueError):
            # 3. IF THE SHIELD TRIGGERS (File is missing, corrupted, or nonsense)
            print(f"\n[SYSTEM]: Memory corrupted or missing for {self.name}. Resetting brain...")
             
            # Use Safe-Mode Defaults
            self.energy = 100 
            self.logs = []
            self.last_check = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.write_log("CRITICAL: JSON corruption detected. Memory was wiped.")
            self.chat_history = []
        # 4. Initialize the rest normally
       
           


    def show_menu(self):
        print(f"\n--- {self.name.upper()}'S WORLD ---")
        print("1: STATUS -------------")
        print(" 2: SYNC TEMP----------")
        print ("3: FEED---------------")
        print(" 4: WORK---------------")
        print(" 5: PLAY---------------")
        print(" 6: SLEEP--------------")
        print("7:MOOD-----------------")
        print("8:LOGS-----------------")
        print("nlp:CHAT---------")
        print("9:LET'S TALK ABOUT IT  ")

    def save_memory_made(self):
        if not os.path.exists("all_pandas"):
            os.makedirs("all_pandas")
        data = {
            "name": self.name,
            "energy": self.energy,
            "logs": self.logs,
            "video_history": self.video_history,
            "last_check": self.last_check,
            "user_profile":self.user_profile
        }
        with open(f"all_pandas/{self.name}.json", "w") as f:
            json.dump(data, f, indent=4)
    
    
    def write_log(self,message):
         
           try:
             time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
             try:
               cpu_val = self.new.vitals['cpu']
             except Exception:
                 cpu_val=0
             log_entry =f"[{time}] {message} / Energy : {self.energy} / CPU:{cpu_val['cpu']}%"
             self.logs.append(log_entry)
             if len(self.logs) > 20:
                self.logs.pop(0)
             self.save_memory_made()
        
           except Exception as e:
             pass
   
    def process_pandy_logic(user_input, chat_history=[]):
    # 1. Build a text block out of your conversation history
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
          final_prompt = f"{system_instruction}{history_context}New User Input: {user_input}"
    
          # 3. Call your Gemini API using this final_prompt instead of just user_input
          # response = model.generate_content(final_prompt)
          # return response.text
   
   
    def update_chat_history(self, user_message, ai_response):
        """Keeps a rolling log of the last 5 interactions to maintain context."""
    # Append the latest exchange as a structured dictionary
        self.chat_history.append({
             "user": user_message,
              "pandy": ai_response
             })
    
    # Sliding Window: If history exceeds 5 turns, drop the oldest memory
        if len(self.chat_history) > 5:
              self.chat_history.pop(0)


    def status(self):
        print(f"\n[STATUS] {self.name} | Energy: {self.energy}%")
        input("Press Enter...")

    def get_temp(self):
        url = "https://api.open-meteo.com/v1/forecast?latitude=27.7172&longitude=85.3240&current_weather=true"
        try:

            response = requests.get(url, timeout=5)
            data = response.json()
            # Fixed the dictionary access here
            temp = data["current_weather"]["temperature"]
            print(f"\n[WEATHER] Kathmandu is {temp}°C")
            result = random.randint(1, 100)
            if result <= 10:

                print("!!! POWER SURGE! Energy -20")

                self.energy -= 20

            elif result <= 20:

                print("!!! RAINBOW APPEARS! Energy +15")

                self.energy += 15

            else:

                print("Normal day. No energy surge.")

            # Keep energy between 0 and 100

            self.energy = max(0, min(100, self.energy))
            self.write_log("FETCHING TEMPERATURE!!")

             # Always save after a change!

            input("\nPress Enter...")

        except Exception as e:

            print(f"Error connecting to weather: {e}")
        input("Press Enter...")

    def feedpanda(self):
        self.energy = min(100, self.energy + 20)
        print("\n[FEED] Yum! +20 Energy.")
       
        self.write_log("EVENT: panda was fed a bamboo snak")
        input("Press Enter...")

    def manual_metabolism(self):
        self.energy = max(0, self.energy - 5)
        print("\n[WORK] Panda worked hard. -5 Energy.")
        self.write_log("MANUAL METABOLISM SCAN")
        input("Press Enter...")

    def play_game(self):
        result = random.randint(1, 100)
        print("THE NUMBERS ARE SCROLLING LOOK CLOSELY WHAT DAY YOUR MIGHT BE!!!")
        if result < 30:
            print("\n[JACKPOT] +90 Energy!")
            self.energy = min(100, self.energy + 90)
        else:
            print("OPPS YOU HAVE A BAD DAY TODAY")
            print("\n[PLAY] Fun times!")
        self.write_log("PLAY TIME!!!")
        input("Press Enter...")

    def sleep(self): # Fixed: Added 'self'
        
        # 1. Pull the actual live data from your neurons/vitals engine 
          data_payload = {
             "energy": self.energy,
             "mood": self.new.get_mood(),
              "last_check": self.last_check,
               "user_profile": self.user_profile,
        
        # 🔑 THE NEW LINE: Lock the chat history into your JSON file!
              "chat_history": self.chat_history
            }
    
    # 2. Hard-write that payload directly to your laptop's disk
          try:
             with open(self.save_path, "w") as file:
                 json.dump(data_payload, file, indent=4)
             print("💾 Reality Locked: Pandy's live state successfully saved to disk.")
             self.write_log("DATA SAVED SLEEP MODE!!!!")
          except Exception as e:
             print(f"⚠️ Serialization Failed: Could not write file. Error: {e}")
          
          
          print("🔌 Disconnecting from brain. Hard process termination. Goodbye!")
          os._exit(0)

    def apply_decay(self):
        now = datetime.datetime.now()
        last_time = datetime.datetime.strptime(self.last_check, "%Y-%m-%d %H:%M:%S")
        blocks = int((now - last_time).total_seconds() // 120)
        if blocks > 0:
            self.energy = max(0, self.energy - (blocks * 2))
            self.last_check = now.strftime(self.date_format)
        self.write_log("check for decay")
    
    def mood_now(self):
         mood=self.new.get_mood()
         print(f"PANDA IS IN {mood}  RIGHT NOW")
        
    def background_monitor(self):
        self.new.update_sensors()

    def check_hunger(self,data):
        # 1. Update the battery status
        batt_data = self.new.vitals.get('batt')
        is_plugged = self.new.vitals.get('charge', True) # Default to True if unknown
        
        # 2. If plugged in, Pandy is happy. Exit.
        if is_plugged:
            return 

        # 3. The Lockdown Loop
        if self.energy < 20:
            print(f"\n!!! LOW ENERGY ({self.energy}%) !!!")
            
            while True:  
                print(f"Pandy: I'm too weak! Type 'feed' or '3' to help!")
                user_input = input(f"[{self.name} > FEED]: ").lower().strip()

                # Check for BOTH 'feed' and '3'
                if user_input == "feed" or user_input == "3":
                    self.energy += 40 
                    if self.energy > 100: self.energy = 100
                    
                    print(f"Pandy: Om nom nom! Energy is now {self.energy}%.")
                    self.save_memory_made() 
                    break  # This exits the loop and goes back to the main menu
                else:
                    print("Pandy: No... I need bamboo (Type 'feed' or '3')...")
    def write_log(self,message):
           try:
             time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
             cpu_val = self.vitals.get('cpu', 0)
             log_entry =f"[{time}] {message} / Energy : {self.energy} / CPU:{cpu_val}%"
             self.logs.append(log_entry)
             if len(self.logs) > 20:
                self.logs.pop(0)
             self.save_memory_made()
             
        
           except Exception as e:
             pass
   
    def show_log(self):
        # In your main loop or a choice menu
    
        print(f"\n--- {self.name}'s Memory Logs ---")
        if not self.logs:
           print("No memories recorded yet.")
        else:
            for entry in self.logs:
               print(entry)
        input("\nPress Enter to go back...")

    def setup_wizard(self):
       print("\n--- PANDY INITIALIZATION ---")
    
    # 1. Validation Loop (Don't let them leave it blank)
       while True:
            name = input("I am Pandy. Who is my primary operator? ").strip()
            if name: # Checks if the string is not empty
                self.user_profile['name'] = name
                break
            print("⚠️ I need a name to initialize my core. Please try again.")

       print(f"\nNice to meet you, {self.user_profile['name']}.")
    
       # 2. Capture the Mission
       goal = input("What is our main objective for this 100-day sprint? ").strip()
       self.user_profile['goal'] = goal if goal else "General AI Development"

       # 3. Persistence & Logging to the update mode 
       try:
            self.write_log(f"System synced with {self.user_profile['name']}. Mission: {self.user_profile['goal']}")
            self.save_memory_made()
            print("\n[SUCCESS] Initialization complete. Let's get to work.")
       except Exception as e:
              print(f"⚠️ Error saving profile: {e}")

    def check_first_boot(self):
          # Check if the name is still the default
        if self.user_profile['name'] == "Unknown":
            self.setup_wizard()
            
        else:
           print(f"Welcome back, Agent {self.user_profile['name']}.")
   

    def hunger_check(self):
    # 'new' is your VitalsEngine instance
         if self.energy < 10:
               print(f"\n[SYSTEM]: Pandy is at {self.energy}% energy and is UNPLUGGED.")
               print("!!! LOCKDOWN ACTIVE: PANDY NEEDS BAMBOO !!!")
        
               while True:
               
                     user_input = input("Pandy [STREAVING] > ").lower().strip()
            
              # Use your keyword list
                     if any(word in user_input for word in ["feed", "eat", "3", "bamboo"]):
                # 1. Update the Vitals/Body state
                         self.energy = 100 
                
                # 2. Log the event
                         self.write_log("Emergency feeding completed.")
                
                # 3. SAVE to the JSON (Very important!)
                         self.save_memory_made()
                
                         print("Pandy: Om nom nom! System restored. You may proceed.")
                         break # This breaks the 'Wall' and lets the program continue
                     else:
                         print("Wall: Pandy is too weak to move. Feed him first!")
         else:
                 pass   



    def make(self):
            current_hardware_data=self.new.vitals
            current_mood= self.made.get_current_mood(current_hardware_data)
            if current_mood =="stressed":
                 print("[CRITICAL SYSTEM ERROR]: PANDY IS OVERHEATING!")
                 print("Fluff temp and CPU levels are too dangerous to continue.")
                 print("Shutting down the terminal application immediately...")
                 self.sleep();
                 log_msf=f"CRITICAL SHUTDOWN-CPU:{current_hardware_data['cpu']} // batt:{current_hardware_data['batt']}%"
                 self.write_log(log_msf);
                 
            else:
               pandy_msg=self.made.speak(current_mood)
               print(f"\n[Pandy]:{pandy_msg}")
          
load_dotenv()

base_dir = Path(__file__).resolve().parent
env_path = base_dir / ".env"

# Load the explicit path
load_dotenv(dotenv_path=env_path)

SECRET_API_KEY = os.getenv("GEMINI_API_KEY")

# 🚨 DIAGNOSTIC SAFETY CHECK (Prints right to your terminal log screen)
print("\n--- 🔑 STEALTH KEY VERIFICATION LAYER ---")
if SECRET_API_KEY:
    # Safely print just the first 4 characters to confirm it's loading, without exposing the secret!
    print(f"✅ Vault Status: ACTIVE. Key successfully loaded into RAM (Starts with: {SECRET_API_KEY[:4]}...)")
    genai.configure(api_key=SECRET_API_KEY)
else:
    print("❌ Vault Status: CRITICAL ERROR. The system returned 'None'. Python cannot find or read your .env file!")
    print(f"Target path checked was: {env_path}")
print("----------------------------------------\n")

class PandaBrain:
    
    def __init__(self):
        # 1. Securely grab the API key from your laptop's environment
        api_key = os.environ.get("GEMINI_API_KEY")
        
        # 🟢 FIX: Keep this safely set to None on boot to prevent server stalls
        self.engine = None 
        
        # 2. Initialize the Google AI configuration
        if api_key:
            genai.configure(api_key=api_key)
            # Using the fast, standard flash model
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.online_mode = True
        else:
            self.online_mode = False
    
    def update_telemetry(self, user_msg):
        """
        Analyzes the user's input sentence to dynamically adjust 
        Pandy's internal energy and mood metrics.
        """
        msg_lower = user_msg.lower()
        
        # 🧠 Context Trigger 1: Exam Stress / Heavy Work
        if any(word in msg_lower for word in ["exam", "study", "studying", "test", "deadline", "homework"]):
            self.energy = max(15, self.energy - 15)  # Drains energy
            self.mood = "Empathetic but Tired"
            
        # 🎋 Context Trigger 2: Food & Recharging
        elif any(word in msg_lower for word in ["bamboo", "eat", "food", "snack", "sleep", "nap"]):
            self.energy = min(100, self.energy + 25)  # Boosts energy
            self.mood = "Happy & Content"
            
        # ⚡ Context Trigger 3: High Energy Greetings
        elif any(word in msg_lower for word in ["hi", "hello", "hey", "let's go", "hype"]):
            self.energy = min(100, self.energy + 5)
            if self.energy > 75:
                self.mood = "Hyperactive"
            else:
                self.mood = "Chilled"

    def talk_to_pandy_web(self, user_msg, live_energy, live_mood, memo, prompt_modifier=None, **k):
        """
        Hardened Brain Engine: Computes real-time persistent telemetry updates
        and returns BOTH the text response and the updated metrics back to the UI state.
        """
        import os
        from pathlib import Path
        import google.generativeai as genai
        from dotenv import load_dotenv

        # 🎯 FORCE PATH RESOLUTION INSIDE THE RUNNING FUNCTION
        active_file_location = Path(__file__).resolve()
        target_env_path = active_file_location.parent / ".env"
        
        # Explicitly reload the environment variables right now
        load_dotenv(dotenv_path=target_env_path, override=True)
        SECRET_API_KEY = os.getenv("GEMINI_API_KEY")

        if not SECRET_API_KEY:
            return (
                f"❌ SYSTEM PATH MISMATCH ERROR\n\n"
                f"Streamlit is actively reading this specific file:\n`{active_file_location}`\n\n"
                f"It searched for your hidden `.env` file here:\n`{target_env_path}`\n\n"
                f"**Result:** File does not exist, is empty, or variable name is misspelled!"
            ), live_energy, live_mood

        # Apply configuration tokens to Google's servers
        genai.configure(api_key=SECRET_API_KEY)
    
        # 📊 DYNAMIC TELEMETRY CALCULATION (Using true current values)
        msg_lower = user_msg.lower()
    
        # Context Trigger 1: Heavy Exam Stress / Study Talk
        if any(word in msg_lower for word in ["exam", "study", "studying", "test", "deadline", "homework"]):
            st.session_state.energy= max(15, live_energy - 15)  # Drains energy
            st.session_state.mood = "Empathetic but Tired"
            
        # Context Trigger 2: Recharging & Rewards
        elif any(word in msg_lower for word in ["bamboo", "eat", "food", "snack", "sleep", "nap"]):
            st.session_state.energy = min(100, live_energy + 25)  # Boosts energy
            st.session_state.mood= "Happy & Content"
            
        # Context Trigger 3: Hype / Greetings
        elif any(word in msg_lower for word in ["hi", "hello", "hey", "let's go", "hype"]):
            st.session_state.energy = min(100, live_energy + 5)
            st.session_state.mood = "Hyperactive" if  st.session_state.energy  > 80 else "Chilled"

        # 🧠 BEHAVIORAL PROMPT TUNING (Using the newly shifted values)
        energy_rule = "Be conversational, friendly, and matching your normal chilled-out state."
        if  st.session_state.energy < 30:
            energy_rule = "CRITICAL: You are starving and exhausted. Keep your response very short, lazy, and mention needing a nap or bamboo."
        elif st.session_state.energy > 80:
            energy_rule = "CRITICAL: You are hyperactive and full of life! Be extremely witty, enthusiastic, and crack a joke."
        else:
            st.session_state.mood = "Chilled"
            energy_rule = "Be conversational, friendly, relaxed, and matching your normal chilled-out pet state."
        system_context = (
            f"You are an AI character engine representing a digital virtual panda pet.\n"
            f"Your CURRENT LIVE status metrics are EXACTLY:\n"
            f"- Mood: {st.session_state.mood}\n"
            f"- Energy: {st.session_state.energy}%\n"
            f"Behavioral Guideline: {energy_rule}\n"
            f"CRITICAL: Always stay completely in character. Do not mention being a language model."
        )

        system_instructions = f"You are Pandy, a helpful virtual companion. Current Energy: {  st.session_state.energy}%, Mood: {  st.session_state.mood}."
        if prompt_modifier:
            system_instructions += f"\n\n{prompt_modifier}"

        # 🎬 PIPELINE PIPING & EXECUTION
        if self.online_mode:
            try:
                # Filter out contaminated logs
                chat_history = [m for m in memo if m.get("role") in ["user", "assistant"] and m.get("content") is not None]
                if not chat_history:
                    chat_history = [{"role": "assistant", "content": "Hello!"}]
                
                def calculate_memory_weight(msg):
                    content = str(msg.get("content", "")).lower()
                    weight = len(content)
                    anchors = ["name", "remember", "project", "exam", "feel", "study", "tired", "deadline"]
                    if any(anchor in content for anchor in anchors):
                        weight += 200
                    return weight

                prioritized_logs = sorted(chat_history[:-1], key=calculate_memory_weight, reverse=True)
                core_anchors = prioritized_logs[:6]
                immediate_flow = chat_history[-3:] if len(chat_history) >= 3 else chat_history
                
                unique_memories = {}
                for m in (core_anchors + immediate_flow):
                    # If content is a list (e.g., streaming components), extract the first element or join it
                    raw_content = m.get("content", "")
                    if isinstance(raw_content, list):
                        string_key = " ".join([str(item) for item in raw_content])
                    else:
                        string_key = str(raw_content)
                    
                    unique_memories[string_key] = m

                active_memory_pool = list(unique_memories.values())
                active_memory_pool = sorted(active_memory_pool, key=lambda x: chat_history.index(x))
                transcript = ""
                for msg in active_memory_pool:
                    role_label = "User" if msg["role"] == "user" else "Model"
                    transcript += f"{role_label}: {msg['content']}\n"

                transcript += f"User: {user_msg}\nModel:"
                full_payload = f"System Context:\n{system_context}\n\nTelemetry Adjustments:\n{system_instructions}\n\nChat History Log:\n{transcript}"

                response = self.model.generate_content(full_payload)
                
                if response and hasattr(response, 'text') and response.text:
                    return response.text,   st.session_state.mood,st.session_state.energy
                
                return "🐼 *Pandy is connected, but the model returned an empty text payload.*",  st.session_state.energy,st.session_state.mood
            except Exception as e:
                return f"⚠️ Brain Engine Exception: {str(e)}",   st.session_state.energy,   st.session_state.mood
        
        return f"🐼 (Offline Mode): I received '{user_msg}'",   st.session_state.energy,   st.session_state.mood