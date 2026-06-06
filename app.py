import streamlit as st
from memory_service import MemoryService
from panda_brain_v1 import PandaBrain 

st.set_page_config(page_title="Pandy AI Dashboard", page_icon="🐼", layout="centered")

# Initialize and Cache our Service Modules safely
@st.cache_resource
def initialize_services():
    return MemoryService(), PandaBrain()

memory_manager, pandy_brain = initialize_services()

# Smoothly load persistent data into active frontend session memory
saved_data = memory_manager.load_memory()

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
    memory_manager.save_memory(st.session_state.energy, st.session_state.messages)