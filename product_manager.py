import panda_brain_v1
from  panda_brain_v1 import PandaCharacter
import os
import json

def play_with_panda(active_panda):
    # --- STEP 1: DECAY CHECK ---
    # This runs once when you enter the room
    active_panda.apply_decay() 

    while True:
        # --- STEP 2: REFRESH MENU ---
        # We show the options every time a loop finishes
        active_panda.show_menu() 
        
        # --- STEP 3: THE HUNGER BLOCKADE ---
        if active_panda.energy == 0:
            print("\n!!! ENERGY IS 0. ONLY FEEDING IS ALLOWED !!!")
            choice = input("Your only choice is (3) to Feed: ")
            if choice == "3":
                active_panda.feedpanda()
            elif choice == "5": # Let them exit even if hungry
                break
            continue # Go back to top of loop

        # --- STEP 4: NORMAL MENU CHOICES ---
        choice = input("Command -> ")

        if choice == "1":
            active_panda.status()
        elif choice == "2":
            active_panda.get_temp()
        elif choice == "3":
            active_panda.feedpanda()
        elif choice == "4":
            active_panda.manual_metabolism()
        elif choice == active_panda.exist_key:
            active_panda.save_memory_made() # Final save before leaving
            print("Returning to Lobby...")
            break 
        else:
            print("Invalid choice!")

def main_lobby():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=== WELCOME TO PANDA ENGINE ===")
        
        # 1. Scan for existing pandas
        if not os.path.exists("all_pandas"):
            os.makedirs("all_pandas")
            
        files = os.listdir("all_pandas")
        pandas = [f.removesuffix(".json") for f in files if f.endswith(".json")]

        # 2. Display the Dynamic Menu
        for i, name in enumerate(pandas, 1):
            print(f"{i}. {name}")
        
        new_panda_option = len(pandas) + 1
        print(f"{new_panda_option}. Create New Panda")
        print("0. Exit Game")

        choice = input("\nSelect an option: ")

        # 3. Handle the choice
        if choice == "0":
            break
        
        # CHOICE: Pick existing Panda
        elif choice.isdigit() and 1 <= int(choice) <= len(pandas):
            selected_name = pandas[int(choice) - 1]
            
            # Load the data from the file
            with open(f"all_pandas/{selected_name}.json", "r") as f:
                data = json.load(f)
            
            # Create the object with saved data
            active_panda = PandaCharacter(
                name=data["name"], 
                energy=data["energy"], 
                logs=data["logs"], 
                last_check=data.get("last_check") # get() prevents crashing if missing
            )
            play_with_panda(active_panda)

        # CHOICE: Create New Panda
        elif choice == str(new_panda_option):
            name = input("Enter Panda Name: ")
            # Start fresh with 0 energy
            active_panda = PandaCharacter(name, energy=0)
            active_panda.save_memory_made()
            play_with_panda(active_panda)



if __name__ == "__main__":
    main_lobby()
