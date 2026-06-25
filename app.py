"""
Project Dashboard Engine
Phase 1 Production Build: Pandy Virtual Pet & AI Journaling Assistant
Compliance: PEP 8 Structural Standards & Phase 1 Performance Contracts
"""

import os
import json
import time
from datetime import datetime
import streamlit as st
from memory_service import MemoryService  # Adjust file name if different
from panda_brain_v1 import PandaBrain

# =====================================================================
# GLOBAL CONFIGURATION & PERFORMANCE SETTINGS
# =====================================================================
st.set_page_config(
    page_title="Project Dashboard Engine",
    page_icon="🚀",
    layout="wide"
)

DB_FILENAME = "journal_db.json"

# Fallback imports/initializations for background pet classes if not globally scoped
try:
    from journal_brain import JournalRouter
    router = JournalRouter(api_key="AIzaSyYourActualGeminiKeyWillGoHere")
except ImportError:
    pass

# =====================================================================
# PIPELINE SERVICE MODULES (BACKEND PIPELINES)
# =====================================================================
def load_database_records(filepath: str) -> list:
    """Reads, parses, and returns historical records from local JSON storage.
    Enforces robust error gates to handle missing or corrupted files defensively.

    Args:
        filepath (str): Target disk path to the system log storage file.

    Returns:
        list: Array of deserialized transactional logging dictionaries.
    """
    if not filepath or not isinstance(filepath, str):
        st.error("Engine Fault: Invalid or uninitialized database filepath string.")
        return []

    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as file_stream:
                return json.load(file_stream)
        except json.JSONDecodeError:
            st.error("⚠️ Storage Corrupted: `journal_db.json` contains malformed syntax. Resetting runtime view.")
            return []
        except PermissionError:
            st.error("⚠️ System Error: Insufficient disk read permissions for storage file.")
            return []
    return []

def save_database_record(filepath: str, payload: dict) -> bool:
    """Serializes and appends a fresh operational tracking frame to disk storage.
    Provides proactive mitigation against I/O exceptions and formatting errors.

    Args:
        filepath (str): Target disk path to the system log storage file.
        payload (dict): Structured transaction dictionary to write to disk.

    Returns:
        bool: True if transaction committed successfully, False otherwise.
    """
    if not payload or not isinstance(payload, dict):
        st.warning("Validation Skipped: Attempted to log an empty or invalid data payload structure.")
        return False

    try:
        history_log = load_database_records(filepath)
        history_log.append(payload)
        
        with open(filepath, "w", encoding="utf-8") as file_stream:
            json.dump(history_log, file_stream, indent=4)
        return True
    except (IOError, OSError) as write_error:
        st.error(f"⚠️ Critical Storage Write Failure: {write_error}")
        return False
    
def execute_offline_sentiment_pipeline(text: str) -> dict:
    """Applies a deterministic rule matrix to parse text strings for tone properties.

    Args:
        text (str): Raw string expression submitted from the frontend layer.

    Returns:
        dict: Target schema tracking indicators (score, mood, tag summary).
    """
    text_lower = text.lower()
    if any(keyword in text_lower for keyword in ["tired", "stress", "exhausted"]):
        return {"sentiment_score": 4, "dominant_mood": "Exhausted", "summary_tag": "Exam Fatigue"}
    elif any(keyword in text_lower for keyword in ["happy", "clear", "pass", "win"]):
        return {"sentiment_score": 9, "dominant_mood": "Accomplished", "summary_tag": "Major Win"}
    return {"sentiment_score": 7, "dominant_mood": "Balanced", "summary_tag": "Steady Progress"}

# ==========================================
# 🗺️ GLOBAL MULTI-APP NAVIGATION ROUTER
# ==========================================
st.sidebar.title("🚀 Project Dashboard")
active_app = st.sidebar.radio(
    "Select Application:",
    ["🐼 Pandy Virtual Pet", "📓 Personal AI Journal"]
)
st.sidebar.markdown("---")

# ==========================================
# 🐼 APP 1: PANDY VIRTUAL PET ROUTE
# ==========================================
if active_app == "🐼 Pandy Virtual Pet":
    st.title("Pandy Console")

    @st.cache_resource
    def initialize_services():
        return MemoryService(),PandaBrain()
        # Fallback mocks to prevent structural exceptions during runtime imports
        try:
            return MemoryService(), PandaBrain()
        except NameError:
            class MockService:
                def load_memory(self, name): return {"energy": 100, "chat_history": []}
                def save_memory(self, *args): pass
            class MockBrain:
                def talk_to_pandy_web(self, **k): return "Pandy Engine Online (Hardening Gate)."
            return MockService(), MockBrain()

    memory_manager, pandy_brain = initialize_services()

    if "active_panda" not in st.session_state:
        st.subheader("🐼 Panda AI Management Console")
        
        if not os.path.exists("all_pandas"): 
            os.makedirs("all_pandas")
        
        files = os.listdir("all_pandas")
        pandas = [f.removesuffix(".json").capitalize() for f in files if f.endswith(".json")]
    
        menu_options = pandas + ["✨ Create New Panda"]
        choice = st.selectbox("Select an option from the console:", menu_options)
    
        new_name = ""
        if choice == "✨ Create New Panda":
            new_name = st.text_input("Name your new virtual companion:")
            
        if st.button("Generate & Boot Profile", use_container_width=True):
            if new_name.strip() != "":
                st.session_state["active_panda"] = new_name.strip().lower()
                st.rerun()
            else:
                st.warning("Please type a valid character name string.")
        else:
            if choice != "✨ Create New Panda":
                st.info(f"Ready to mount memory context for: {choice}")
                if st.button(f"Boot {choice} Instance", use_container_width=True):
                    st.session_state["active_panda"] = choice.lower()
                    st.rerun()

    else:
        current_panda = st.session_state["active_panda"]
    
        if "loaded_panda" in st.session_state and st.session_state["loaded_panda"] != current_panda:
            if "energy" in st.session_state: del st.session_state["energy"]
            if "messages" in st.session_state: del st.session_state["messages"]
              
        st.session_state["loaded_panda"] = current_panda
        saved_data = memory_manager.load_memory(current_panda)
    
        if "energy" not in st.session_state:
            st.session_state.energy = saved_data.get("energy", 100)

        if "messages" not in st.session_state:
            st.session_state.messages = saved_data.get("chat_history", [])
            if not st.session_state.messages:
                st.session_state.messages = [{"role": "assistant", "content": f"Hello! I am {current_panda.capitalize()}."}]

        st.subheader(f"🐼 Managing Dashboard: {current_panda.capitalize()}")
        st.caption(f"Active Profile File Context: all_pandas/{current_panda}.json")

        def calculate_live_mood(energy):
            if energy > 80: return "Energetic & Happy 🎋"
            elif energy > 40: return "Chilled Out 🐼"
            else: return "Tired & Grumpy 💤"

        current_mood = calculate_live_mood(st.session_state.energy)
        is_full = st.session_state.energy >= 100
        is_exhausted = st.session_state.energy <= 0

        with st.sidebar:
            st.header("📊 Vitals Engine")
            st.metric(label="Energy Level", value=f"{st.session_state.energy}%")
            st.metric(label="Calculated Mood", value=current_mood)
          
            st.write("---")
            if st.button("🍲 Feed Bamboo (+15 Energy)", use_container_width=True, disabled=is_full):
                st.session_state.energy = min(100, st.session_state.energy + 15)
                memory_manager.save_memory(st.session_state["active_panda"], st.session_state.energy, st.session_state.messages)
                st.rerun()
           
            if st.button("🏃 Exercise Routine (-20 Energy)", use_container_width=True, disabled=is_exhausted):
                st.session_state.energy = max(0, st.session_state.energy - 20)
                memory_manager.save_memory(st.session_state["active_panda"], st.session_state.energy, st.session_state.messages)
                st.rerun()

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        user_input = st.chat_input(f"Talk to {current_panda.capitalize()}...")
      
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)
              
            with st.chat_message("assistant"):
                with st.spinner(f"{current_panda.capitalize()} is processing response..."):
                    pandy_response = pandy_brain.talk_to_pandy_web(
                        user_msg=user_input, 
                        live_energy=st.session_state.energy, 
                        live_mood=current_mood,
                        memo=st.session_state.messages
                    )
                    st.write(pandy_response)
                  
            st.session_state.messages.append({"role": "assistant", "content": pandy_response})
            memory_manager.save_memory(st.session_state["active_panda"], st.session_state.energy, st.session_state.messages)

# ==========================================
# 📓 APP 2: AI JOURNALING ASSISTANT ROUTE
# ==========================================
else:
    st.title("📓 Personal AI Journaling Assistant")
    st.subheader("Day 39: Exception Hardening & Validation Testing")

    if "journal_entries" not in st.session_state:
        st.session_state.journal_entries = []

    # --- WORKSPACE GRID ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📝 Write Today's Reflection")
        journal_input = st.text_area(
            "How was your day? Write down your raw thoughts, struggles, or wins:",
            height=200,
            placeholder="Type your entry here...",
            key="journal_text_box"
        )
        submit_entry = st.button("Analyze & Log Entry", type="primary")

    with col2:
        st.markdown("### 📊 Live Sentiment Analysis")
        
        if submit_entry and journal_input:
            with st.spinner("Processing local text matrices..."):
                time.sleep(0.1)  # Optimized latency interval
                
                # Execute decoupled processing modules
                analysis_data = execute_offline_sentiment_pipeline(journal_input)
                
                entry_payload = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "raw_text": journal_input,
                    "metrics": analysis_data
                }
                
                # Commit structural updates
                save_database_record(DB_FILENAME, entry_payload)
                st.toast("Data matrix logged!", icon="💾")
                
                # Render Design Variants
                score = analysis_data["sentiment_score"]
                if score >= 8:
                    st.success(f"Dominant Mood: {analysis_data['dominant_mood']}")
                    st.metric(label="Sentiment Score", value=f"{score}/10", delta="Excellent State")
                    st.balloons()
                elif score >= 6:
                    st.info(f"Dominant Mood: {analysis_data['dominant_mood']}")
                    st.metric(label="Sentiment Score", value=f"{score}/10", delta="Stable Matrix", delta_color="off")
                else:
                    st.error(f"Dominant Mood: {analysis_data['dominant_mood']}")
                    st.metric(label="Sentiment Score", value=f"{score}/10", delta="- Fatigue Alert", delta_color="inverse")
                    
                st.markdown(f"**Brief Index Summary:**")
                st.code(analysis_data['summary_tag'], language="text")
        else:
            st.info("Awaiting input transmission.")

    # --- TIMELINE & ANALYTICS SECTION ---
    st.markdown("---")
    st.markdown("### 📜 Past Reflections Timeline")
    
    saved_logs = load_database_records(DB_FILENAME)
    
    if saved_logs:
        total_entries = len(saved_logs)
        scores = [log.get("metrics", {}).get("sentiment_score", 7) for log in saved_logs]
        avg_score = sum(scores) / total_entries if total_entries > 0 else 0.0
        
        if avg_score >= 8.0: trend_emoji, trend_text = "🚀", "Thriving"
        elif avg_score >= 6.0: trend_emoji, trend_text = "⚖️", "Stable / Balanced"
        else: trend_emoji, trend_text = "📉", "Fatigued / Low Energy"

        stat_col1, stat_col2, stat_col3 = st.columns(3)
        with stat_col1:
            st.metric(label="Total Reflections Logged", value=f"{total_entries} Days")
        with stat_col2:
            st.metric(label="Lifetime Sentiment Avg", value=f"{avg_score:.1f} / 10")
        with stat_col3:
            st.markdown(f"**Current Status Trend:**")
            st.info(f"{trend_emoji} {trend_text}")
            
        st.markdown("#### Chronological Entries Feed")
        for log in reversed(saved_logs):
            ts = log.get("timestamp", "Unknown Time")
            mood = log.get("metrics", {}).get("dominant_mood", "Balanced")
            score = log.get("metrics", {}).get("sentiment_score", 7)
            tag = log.get("metrics", {}).get("summary_tag", "Progress")
            text = log.get("raw_text", "")
            
            with st.expander(f"📅 {ts} | Mood: {mood} ({score}/10)"):
                st.markdown(f"**Short Tag:** `{tag}`")
                st.info(text)
    else:
        st.warning("Database file empty or uninitialized.")