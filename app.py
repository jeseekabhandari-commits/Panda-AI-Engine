import streamlit as st
import os  # Crucial for scanning your directory!
from memory_service import MemoryService
from panda_brain_v1 import PandaBrain 
from journal_brain import JournalRouter
router = JournalRouter(api_key="AIzaSyYourActualGeminiKeyWillGoHere")

# Initialize global layout settings
st.set_page_config(page_title="AI Engineering Hub", layout="wide")

# ==========================================
# 🗺️ GLOBAL MULTI-APP NAVIGATION ROUTER
# ==========================================
st.sidebar.title("🚀 Project Dashboard")
active_app = st.sidebar.radio(
    "Select Application:",
    ["🐼 Pandy Virtual Pet", "📓 Personal AI Journal"]
)

st.sidebar.markdown("---") # Visual break before app-specific sidebars

# ==========================================
# 🐼 APP 1: PANDY VIRTUAL PET ROUTE
# ==========================================
if active_app == "🐼 Pandy Virtual Pet":
    st.title("Pandy Console")
    st.set_page_config(page_title="Panda Console", page_icon="🐼", layout="centered")

   #   Initialize your background service engines
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
    
       if not os.path.exists("all_pandas"): 
        os.makedirs("all_pandas")
        
       files = os.listdir("all_pandas")
       pandas = [f.removesuffix(".json").capitalize() for f in files if f.endswith(".json")]
    
       menu_options = pandas + ["✨ Create New Panda"]
       choice = st.selectbox("Select an option from the console:", menu_options)
    
       if choice == "✨ Create New Panda":
           new_name = st.text_input("Name your new virtual companion:")
       if st.button("Generate & Boot Profile", use_container_width=True):
            if new_name.strip() != "":
                st.session_state["active_panda"] = new_name.strip().lower()
                st.rerun()
            else:
                st.warning("Please type a valid character name string.")
       else:
            st.info(f"Ready to mount memory context for: {choice}")
       if st.button(f"Boot {choice} Instance", use_container_width=True):
            st.session_state["active_panda"] = choice.lower()
            st.rerun()

     # =========================================================
       #      STEP 2: THE REAL DASHBOARD ROAD (THE MAIN ELSE BLOCK)
     #     =========================================================
    else:
      current_panda = st.session_state["active_panda"]
    
     # --- STATE HYDRATION GATEKEEPER ---
      if "loaded_panda" in st.session_state and st.session_state["loaded_panda"] != current_panda:
          if "energy" in st.session_state:
            del st.session_state["energy"]
          if "messages" in st.session_state:
            del st.session_state["messages"]
            
      st.session_state["loaded_panda"] = current_panda
      saved_data = memory_manager.load_memory(current_panda)
    
      # Synchronize states cleanly using safe default schema boundaries
      if "energy" not in st.session_state:
        st.session_state.energy = saved_data.get("energy", 100)

      if "messages" not in st.session_state:
        st.session_state.messages = saved_data.get("chat_history", [])
        if not st.session_state.messages:
            st.session_state.messages = [{"role": "assistant", "content": f"Hello! I am {current_panda.capitalize()}."}]

      # --- MAIN INTERFACE DISPLAY ---
      st.title(f"🐼 Managing Dashboard: {current_panda.capitalize()}")
      st.write(f"Active Profile File Context: all_pandas/{current_panda}.json")

     # Dynamic Mood Engine Logic
      def calculate_live_mood(energy):
          if energy > 80: return "Energetic & Happy 🎋"
          elif energy > 40: return "Chilled Out 🐼"
          else: return "Tired & Grumpy 💤"

      current_mood = calculate_live_mood(st.session_state.energy)
      is_full = st.session_state.energy >= 100
      is_exhausted = st.session_state.energy <= 0

      # --- SIDEBAR VITAL CONTROLS ---
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

     # --- CHAT DISPLAY STREAM ---
      for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

      # --- BALANCED INPUT PIPELINE (SAFE INDENTATION OUTSIDE CRASH REGIONS) ---
      user_input = st.chat_input(f"Talk to {current_panda.capitalize()}...")
    
      if user_input:
        # 1. Update session state locally and render instantly
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
            
        # 2. Trigger API processing wrapper ONLY when text exists
        with st.chat_message("assistant"):
            with st.spinner(f"{current_panda.capitalize()} is processing response..."):
                pandy_response = pandy_brain.talk_to_pandy_web(
                    user_msg=user_input, 
                    live_energy=st.session_state.energy, 
                    live_mood=current_mood,
                    memo=st.session_state.messages
                )
                st.write(pandy_response)
                
        # 3. Save downstream timeline states to storage disk
        st.session_state.messages.append({"role": "assistant", "content": pandy_response})
        memory_manager.save_memory(st.session_state["active_panda"], st.session_state.energy, st.session_state.messages)
        

  # ==========================================
 # 📓 APP 2: AI JOURNALING ASSISTANT ROUTE
 # ==========================================
else:
    st.title("📓 Personal AI Journaling Assistant")
    st.subheader("Day 35: Historical Stream Hydration & Feed Layout")

    if "journal_entries" not in st.session_state:
        st.session_state.journal_entries = []

    # --- SECTION 1: INTERACTIVE INPUT & PERSISTENCE ---
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
                import time
                import json
                import os
                from datetime import datetime
                
                time.sleep(0.3)
                text_lower = journal_input.lower()
                
                # Deterministic simulation matching engine
                if "tired" in text_lower or "stress" in text_lower or "exhausted" in text_lower:
                    analysis_data = {"sentiment_score": 4, "dominant_mood": "Exhausted", "summary_tag": "Exam Fatigue"}
                elif "happy" in text_lower or "clear" in text_lower or "pass" in text_lower or "win" in text_lower:
                    analysis_data = {"sentiment_score": 9, "dominant_mood": "Accomplished", "summary_tag": "Major Win"}
                else:
                    analysis_data = {"sentiment_score": 7, "dominant_mood": "Balanced", "summary_tag": "Steady Progress"}
                    
                entry_payload = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "raw_text": journal_input,
                    "metrics": analysis_data
                }
                
                # File system serialization append
                db_filename = "journal_db.json"
                if os.path.exists(db_filename):
                    with open(db_filename, "r") as f:
                        try: history_log = json.load(f)
                        except: history_log = []
                else:
                    history_log = []
                    
                history_log.append(entry_payload)
                with open(db_filename, "w") as f:
                    json.dump(history_log, f, indent=4)
                    
                st.toast("Entry saved locally!", icon="💾")

                # Render active metrics cards
                st.success(f"Dominant Mood: {analysis_data['dominant_mood']}")
                st.metric(label="Sentiment Score", value=f"{analysis_data['sentiment_score']}/10")
                st.info(f"Summary: {analysis_data['summary_tag']}")
        else:
            st.info("Awaiting input transmission.")

    # --- SECTION 2: DAY 35 HISTORICAL TIMELINE FEED ---
        # --- SECTION 2: DAY 36 HISTORICAL TIMELINE FEED & STATS ---
    st.markdown("---")
    st.markdown("### 📜 Past Reflections Timeline")

    import json
    import os

    db_filename = "journal_db.json"
    if os.path.exists(db_filename):
        with open(db_filename, "r") as f:
            try:
                saved_logs = json.load(f)
            except:
                saved_logs = []
                
        if saved_logs:
            # 1. CORE DATA AGGREGATION: Parse integers to build analytical KPI metrics
            total_entries = len(saved_logs)
            scores = [log.get("metrics", {}).get("sentiment_score", 7) for log in saved_logs]
            avg_score = sum(scores) / total_entries if total_entries > 0 else 0.0
            
            # Determine current mood trend based on average score thresholds
            if avg_score >= 8.0: trend_emoji, trend_text = "🚀", "Thriving"
            elif avg_score >= 6.0: trend_emoji, trend_text = "⚖️", "Stable / Balanced"
            else: trend_emoji, trend_text = "📉", "Fatigued / Low Energy"

            # Render KPI Columns at the apex of the timeline section
            stat_col1, stat_col2, stat_col3 = st.columns(3)
            with stat_col1:
                st.metric(label="Total Reflections Logged", value=f"{total_entries} Days")
            with stat_col2:
                st.metric(label="Lifetime Sentiment Avg", value=f"{avg_score:.1f} / 10")
            with stat_col3:
                st.markdown(f"**Current Status Trend:**")
                st.info(f"{trend_emoji} {trend_text}")
                
            st.markdown("#### Chronological Entries Feed")
            
            # Reverse logs to ensure newest records sit at the absolute top
            display_logs = list(reversed(saved_logs))
            
            # 2. RUN EXPANDER ITERATION LOOP
            for index, log in enumerate(display_logs):
                ts = log.get("timestamp", "Unknown Time")
                mood = log.get("metrics", {}).get("dominant_mood", "Balanced")
                score = log.get("metrics", {}).get("sentiment_score", 7)
                tag = log.get("metrics", {}).get("summary_tag", "Progress")
                text = log.get("raw_text", "")
                
                with st.expander(f"📅 {ts} | Mood: {mood} ({score}/10)"):
                    st.markdown(f"**Short Tag:** `{tag}`")
                    st.info(text)
        else:
            st.warning("No historical logs found. Submit your first entry above to populate your database file!")
    else:
        st.warning("Database file not initialized yet. Write an entry to create your local history stream!") 