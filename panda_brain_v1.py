
import os
import json
import requests
import random
import datetime

class PandaCharacter:
    def __init__(self, name, energy=0, logs=None, video_history=None, last_check=None):
        self.name = name
        self.energy = energy
        self.logs = logs if logs else []
        self.video_history = video_history if video_history else []
        self.exist_key = "5"
        self.date_format = "%Y-%m-%d %H:%M:%S"

        # If no time is provided, set it to "Right Now"
        self.last_check = last_check if last_check else datetime.datetime.now().strftime(self.date_format)
    def show_menu(self):
        print("----------------------------------------------------")
        print("  WELCOME  TO THE PANDA WORLD !!!!!  ")
        print("---1:STATUS---------------")
        print("---2:SYNC_TEMPERATURE-----")
        print("---3:FEED PANDA-----------")
        print("---4:MANUAL METABOLISM----")
        print("---5:EXIT-----------------")
        

    def save_memory_made(self):
        if not os.path.exists("all_pandas"):
            os.makedirs("all_pandas")
            
        data = {
            "name": self.name,
            "energy": self.energy,
            "logs": self.logs,
            "video_history": self.video_history,
            "last_check": self.last_check  # Save the time!
        }

        filepath = f"all_pandas/{self.name}.json"
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        print(f"--- {self.name}'s memory saved! ---")

    def status(self):
        print(f"\n[STATUS] Name: {self.name} | Energy: {self.energy}")
        print(f"Last Sync: {self.last_check}")
        if self.energy == 0:
            print("!!! ENERGY IS LOW! FEED ME NOW !!!")
        input("\nPress Enter...")

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
            self.save_memory_made() # Always save after a change!
            input("\nPress Enter...")
        except Exception as e:
            print(f"Error connecting to weather: {e}")

    def feedpanda(self):
        self.energy = min(100, self.energy + 20)
        print("\n[FEED] +20 Energy!")
        self.save_memory_made()      
        input("\nPress Enter...")

    def manual_metabolism(self):
        self.energy = max(0, self.energy - 2)
        print("\n[WORK] Panda used 2 energy.")
        self.save_memory_made()
        input("\nPress Enter...")

    def apply_decay(self):
         now = datetime.datetime.now()
         last_time = datetime.datetime.strptime(self.last_check,self.date_format)
    
         seconds_passed = (now - last_time).total_seconds()
         blocks = int(seconds_passed // 120)
    
         if blocks > 0:
            self.energy = max(0, self.energy - (blocks * 2))
            self.last_check = now.strftime(self.date_format)
            self.save_memory_made() # Save the new lower energy immediately
         if self.energy == 0:
             print("ENERGY IS LOW FEED ME!!!!!")