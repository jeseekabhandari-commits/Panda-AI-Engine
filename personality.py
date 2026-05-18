import random
from vitals_engine import VitalsEngine
class PandyVoice:
    def __init__(self):
        self.stri=VitalsEngine()
        self.phrases = {
            "energetic": [
                "Energy at 100%! I'm ready to move all day🐼🐼🐦!",
                "Energy levels are peak. What's our next big project?",
                "I'm feeling unstoppable! .",
                "Power plugged in. Pandy is in Turbo Mode! 🚀"
            ],
            "calm": [
                "Everything is smooth.🐦‍🔥🐦‍🔥",
                "Chilling in the background. Standing by..."
            ],
            "stressed": [
                "Too many tasks! My fluff is overheating🤒🤒!",
                "I need a second to breathe... CPU is heavy."
            ]
        }

    def speak(self, mood):
        # Pick a random phrase from the chosen mood
        options = self.phrases.get(mood,["Iam here"])
        return random.choice(options)
    
    
    def get_current_mood(self):
    # Ask Vitals for the data
      stats = self.stri.vitals 
    
    # Logic for "Full and Energetic"
      if stats['charge'] == True and stats['batt'] > 80:
          return "energetic"
      elif stats['cpu'] > 75:
        return 'stressed'
      else:
        return "calm"
      