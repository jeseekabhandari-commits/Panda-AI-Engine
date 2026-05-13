import json
import os
import datetime

panda_data = {

    "name": "panda",

    "energy": 70,

    "video_history": []

}
def save_memory(data: dict, filepath: str = "memory.json") -> None:

    """Serialise *data* to *filepath* as formatted JSON."""

    try:
        with open(filepath, "w", encoding="utf-8") as f:

            json.dump(data, f, indent=4)

        print(f"[save] Memory written to '{filepath}'.")

    except IOError as e:

        print(f"[error] Could not write to file: {e}")

def load_memory(filepath: str = "memory.json") -> dict:

    """ Try to read *filepath*.

    - Found → parse and return it.

    - Missing or Corrupt → return default and save it. """

    default = {

        "name": "Unknown Panda",

        "energy": 50,

        "video_history": []

    }
    if not os.path.exists(filepath):

        print(f"[load] '{filepath}' not found — creating default memory.")

        save_memory(default, filepath)

        return default

    try:

        with open(filepath, "r", encoding="utf-8") as f:

            return json.load(f)

    except (json.JSONDecodeError, ValueError):

        print(f"[error] '{filepath}' is corrupted. Resetting to default.")

        save_memory(default, filepath)

        return default

if __name__ == "__main__":

    save_memory(panda_data)
    loaded = load_memory()
    loaded["video_history"].append("Panda eats bamboo.mp4")

    save_memory(loaded)
    print("Final Video History:", load_memory()["video_history"])

import os
import datetime
import panda_brain_v1

def show_menu(energy):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("---------------------------")
    print(f" PANDA ENGINE | ENERGY: {energy}%")
    print("---------------------------")
    print("1. Status Report")
    print("2. Sync Weather (Luck Roll)")
    print("3. Feed Panda (+20)")
    print("4. Manual Metabolism (-2)")
    print("5. Exit")
    print("---------------------------")

def main():
    # 1. Load memory and ensure we have a timestamp
    memory = panda_brain_v1.load_memory()
    if "last_check" not in memory:
        memory["last_check"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    while True:
        # A. Calculate Time Decay automatically every loop
        lost_energy, new_time_str = panda_brain_v1.calculate_decay(memory["last_check"])
        if lost_energy > 0:
            memory["energy"] = max(0, memory["energy"] - lost_energy)
            memory["last_check"] = new_time_str
            print(f"\n[TIME] {lost_energy} energy lost while you were away.")

        show_menu(memory["energy"])
        choice = input("Select: ").strip()

        if choice == "1":
            print(f"\n[STATUS] Name: {memory['name']} | Energy: {memory['energy']}")
            print(f"Last Sync: {memory['last_check']}")
            input("\nPress Enter...")

        elif choice == "2":
            temp = panda_brain_v1.get_temp()
            print(f"\n[WEATHER] Kathmandu is {temp}°C")
            memory["energy"] = panda_brain_v1.calculate_weather_luck(memory["energy"])
            panda_brain_v1.save_memory(memory)
            input("\nPress Enter...")

        elif choice == "3":
            memory["energy"] = min(100, memory["energy"] + 20)
            print("\n[FEED] +20 Energy!")
            panda_brain_v1.save_memory(memory)
            input("\nPress Enter...")

        elif choice == "4":
            memory["energy"] = max(0, memory["energy"] - 2)
            print("\n[WORK] Panda used 2 energy.")
            input("\nPress Enter...")

        elif choice == "5":
            panda_brain_v1.save_memory(memory)
            print("Memory Saved. Goodbye!")
            break

if __name__ == "__main__":
    main()