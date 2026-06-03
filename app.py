import streamlit as st
import json
import os
from panda_brain_v1 import PandaBrain 

st.set_page_config(page_title="Pandy AI Dashboard", page_icon="🐼", layout="centered")

MEMORY_FILE = "pandy_memory.json"

# --- HELPER FUNCTIONS FOR PERMANENT STORAGE ---
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"energy": 100, "chat_history": []}

def save_memory(energy, messages):
    with open(MEMORY_FILE, "w") as f:
        json.dump({"energy": energy, "chat_history": messages}, f, indent=4)

# Load saved stats right into Session State
saved_data = load_memory()
if "energy" not in st.session_state:
    st.session_state.energy = saved_data["energy"]
if "messages" not in st.session_state:
    st.session_state.messages = saved_data["chat_history"]
    if not st.session_state.messages:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I am Pandy. Let's talk!"}]

@st.cache_resource
def load_cached_brain():
    return PandaBrain()

pandy_brain = load_cached_brain()

# Dynamically compute mood state
def calculate_live_mood(energy):
    if energy > 80: return "Energetic & Happy 🎋"
    elif energy > 40: return "Chilled Out 🐼"
    else: return "Tired & Grumpy 💤"

current_mood = calculate_live_mood(st.session_state.energy)

# --- SIDEBAR MONITORS ---
with st.sidebar:
    st.header("📊 Vitals Engine")
    st.metric(label="Energy Level", value=f"{st.session_state.energy}%")
    st.metric(label="Calculated Mood", value=current_mood)
    
    st.write("---")
    if st.button("🍲 Feed Bamboo (+15 Energy)", use_container_width=True):
        st.session_state.energy = min(100, st.session_state.energy + 15)
        save_memory(st.session_state.energy, st.session_state.messages)
        st.rerun()
        
    if st.button("🏃 Exercise Routine (-20 Energy)", use_container_width=True):
        st.session_state.energy = max(0, st.session_state.energy - 20)
        save_memory(st.session_state.energy, st.session_state.messages)
        st.rerun()

# --- MAIN INTERFACE ---
st.title("🐼 Pandy AI Character Console")
st.write("---")

# Render active chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User Chat Action Processing
user_input = st.chat_input("Talk to Pandy...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
        
    with st.chat_message("assistant"):
        with st.spinner("Pandy is processing response..."):
            pandy_response = pandy_brain.talk_to_pandy_web(
                user_msg=user_input, 
                live_energy=st.session_state.energy, 
                live_mood=current_mood
            )
            st.write(pandy_response)
            
    st.session_state.messages.append({"role": "assistant", "content": pandy_response})
    # Save everything instantly to the hard drive
    save_memory(st.session_state.energy, st.session_state.messages)