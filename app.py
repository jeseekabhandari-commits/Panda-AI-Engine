import streamlit as st
import os
from panda_brain_v1 import PandaBrain 

st.set_page_config(page_title="Pandy AI Dashboard", page_icon="🐼", layout="centered")

# Initialize and Cache the Brain instance
@st.cache_resource
def load_cached_brain():
    return PandaBrain()

pandy_brain = load_cached_brain()

# Initialize standard session states for live metrics tracking
if "energy" not in st.session_state:
    st.session_state.energy = 85  # Starting default

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am Pandy. Let's talk!"}
    ]

# Dynamically compute mood state based on live web metrics (mirroring get_mood logic)
def calculate_live_mood(energy):
    if energy > 80:
        return "Energetic & Happy 🎋"
    elif energy > 40:
        return "Chilled Out 🐼"
    else:
        return "Tired & Grumpy 💤"

current_mood = calculate_live_mood(st.session_state.energy)

# --- SIDEBAR MONITORS ---
with st.sidebar:
    st.header("📊 Vitals Engine")
    st.metric(label="Energy Level", value=f"{st.session_state.energy}%")
    st.metric(label="Calculated Mood", value=current_mood)
    
    st.write("---")
    if st.button("🍲 Feed Bamboo (+15 Energy)", use_container_width=True):
        st.session_state.energy = min(100, st.session_state.energy + 15)
        st.rerun()
        
    if st.button("🏃 Exercise Routine (-20 Energy)", use_container_width=True):
        st.session_state.energy = max(0, st.session_state.energy - 20)
        st.rerun()

# --- MAIN INTERFACE ---
st.title("🐼 Pandy AI Character Console")
st.write("This dashboard passes true status metrics dynamically into Pandy's conversational layer.")
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
            # Pass metrics right into your prompt payload execution wrapper
            pandy_response = pandy_brain.talk_to_pandy_web(
                user_msg=user_input, 
                live_energy=st.session_state.energy, 
                live_mood=current_mood
            )
            st.write(pandy_response)
            
    st.session_state.messages.append({"role": "assistant", "content": pandy_response})