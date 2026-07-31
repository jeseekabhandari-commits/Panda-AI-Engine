"""
Project Dashboard Engine
Phase 1 Production Build: Pandy Virtual Pet & AI Journaling Assistant
Compliance: PEP 8 Structural Standards & Phase 1 Performance Contracts
"""

import os
import json
import time
import pandas as pd
from datetime import datetime
import streamlit as st
from memory_service import MemoryService  # Adjust file name if different
from panda_brain_v1 import PandaBrain
from extractor import MeetingNoteExtractor
from dotenv import load_dotenv
from ingest_service import insert_job_description,search_jobs
from extractor import JobMetadataExtractor
# =====================================================================
# GLOBAL CONFIGURATION & PERFORMANCE SETTINGS
# =====================================================================
load_dotenv()
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
    Enforces atomic thread safety via shadow staging and triggers an automated
    timestamped temporal backup copy in a secure vault directory.
    """
    if not payload or not isinstance(payload, dict):
        st.warning("Validation Skipped: Attempted to log an empty or invalid data payload structure.")
        return False

    temp_filepath = f"{filepath}.tmp"
    backup_dir = "journal_vault_backups"
    
    try:
        # Enforce instant initialization of the backup directory vault
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        # Load stable memory frames
        history_log = load_database_records(filepath)
        history_log.append(payload)
        
        # 1️⃣ Write atomic data into the shadow clone first
        with open(temp_filepath, "w", encoding="utf-8") as temp_stream:
            json.dump(history_log, temp_stream, indent=4)
        
        # 2️⃣ Perform atomic replacement over production file
        if os.path.exists(temp_filepath):
            os.replace(temp_filepath, filepath)
            
            # 3️⃣ TEMPORAL ROTATION: Generate isolated snapshot mirror
            timestamp_slug = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{timestamp_slug}.json"
            backup_filepath = os.path.join(backup_dir, backup_filename)
            
            with open(backup_filepath, "w", encoding="utf-8") as backup_stream:
                json.dump(history_log, backup_stream, indent=4)
                
            return True
        return False
    except (IOError, OSError) as write_error:
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)  # Clean up orphaned temp files
        st.error(f" Critical Storage Write Failure: {write_error}")
        return False
    

def execute_offline_sentiment_pipeline(text: str) -> dict:
    """Applies a weighted frequency matrix and input length coefficient to 
    dynamically compute granular sentiment indices without hitting web APIs.

    Args:
        text (str): Raw string expression submitted from the frontend layer.

    Returns:
        dict: Target schema tracking indicators (score, mood, tag summary).
    """
    text_lower = text.lower()
    word_count = len(text_lower.split())
    
    # Define dynamic analytical buckets
    fatigue_keywords = ["tired", "stress", "exhausted", "hard", "sad", "fail", "bad"]
    growth_keywords = ["happy", "clear", "pass", "win", "adventure", "fun", "good", "learned"]
    
    # Calculate keyword density matches
    fatigue_score = sum(text_lower.count(key) for key in fatigue_keywords)
    growth_score = sum(text_lower.count(key) for key in growth_keywords)
    
    # Base calculation baseline
    base_score = 7
    net_coefficient = growth_score - fatigue_score
    calculated_score = base_score + net_coefficient
    
    # Apply entry length bias (longer reflections reflect deeper processing)
    if word_count > 15 and calculated_score >= 7:
        calculated_score = min(calculated_score + 1, 10)
    elif word_count > 15 and calculated_score < 7:
        calculated_score = max(calculated_score - 1, 1)
        
    # Boundary clamp validation
    calculated_score = max(1, min(calculated_score, 10))
    
    # Schema routing assignment
    if calculated_score >= 8:
        return {"sentiment_score": calculated_score, "dominant_mood": "Accomplished", "summary_tag": "Dynamic Win"}
    elif calculated_score >= 5:
        return {"sentiment_score": calculated_score, "dominant_mood": "Balanced", "summary_tag": "Steady Momentum"}
    else:
        return {"sentiment_score": calculated_score, "dominant_mood": "Exhausted", "summary_tag": "Fatigue Warning"}
 

def get_journal_context_for_agent(journal_filepath: str) -> dict:
    """Safely parses disk journal logs to extract live stress indicators,
    preventing any file locks or schema crashes.
    """
    context = {"drift_flag": False, "recent_avg": 7.0}
    try:
        if os.path.exists(journal_filepath):
            with open(journal_filepath, "r", encoding="utf-8") as file:
                logs = json.load(file)
            if logs:
                total_logs = len(logs)
                global_avg = sum(log.get("metrics", {}).get("sentiment_score", 7) for log in logs) / total_logs
                
                # Extract rolling 3-day window metrics
                recent_3_scores = [log.get("metrics", {}).get("sentiment_score", 7) for log in logs[-3:]]
                recent_3_avg = sum(recent_3_scores) / len(recent_3_scores) if recent_3_scores else global_avg
                
                context["recent_avg"] = round(recent_3_avg, 2)
                context["drift_flag"] = (global_avg - recent_3_avg) >= 2.0
    except Exception as context_error:
        # Prevent any structural crashes in Pandy's route if journal file is corrupted
        pass
    return context

# ==========================================
# 🗺️ GLOBAL MULTI-APP NAVIGATION ROUTER
# ==========================================

st.sidebar.markdown("---")
# --- STATE SYNCHRONIZATION RUNTIME INITIALIZATION ---
if "current_active_view" not in st.session_state:
    st.session_state["current_active_view"] = "📓 Personal AI Journal"

# Sidebar Selection Gate
st.sidebar.title("🚀 Project Dashboard")
active_app = st.sidebar.radio(
    "Select Application:",
    ["🐼 Pandy Virtual Pet", "📓 Personal AI Journal","video extractor🤖🤖","⚡ AI Data Ingestion Engine"],
    index=1 if st.session_state["current_active_view"] == "📓 Personal AI Journal" else 0
)

# ==========================================


# 🔄 THE SYNC BARRIER: Detect cross-application transitions and flush stale layouts
if active_app != st.session_state["current_active_view"]:
    st.session_state["current_active_view"] = active_app
    # Evict temporary operational flags from memory to prevent bleed-through
    keys_to_clear = [k for k in st.session_state.keys() if k.startswith("del_") or k in ["journal_input"]]
    for key in keys_to_clear:
        st.session_state.pop(key, None)
    st.toast("Application context synchronized cleanly!", icon="🔄")
    st.rerun()


# ==========================================
# ⚙️ SYSTEM LIFECYCLE DESTRUCTION GATE (NEW)
# ==========================================
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚠️ System Maintenance")

# Leverage an expander state to act as a dual-layer confirmation barrier
with st.sidebar.expander("🚨 Factory Reset Data Vault"):
    st.warning("This operation is completely destructive and will instantly purge all historical metric data nodes.")
    
    # Injected Confirmation Safe-Lock Toggle
    confirm_purge = st.checkbox("I understand this action cannot be undone.", key="purge_lock")
    
    # Execution Button Gate
    if st.button("💥 Execute Hard Factory Reset", type="primary", disabled=not confirm_purge):
        temp_reset_path = f"{DB_FILENAME}.tmp"
        try:
            # Step 1: Write an empty structural layout to our shadow file
            with open(temp_reset_path, "w", encoding="utf-8") as temp_stream:
                json.dump([], temp_stream, indent=4)
            
            # Step 2: Swap the blank template atomically over production database
            os.replace(temp_reset_path, DB_FILENAME)
            
            # Step 3: Evict runtime cache indicators from session state memory
            st.session_state.journal_entries = []
            
            st.toast("System architecture successfully restored to factory defaults!", icon="🧹")
            time.sleep(0.4)
            st.rerun()
            
        except IOError as reset_fault:
            if os.path.exists(temp_reset_path):
                os.remove(temp_reset_path)
            st.sidebar.error(f"Reset Failure: {reset_fault}")
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
         
        # Fetch live telemetry from the Journal database
        journal_stats = get_journal_context_for_agent("journal_db.json")
        
        # Adjust Pandy's personality parameters based on live stress flags
        if journal_stats["drift_flag"]:
            pandy_mood = "❤️ Empathetic & Supportive"
            pandy_prompt_modifier = (
                "SYSTEM NOTE: The user's system metrics indicate a severe fatigue dip or mental burnout. "
                "Shift your tone. Be incredibly supportive, gentle, encouraging, and recommend brief breaks. "
                "Prioritize comfort over high-energy productivity banter."
            )
        else:
            pandy_mood = "⚡ Playful & Energetic"
            pandy_prompt_modifier = "SYSTEM NOTE: The user is operating at normal or high momentum. Keep your usual witty, engaging self."
        
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
            
            # Status Card in Pandy's interface
        with st.expander("🧠 Pandy's Cognitive State", expanded=True):
            st.write(f"**Current Personality Vector:** {pandy_mood}")
            st.write(f"**Synced 3-Day Momentum Average:** {journal_stats['recent_avg']}/10")
            if journal_stats["drift_flag"]:
                st.warning("⚠️ Pandy has detected your fatigue dip and entered comforting mode.")
        
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
                   enriched_user_msg = user_input
                   if journal_stats["drift_flag"]:
                        enriched_user_msg += f"\n\n[CONTEXT OVERRIDE: {pandy_prompt_modifier}]"
                   
                   pandy_response = pandy_brain.talk_to_pandy_web(
                        user_msg=enriched_user_msg, 
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
elif active_app == "📓 Personal AI Journal":
        st.title("📓 Personal AI Journaling Assistant") 
        st.subheader("Day 52: Dynamic Memory Indexing & Contextual Recall Thresholds")
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
                # ⏱️ START TELEMETRY CLOCK
                execution_start_timestamp = time.perf_counter()
                
                with st.spinner("Processing local text matrices..."):
                    time.sleep(0.05)  # Mimicking optimized hardware pipeline latency
                    
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
                    
                    # Render Design Variations
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

                # ⏱️ STOP TELEMETRY CLOCK
                execution_end_timestamp = time.perf_counter()
                total_latency_ms = (execution_end_timestamp - execution_start_timestamp) * 1000
                
                # Render clear performance metrics below the analytics window
                st.metric(
                    label="⚡ System Processing Latency", 
                    value=f"{total_latency_ms:.2f} ms", 
                    delta="Target: < 200.00 ms",
                    delta_color="normal" if total_latency_ms < 200 else "inverse"
                )
            else:
                st.info("Awaiting input transmision")
        st.markdown("---")
        st.markdown("### 📊 Historical Analytics & Velocity Tracking")

        saved_logs = load_database_records(DB_FILENAME)

        if not saved_logs:
            st.warning("Database file empty or uninitialized.")
        else:
            # --- COMPUTE TIME-SERIES CLUSTERING ---
            current_date_str = datetime.now().strftime("%Y-%m-%d")
            
            today_scores = []
            past_scores = []
            
            for log in saved_logs:
                log_ts = log.get("timestamp", "")
                log_score = log.get("metrics", {}).get("sentiment_score", 7)
                
                # Cluster logs based on calendar day matching
                if log_ts.startswith(current_date_str):
                    today_scores.append(log_score)
                else:
                    past_scores.append(log_score)
            
            # --- CALCULATE AGGREGATE COUPLING COEFFICIENTS ---
            # --- CALCULATE AGGREGATE COUPLING COEFFICIENTS ---
            total_logs = len(saved_logs)
            global_avg = sum(log.get("metrics", {}).get("sentiment_score", 7) for log in saved_logs) / total_logs
            
            # 🧠 DYNAMIC CACHE EVICTION: Enforce a strict 30-day sliding viewport window
            VIEW_WINDOW_LIMIT = 30
            active_window_logs = saved_logs[-VIEW_WINDOW_LIMIT:]  # Slices only the latest 30 records
            evicted_count = max(0, total_logs - VIEW_WINDOW_LIMIT)
            
            today_avg = sum(today_scores) / len(today_scores) if today_scores else None
            past_avg = sum(past_scores) / len(past_scores) if past_scores else global_avg
            
            # Compute Velocity Delta
            if today_avg is not None:
                velocity_delta = today_avg - past_avg
                delta_string = f"{velocity_delta:+.2f} vs. Baseline"
            else:
                velocity_delta = 0.0
                delta_string = "No entries today yet"

            # ⚡ DAY 50: ADVANCED STATISTICAL DRIFT INTERCEPTOR
            # Calculate the rolling score variance of the last 3 entries to detect sudden mental/productivity shifts
            recent_3_scores = [log.get("metrics", {}).get("sentiment_score", 7) for log in saved_logs[-3:]]
            recent_3_avg = sum(recent_3_scores) / len(recent_3_scores) if recent_3_scores else global_avg
            
            # Drift Condition: If short-term velocity drops 2.0+ points below the global multi-day average
            drift_anomaly_detected = (global_avg - recent_3_avg) >= 2.0

            # 🚨 ANOMALOUS SHOCK TRIPWIRE BANNER
            if drift_anomaly_detected:
                st.error(f"🚨 **Critical Operational Drift Flagged:** A sudden localized baseline fracture has been detected. Your 3-day momentum average ({recent_3_avg:.1f}/10) has plummeted drastically relative to your lifetime system baseline average ({global_avg:.1f}/10). Investigate burn-out factors immediately.")
                st.markdown("---")

            stat_col1, stat_col2, stat_col3 = st.columns(3)
            
            with stat_col1:
                st.metric(
                    label="Total Reflections Logged", 
                    value=f"{total_logs} Days"
                )
            with stat_col2:
                st.metric(
                    label="Lifetime Sentiment Avg", 
                    value=f"{global_avg:.1f} / 10",
                    delta="System Baseline",
                    delta_color="off"
                )
            with stat_col3:
                if today_avg is not None:
                    main_velocity_display = f"{velocity_delta:+.2f}"
                    sub_delta_display = f"Today's Avg: {today_avg:.1f}/10"
                else:
                    main_velocity_display = "N/A"
                    sub_delta_display = "No Entries Today"
                
                st.metric(
                    label="Sentiment Velocity Delta", 
                    value=f"{today_avg:.1f} / 10" if today_avg is not None else "N/A", 
                    delta=delta_string,
                    delta_color="normal" if velocity_delta >= 0 else "inverse"
                )

            # Dynamic Status Trend Card
            st.markdown("#### Current Directional Vector")
                
            if velocity_delta > 0.5:
                st.success("🚀 Positive Acceleration: Your localized daily mindset is outperforming your historical baseline.")
            elif velocity_delta < -0.5:
                st.error("⚠️ Fatigue Dip Detected: Current logs point to an active energy drain compared to your baseline trend.")
            else:
                st.info("⚖️ Stable Equilibrium: Current velocity matches your steady historical momentum.")
            # ==========================================
            # 📊 DYNAMIC MOOD DISTRIBUTION MATRIX (NEW)
            # ==========================================
            st.markdown("#### 📉 Weekly Sentiment Density Distribution")
            
            # Extract and compile a flat vector of recent metrics
            historical_scores = [log.get("metrics", {}).get("sentiment_score", 7) for log in active_window_logs]
            
            if historical_scores:
                # Map structural categorical labels to score ranges for cleaner visualization
                score_categories = {
                    10: "Accomplished (10)", 9: "Accomplished (9)", 8: "Accomplished (8)",
                    7: "Balanced (7)", 6: "Balanced (6)", 5: "Balanced (5)",
                    4: "Exhausted (4)", 3: "Exhausted (3)", 2: "Exhausted (2)", 1: "Exhausted (1)"
                }
                
                # Construct a clean relational frequency series
                distribution_map = []
                for score in historical_scores:
                    distribution_map.append({
                        "Score Level": score,
                        "Mood Tier": score_categories.get(score, f"Level {score}"),
                        "Logs Count": 1
                    })
                
                # Formulate structured analytical dataframe
                chart_dataframe = pd.DataFrame(distribution_map)
                
                # Aggregate entries to compute frequency density per score bracket
                summary_chart_data = chart_dataframe.groupby(["Mood Tier"]).sum().reset_index()
                
                
                if evicted_count > 0:
                        st.caption(f"⚡ Performance Optimization Active: Displaying latest {VIEW_WINDOW_LIMIT} trends. ({evicted_count} historical records safely archived on disk).")
                
                # Render a high-fidelity native horizontal bar chart
                st.bar_chart(
                    data=summary_chart_data,
                    x="Mood Tier",
                    y="Logs Count",
                    use_container_width="stretch"
                )
            else:
                st.info("Insufficient metrics available to populate density charts.")
            # --- CHRONOLOGICAL FEED ---
            st.markdown("#### Chronological Entries Feed")
            logs_list = list(saved_logs)
            total_logs = len(logs_list)
                
            for index, log in enumerate(reversed(logs_list)):
                # Map the reverse loop index back to the true absolute disk array index
                true_disk_index = total_logs - 1 - index
                
                ts = log.get("timestamp", "Unknown Time")
                mood = log.get("metrics", {}).get("dominant_mood", "Balanced")
                score = log.get("metrics", {}).get("sentiment_score", 7)
                tag = log.get("metrics", {}).get("summary_tag", "Progress")
                text = log.get("raw_text", "")
                
                with st.expander(f"📅 {ts} | Mood: {mood} ({score}/10)"):
                    st.markdown(f"**Short Tag:** `{tag}`")
                    st.info(text)
                    
                    # 🛠️ THE MUTATION GATE: Targeted Record Erasure
                    # 🛠️ THE MUTATION GATE: Hardened Target Record Erasure
                    if st.button(f"🗑️ Erase Entry Record", key=f"del_{true_disk_index}_{ts[:19].replace(' ', '_')}"):
                        logs_list.pop(true_disk_index)
                        
                        temp_db_path = f"{DB_FILENAME}.tmp"
                        try:
                            # Stream state modifications safely to hidden staging layer first
                            with open(temp_db_path, "w", encoding="utf-8") as temp_stream:
                                json.dump(logs_list, temp_stream, indent=4)
                            
                            # Swap verified file matrix to production path
                            os.replace(temp_db_path, DB_FILENAME)
                            
                            st.toast("Record mutated successfully!", icon="💥")
                            time.sleep(0.2)
                            st.rerun()
                        except IOError as mutation_fault:
                            if os.path.exists(temp_db_path):
                                os.remove(temp_db_path)
                            st.error(f"Mutation Failure: {mutation_fault}")

elif active_app == "📹 Personal AI Video Extractor":
    st.title("📹 Personal AI Video Extractor")
    st.write("Upload a raw recording file, and let the background script compile structured lecture briefs.")
    st.markdown("---")
    
    # Keep the frontend ultra-lightweight by instantiating the backend class here
    extractor = MeetingNoteExtractor()
    
    # Render the input widget using a unique namespaced key
    uploaded_file = st.file_uploader(
        label="Drop your lecture or meeting video file here", 
        type=["mp4", "mov", "avi"],
        key="extractor_video_file"
    )
    
    if uploaded_file is not None:
        st.video(uploaded_file)
        
        # Action button to trigger processing execution
        if st.button("🚀 Trigger Pandy Note Extraction", type="primary"):
            with st.spinner("📥 Extracting soundtracks and compiling notes..."):
                try:
                    # Write out the temporary file stream so the backend can path it
                    temp_filename = f"temp_runtime_{uploaded_file.name}"
                    with open(temp_filename, "wb") as f:
                        f.write(uploaded_file.read())
                    
                    # Call the isolated pipeline logic in exactly one line of code
                    structured_notes = extractor.run_pipeline(temp_filename)
                    st.success("🎉 Note extraction successful!")
                    st.subheader(f"📝 Profile: {structured_notes['meeting_title']}")
                    st.write("**📋 Structured Summary:**")
                    st.info(structured_notes['detailed_summary'])
                    
                except Exception as e:
                    st.error(f"❌ Core pipeline execution crashed: {str(e)}")
                finally: 
                    # Immediate physical cleanup of the temporary video container
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
elif active_app=="AI Data Ingestion Engine":
       st.title("⚡ AI Data Ingestion Engine")
       st.caption("Day 58: Connecting Streamlit UI to PostgreSQL Pipeline")

       st.markdown("---")

       # Form Inputs
       with st.form("job_ingestion_form", clear_on_submit=True):
        st.subheader("📥 Ingest New Job Description")

        col1, col2 = st.columns(2)
        with col1:
          job_title = st.text_input("Job Title *", placeholder="e.g. AI Engineer")

        with col2:
         company_name = st.text_input("Company Name *", placeholder="e.g. Acme Corp")

         keywords_input = st.text_input("Keywords (comma separated)", placeholder="Python, PostgreSQL, Streamlit, LLMs")

         raw_text = st.text_area("Raw Job Description *", placeholder="Paste the full job post text here...", height=200)

       submit_btn = st.form_submit_button("🚀 Insert into Database", use_container_width=True)

      # Form Submission Processing
       if submit_btn:
       # Basic validation
        if not job_title.strip() or not company_name.strip() or not raw_text.strip():
         st.error("⚠️ Please fill in all required fields (Title, Company, and Raw Text).")
       else:
       # Process keywords into a list
        keywords = [kw.strip() for kw in keywords_input.split(",") if kw.strip()]

        # Call our Day 57 backend service function!
       with st.spinner("Ingesting into PostgreSQL..."):
        inserted_id = insert_job_description(
        title=job_title.strip(),
         company=company_name.strip(),
         raw_text=raw_text.strip(),
         keywords=keywords
       )

       if inserted_id:
        st.success(f"✅ Data Ingested Successfully! Database UUID: `{inserted_id}`")
       else:
        st.error("❌ Failed to insert data into the database. Check console logs.")                     

else:
    st.set_page_config(page_title="AI Job Engine", layout="wide")

    st.title("⚡ AI Job Description & Search Engine")

    # Sidebar navigation
    menu = st.sidebar.radio("Navigation", ["🔍 Search & Analytics", "📥 Ingest New Job"])

    # ==========================================
    # PAGE 1: SEARCH & ANALYTICS
    # ==========================================
    if menu == "🔍 Search & Analytics":
        st.header("🔍 Query Job Database")

        # Filter Section
        col1, col2 = st.columns(2)
        
        with col1:
            search_term = st.text_input("Search Title or Company", placeholder="e.g. Microsoft, AI Architect")
            
        with col2:
            skill_options = ["python", "Ruby", "c", "PostgreSQL", "Streamlit", "Docker", "REST APIs"]
            selected_keywords = st.multiselect("Filter by Skills (Array Overlap)", options=skill_options)

        limit = st.slider("Max Results", min_value=1, max_value=50, value=10)

        # Fetch results from PostgreSQL
        results = search_jobs(
            search_term=search_term if search_term else None,
            keywords=selected_keywords if selected_keywords else None,
            limit=limit
        )

        # Analytics Metrics
        st.markdown("---")
        m1, m2 = st.columns(2)
        m1.metric("Jobs Found", len(results))
        
        all_matched_keywords = set()
        for r in results:
            if r.get("extracted_keywords"):
                all_matched_keywords.update(r["extracted_keywords"])
        m2.metric("Unique Keywords in Query", len(all_matched_keywords))
        st.markdown("---")

        # Display Results Card View
        if results:
            for job in results:
                with st.expander(f"📌 {job['title']} — {job['company']}"):
                    st.write(f"**UUID:** `{job['id']}`")
                    st.write(f"**Created At:** {job['created_at']}")
                    
                    keywords = job.get('extracted_keywords', [])
                    if keywords:
                        st.write("**Extracted Keywords:**")
                        st.markdown(" ".join([f"`{kw}`" for kw in keywords]))
                    
                    st.subheader("Raw Text")
                    st.text(job.get('raw_text', ''))
        else:
            st.info("No records matched your search parameters.")

    # ==========================================
    # PAGE 2: AI-POWERED INGESTION
    # ==========================================
    elif menu == "📥 Ingest New Job":
        st.subheader("📥 AI Auto-Extraction & Ingestion")
        st.caption("Paste raw text below. Gemini will extract title, company, and keywords automatically.")

        with st.form("auto_job_ingestion_form", clear_on_submit=True):
            raw_text = st.text_area("Raw Job Description *", placeholder="Paste job post here...", height=220)
            submit_btn = st.form_submit_button("🚀 Extract & Ingest via Gemini", use_container_width=True)

        if submit_btn:
            if not raw_text.strip():
                st.error("⚠️ Please paste raw job text before submitting.")
            else:
                with st.spinner("Extracting metadata with Gemini and saving to PostgreSQL..."):
                    # 1. Run LLM Extractor
                    extractor = JobMetadataExtractor()
                    extracted_data = extractor.extract_metadata(raw_text)
                    
                    title = extracted_data.get("job_title", "Unspecified Title")
                    company = extracted_data.get("company", "Unspecified Company")
                    tech_skills = extracted_data.get("tech_skills", [])
                    soft_skills = extracted_data.get("soft_skills", [])
                    keywords = list(set(tech_skills + soft_skills))
                    
                    # 2. Insert into DB
                    inserted_id = insert_job_description(
                        title=title,
                        company=company,
                        raw_text=raw_text.strip(),
                        keywords=keywords
                    )

                    if inserted_id:
                        st.success(f"✅ Data Ingested Successfully! Database UUID: `{inserted_id}`")
                        st.json({
                            "extracted_title": title,
                            "extracted_company": company,
                            "extracted_keywords": keywords
                        })
                    else:
                        st.error("❌ Failed to insert data into PostgreSQL.")