🐼 Panda-AI-Engine
An AI-driven character management system built with Python.

Overview
This project is part of a 100-Day AI Product Engineering Sprint. It is a state-managed engine that simulates an AI character named "Pandy." The engine uses Object-Oriented Programming (OOP) to manage multiple character instances, each with its own persistent memory and metabolism logic.

Key Features
1)Dynamic Character Management: Automatically detects and loads character profiles from local JSON storage.

2)Encapsulated Logic: A central PandaCharacter class handles all state updates, saving/loading, and behavior.

3)Real-time Environment: Integrates with the Open-Meteo API to fetch live weather data for Kathmandu, which influences the panda's energy levels.

4)State Decay System: Implements a time-based metabolism where energy levels drop based on the actual time passed since the last       interaction.

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

      Sprint Update: Emotional State Integration
 
Today’s update adds a layer of "Personality" to the system by linking hardware vitals to response strings.

Technical Details:

Module: Added personality.py containing the PandyVoice class🐼🐼.

Data Flow: Refactored the Brain to request a mood_label (String) from the Body, which is then used as a key in the PandyVoice dictionary to return a randomized response.

Fix: Resolved TypeError: unhashable type: 'list' by ensuring the system passes immutable strings for dictionary lookups rather than mutable lists of phrases.

Efficiency: Optimized conditional checks using Pythonic boolean evaluation (e.g., if stats['charge']:).
        
        
           Structural Guardrails & Architectural Review🐼🐼
Shifted focus to system stability, defensive programming, and verifying internal data flow patterns.

1)Autonomous Interception: Implemented a system-wide freeze within the .make() engine method to intercept user inputs if state evaluates to "stressed".

2)Diagnostic Logging: Upgraded the logging system to capture a structured payload format (f"CRITICAL SHUTDOWN - CPU: {cpu}% | Batt: {batt}%") on failure points instead of loose text strings.

3)Code Review: Audited decoupled communication between personality.py and the main orchestration loop to enforce immutable data hand-offs.


  🛡️ Configuration & Runtime Security Layer

The engine utilizes an isolated environment configuration architecture to separate core application logic from sensitive runtime variables (such as third-party AI platform credentials).

### System Flow Diagram
 🧠 Core Engine Brain Integration (Day 17)

Migrated the natural language pipeline from basic conditional routing to a modular, object-oriented Class structure.

  Architecture Update
* Encapsulated Subsystems: Isolated all conversational API interfaces into a dedicated `PandaBrain` class within `panda_brain_v1.py`.
* Centralized Session Handling: Implemented an internal `handle_chat_session()` router to handle I/O data pipelines directly inside the class, reducing main controller (`product_manager.py`) overhead down to a single method invocation.
 Intent Engine Mapping: Integrated the brain seamlessly with the pre-existing `TextBlob` semantic intent filter layer.
 ## 🌐 Live AI Cloud Integration 

Successfully transitioned the `PandaBrain` subsystem from an offline fallback state to a live, production-ready cloud networking architecture.

### Implementation Highlights
* **Secure Environment Architecture:** Integrated OS-level environment variable fetching via `os.environ.get()` to prevent critical API credential leaks.
**Live Network Handshake:** Established an active pipeline utilizing `google-generativeai` to transmit user conversational payloads over HTTPS.
 **Dynamic Exception Handling:** Engineered a robust `try/except` lifecycle fallback network layer to instantly revert to offline mode if server timeouts or 404 errors occur.