import streamlit as st
import os  # Crucial for scanning your directory!
from memory_service import MemoryService
from panda_brain_v1 import PandaBrain 

st.set_page_config(page_title="Panda Console", page_icon="🐼", layout="centered")

# Initialize your background service engines
@st.cache_resource
def initialize_services():
    return MemoryService(), PandaBrain()

memory_manager, pandy_brain = initialize_services()

# =========================================================
# STEP 1: THE INITIALIZATION GATEKEEPER
# =========================================================
if "active_panda" not in st.session_state:
    st.title("🐼 Panda AI Management Console")
    st.write("---")
    
    # YOUR TERMINAL LOGIC ARCHITECTURE: Ensure folder exists and scan it live
    if not os.path.exists("all_pandas"): 
        os.makedirs("all_pandas")
        
    files = os.listdir("all_pandas")
    # Clean suffix extension mapper
    pandas = [f.removesuffix(".json").capitalize() for f in files if f.endswith(".json")]
    
    # Dropdown menu containing existing files + creation action switch
    menu_options = pandas + ["✨ Create New Panda"]
    choice = st.selectbox("Select an option from the console:", menu_options)
    
    # Branch A: Handle Creation Action Switch
    if choice == "✨ Create New Panda":
        new_name = st.text_input("Name your new virtual companion:")
        
        if st.button("Generate & Boot Profile", use_container_width=True):
            if new_name.strip() != "":
                st.session_state["active_panda"] = new_name.strip().lower()
                st.rerun()
            else:
                st.warning("Please type a valid character name string.")
                
    # Branch B: Handle Booting an Existing Checked Profile
    else:
        st.info(f"Ready to mount memory context for: {choice}")
        if st.button(f"Boot {choice} Instance", use_container_width=True):
            st.session_state["active_panda"] = choice.lower()
            st.rerun()

# =========================================================
# STEP 2: THE REAL DASHBOARD ROAD (THE MAIN ELSE BLOCK)
# =========================================================
else:
    # 1. Grab the active character string locked from Step 1
    current_panda = st.session_state["active_panda"]
    
    # 2. Query your dynamic memory service passing the chosen profile target
    saved_data = memory_manager.load_memory(current_panda)
    
    # 3. Synchronize your runtime session registers directly with real file states
    if "energy" not in st.session_state:
        st.session_state.energy = saved_data.get("energy",100)

    if "messages" not in st.session_state:
        st.session_state.messages = saved_data.get("chat_history",[])
        if not st.session_state.messages:
            st.session_state.messages = [{"role": "assistant", "content": f"Hello! I am {current_panda.capitalize()}."}]

    # -----------------------------------------------------
    # PASTE YOUR INDENTED DASHBOARD FURNITURE BELOW HERE!
    # -----------------------------------------------------
    st.title(f"🐼 Managing Dashboard: {current_panda.capitalize()}")
    

    

    st.write(f"Active Profile File Context: all_pandas/{current_panda}.json")
    
    # (Put your sidebar code, chat render loop, and chat_input code right here)

   # Smoothly load persistent data into active frontend session memory

 
    if "energy" not in st.session_state:
       st.session_state.energy = saved_data["energy"]

    if "messages" not in st.session_state:
       st.session_state.messages = saved_data["chat_history"]
    if not st.session_state.messages:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I am Pandy. Let's talk!"}]

# Dynamic Mood Engine
    def calculate_live_mood(energy):
        if energy > 80: return "Energetic & Happy 🎋"
        elif energy > 40: return "Chilled Out 🐼"
        else: return "Tired & Grumpy 💤"

    current_mood = calculate_live_mood(st.session_state.energy)
    is_full = st.session_state.energy >= 100
    is_exhausted = st.session_state.energy <= 0
# --- SIDEBAR MONITORS ---
    with st.sidebar:
       st.header("📊 Vitals Engine")
       st.metric(label="Energy Level", value=f"{st.session_state.energy}%")
       st.metric(label="Calculated Mood", value=current_mood)
    
       st.write("---")
       if st.button("🍲 Feed Bamboo (+15 Energy)", use_container_width=True,disabled=is_full):
           st.session_state.energy = min(100, st.session_state.energy + 15)
           memory_manager.save_memory(st.session_state.energy, st.session_state.messages)
           st.rerun()
        
       if st.button("🏃 Exercise Routine (-20 Energy)", use_container_width=True,disabled=is_exhausted):
          st.session_state.energy = max(0, st.session_state.energy - 20)
          memory_manager.save_memory(st.session_state.energy, st.session_state.messages)
          st.rerun()
   

    
# --- MAIN INTERFACE ---
       st.title("🐼 Pandy AI Character Console")
       st.write("---")

# Render active chat stream
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
           st.write(msg["content"])

   # User Chat Input Pipeline
    user_input = st.chat_input("Talk to Pandy...")
    if user_input:
    # 1. Append and render user statement
        st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
        
    # 2. Query anchored AI engine
    with st.chat_message("assistant"):
        with st.spinner("Pandy is processing response..."):
            pandy_response = pandy_brain.talk_to_pandy_web(
                user_msg=user_input, 
                live_energy=st.session_state.energy, 
                live_mood=current_mood
            )
            st.write(pandy_response)
            
    # 3. Save updated timeline smoothly via our decoupled service layer
    st.session_state.messages.append({"role": "assistant", "content": pandy_response})
    memory_manager.save_memory(st.session_state["active_panda"],st.session_state.energy, st.session_state.messages)