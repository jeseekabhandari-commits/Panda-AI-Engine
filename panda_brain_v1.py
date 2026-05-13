import json
import requests
import os
import random
import datetime

# --- STORAGE TOOLS ---
def load_memory():
    if os.path.exists("memory.json"):
        with open("memory.json", "r") as f:
            return json.load(f)
    return {"name": "Panda", "energy": 100, "video_history": []}

def save_memory(data):
    with open("memory.json", "w") as f:
        json.dump(data, f, indent=4)

# --- WEATHER TOOLS ---
def get_temp():
    url = "https://api.open-meteo.com/v1/forecast?latitude=27.7172&longitude=85.3240&current_weather=true"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        return data["current_weather"]["temperature"]
    except:
        return 20.0 # Fallback

def calculate_weather_luck(current_energy):
    """Returns the NEW energy value based on luck"""
    result = random.randint(1, 100)
    new_energy = current_energy
    
    if result <= 10:
        print("!!! POWER SURGE! Energy -20")
        new_energy -= 20
    elif result <= 20:
        print("!!! RAINBOW APPEARS! Energy +15")
        new_energy += 15
    else:
        print("Normal day. No energy surge.")
        
    return max(0, min(100, new_energy))

# --- TIME CALCULATION (No more while loop!) ---
def calculate_decay(last_time_str):
    """Calculates how many 2-minute blocks passed since last_time_str"""
    now = datetime.datetime.now()
    last_time = datetime.datetime.strptime(last_time_str, "%Y-%m-%d %H:%M:%S")
    
    seconds_passed = (now - last_time).total_seconds()
    blocks = int(seconds_passed // 120) # 120 seconds = 2 mins
    
    return blocks * 2, now.strftime("%Y-%m-%d %H:%M:%S")
