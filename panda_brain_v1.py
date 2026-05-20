import os
import json
import requests
import random
import datetime
from vitals_engine import VitalsEngine
from personality import PandyVoice

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
                self.user_profile=data.get('user_profile',[])
        except (json.JSONDecodeError, FileNotFoundError, ValueError):
            # 3. IF THE SHIELD TRIGGERS (File is missing, corrupted, or nonsense)
            print(f"\n[SYSTEM]: Memory corrupted or missing for {self.name}. Resetting brain...")
             
            # Use Safe-Mode Defaults
            self.energy = 100 
            self.logs = []
            self.last_check = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.write_log("CRITICAL: JSON corruption detected. Memory was wiped.")
            self.save_memory_made()
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
        print("nlp:LET'S CHAT---------")

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
             cpu_val = self.new.vitals['cpu']
             log_entry =f"[{time}] {message} / Energy : {self.energy} / CPU:{cpu_val['cpu']}%"
             self.logs.append(log_entry)
             if len(self.logs) > 20:
                self.logs.pop(0)
             self.save_memory_made()
        
           except Exception as e:
             pass
   


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
        self.energy = 100
        print("\n[SLEEP] Fully Restored!")
        self.write_log("SLEEP!!")
        input("Press Enter...")


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

       # 3. Persistence & Logging
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
          