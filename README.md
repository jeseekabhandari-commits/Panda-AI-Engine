🐼 Panda-AI-Engine
An AI-driven character management system built with Python.

Overview
This project is part of a 100-Day AI Product Engineering Sprint. It is a state-managed engine that simulates an AI character named "Pandy." The engine uses Object-Oriented Programming (OOP) to manage multiple character instances, each with its own persistent memory and metabolism logic.

Key Features
Dynamic Character Management: Automatically detects and loads character profiles from local JSON storage.

Encapsulated Logic: A central PandaCharacter class handles all state updates, saving/loading, and behavior.

Real-time Environment: Integrates with the Open-Meteo API to fetch live weather data for Kathmandu, which influences the panda's energy levels.

State Decay System: Implements a time-based metabolism where energy levels drop based on the actual time passed since the last interaction.

Tech Stack
Language: Python

Data Persistence: JSON

APIs: Open-Meteo (Weather)

Version Control: Git/GitHub

How to Run

1:Clone the repository.

2:Ensure you have the requests library installed: pip install requests.

3:Run python product_manager.py to start the engine.

System Modularization

The engine has been refactored for better scalability and security.

New Module: vitals.py now encapsulates all psutil dependencies, shielding the main brain from low-level hardware calls.

Logic Decoupling: The PandaCharacter now "owns" a VitalsEngine instance, demonstrating a cleaner Class-based architecture.

Hardware-Driven UX: Added a blocking hunger_check loop that prevents system execution during low-power states until the "Feed" (NLP/Command) intent is satisfied.

Robustness: Implemented try-except blocks across sensor readings to ensure a "Safe Mode" fallback if hardware data is unavailable.