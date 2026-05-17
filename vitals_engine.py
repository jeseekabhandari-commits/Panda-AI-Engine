import psutil

class VitalsEngine:
    def __init__(self):
        self.vitals = {"cpu": 0, "ram": 0, "batt": 0, "charge": True}
        self.energy = 100 # Moved from Brain to Body/Vitals

    def update_sensors(self):
        """Updates internal dictionary with latest hardware data."""
        try:
            self.vitals["cpu"] = psutil.cpu_percent()
            self.vitals["ram"] = psutil.virtual_memory().percent
            batt = psutil.sensors_battery()
            if batt:
                self.vitals["batt"] = batt.percent
                self.vitals["charge"] = batt.power_plugged
        except Exception as e:
            print(f"⚠️ Sensor Error: {e}")
        if self.vitals["batt"] < 15:
            self.write_log("BATTERY CRITICALLY LOW!!")
            
    def get_mood(self):
        cpu = self.vitals["cpu"]
        if cpu > 70: return "STRESSED"
        return "CALM"

    def needs_food(self):
        """Just returns True/False. Let the Brain/Body handle the loop."""
        return self.energy < 20 and not self.vitals["charge"]