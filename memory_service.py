import json
import os

class MemoryService:
    def __init__(self):
           
        self.default_schema = {"energy": 100, "chat_history": []}

    def load_memory(self,panda_name):
        """Safely reads and parses the local persistent storage layer."""
        target_path = f"all_pandas/{panda_name}.json"
        if os.path.exists(target_path):
            try:
                with open(target_path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # Fallback if file becomes corrupted or locked
                return self.default_schema
        return self.default_schema

    def save_memory(self,panda_name, energy, messages):
         """Commits active runtime states back to the persistent JSON file."""
         target_path = f"all_pandas/{panda_name}.json"
         try:
            payload = {
                "energy": energy,
                "chat_history": messages
            }
            with open(target_path, "w") as f:
                json.dump(payload, f, indent=4)
            return True
         except IOError as e:
             print(f"⚠️ Storage Write Error: {e}")
             return False