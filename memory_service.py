import json
import os

class MemoryService:
    def __init__(self, file_path="pandy_memory.json"):
        self.file_path = file_path
        self.default_schema = {"energy": 100, "chat_history": []}

    def load_memory(self):
        """Safely reads and parses the local persistent storage layer."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # Fallback if file becomes corrupted or locked
                return self.default_schema
        return self.default_schema

    def save_memory(self, energy, messages):
        """Commits active runtime states back to the persistent JSON file."""
        try:
            payload = {
                "energy": energy,
                "chat_history": messages
            }
            with open(self.file_path, "w") as f:
                json.dump(payload, f, indent=4)
            return True
        except IOError as e:
            print(f"⚠️ Storage Write Error: {e}")
            return False