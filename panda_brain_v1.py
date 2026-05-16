import os
import json
import requests
import random
import datetime
import psutil


class PandaCharacter:
    
    def __init__(self, name, energy=0, logs=None, video_history=None, last_check=None):
       # 1. Define the basics first
        self.name = name
        self.save_path = f"all_pandas/{self.name}.json"
        
        # 2. Try to LOAD from the file
        try:
            with open(self.save_path, 'r') as f:
                data = json.load(f)
                # If we get here, the file is GOOD. Use the data!
                self.energy = data.get('energy', 100)
                self.logs = data.get('logs', [])
                self.last_check = data.get('last_check', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
               
        except (json.JSONDecodeError, FileNotFoundError, ValueError):
            # 3. IF THE SHIELD TRIGGERS (File is missing, corrupted, or nonsense)
            print(f"\n[SYSTEM]: Memory corrupted or missing for {self.name}. Resetting brain...")
             
            # Use Safe-Mode Defaults
            self.energy = 100 
            self.logs = []
            self.last_check = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.write_log("CRITICAL: JSON corruption detected. Memory was wiped.")
        # 4. Initialize the rest normally
        self.vitals = {"cpu": 0, "ram": 0, "batt": 0, "temps": 0, "charge": 0}
        self.video_history = []
        self.vitals={"cpu":0,"ram":0,"batt":0,"temps":0,"charge":0}
        self.date_format="%Y-%m-%d %H:%M:%S"
        
           


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

    def save_memory_made(self):
        if not os.path.exists("all_pandas"):
            os.makedirs("all_pandas")
        data = {
            "name": self.name,
            "energy": self.energy,
            "logs": self.logs,
            "video_history": self.video_history,
            "last_check": self.last_check
        }
        with open(f"all_pandas/{self.name}.json", "w") as f:
            json.dump(data, f, indent=4)

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
         cpu_val = self.vitals.get('cpu', 0) # Use .get to avoid "KeyError"
         print(f"Your CPU status is {cpu_val}%")
         if cpu_val > 70:
           print("PANDA IS IN STRESS RIGHT NOW")
         else:
           print("PANDA IS IN A GOOD MOOD!!!!")

    def background_monitor(self):
        try:
            self.vitals["cpu"] = psutil.cpu_percent()
            self.vitals["ram"] = psutil.virtual_memory().percent
            batt = psutil.sensors_battery()
            if batt:
                self.vitals["batt"] = batt.percent
                self.vitals["charge"] = batt.power_plugged
            else:
                self.vitals["batt"]=100
                self.vitals["charge"] = True # Default for desktops
        except Exception as e:
           print(f"⚠️ Sensor Warning: Entering Safe Mode! (Error: {e})")
        if self.vitals["batt"] < 15:
            self.write_log("BATTERY CRITICALLY LOW!!")
   
    def check_hunger(self):
        # 1. Update the battery status
        batt_data = self.vitals.get('batt')
        is_plugged = self.vitals.get('charge', True) # Default to True if unknown

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
           time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
           log_entry =f"[{time}] {message} / Energy : {self.energy} / CPU:{self.vitals['cpu']}%"
           self.logs.append(log_entry)
           if len(self.logs) > 20:
               self.logs.pop(0)
           self.save_memory_made()
    def show_log(self):
        # In your main loop or a choice menu
    
        print(f"\n--- {self.name}'s Memory Logs ---")
        if not self.logs:
           print("No memories recorded yet.")
        else:
            for entry in self.logs:
               print(entry)
        input("\nPress Enter to go back...")