🐼 Panda-AI-Engine
An enterprise-grade, state-managed AI character engine and multi-tenant Retrieval-Augmented Generation (RAG) platform built with Python, FastAPI, LangChain, ChromaDB, and Gemini.

📌 Overview
This repository represents the active development evolution of Pandy, an interactive AI companion and smart document reasoning engine built as part of a 100-Day AI Product Engineering Sprint.

The system has evolved from a local, hardware-aware CLI virtual pet into a full-stack, multi-tenant enterprise system capable of real-time environmental context integration, state-managed conversational personalities, and secure, isolated vector document retrieval.

🛠️ Key Features
Multi-Tenant Document Reasoning (RAG): Ingests PDFs, Word documents (.docx), and plain text files with strict tenant isolation (tenant_id) and vector persistence in ChromaDB.

Context-Grounded Generation: Uses LangChain prompt scaffolding combined with google-generativeai (Gemini) to provide zero-hallucination answers anchored exclusively to retrieved document context.

Hardware-Aware Vitals & Metabolism: Monitored via a dedicated vitals.py abstraction layer (psutil), tying CPU load and battery metrics directly to character mood and energy decay.

Dynamic Weather & Real-Time Environment: Integrates with the Open-Meteo API to pull live weather data for Kathmandu, modulating character energy levels dynamically.

State & Memory Management: Persistent JSON storage layer (pandy_memory.json) and reactive UI state tracking via Streamlit.

Resilient Defensive Architecture: Built-in Safe Mode fallbacks, exception handling across sensor networks, and autonomous execution freezes for high-stress system states.

🏗️ System Architecture & Sprint ProgressionPlaintext               +-------------------------------------------+
               |        Pandy Virtual Companion UI         |
               |         (Streamlit / Local Loop)          |
               +---------------------++--------------------+
                                     ||
                                     \/
               +-------------------------------------------+
               |    PandaBrain & Vitals Engine Layer       |
               | (psutil / Open-Meteo API / Personality)   |
               +---------------------++--------------------+
                                     ||
                                     \/
               +-------------------------------------------+
               |   Multi-Tenant RAG Pipeline (FastAPI)     |
               +---------------------++--------------------+
                                     ||
                    +----------------+----------------+
                    |                                 |
                    \/                                \/
      +----------------------------+    +----------------------------+
      |  ChromaDB Vector Storage   |    |      LangChain + Gemini    |
      | (Metadata: tenant_id/doc)  |    |  (Context-Grounded Prompt) |
      +----------------------------+    +----------------------------+
Sprint Milestones

Phase 1: Core Engine,

 Hardware Vitals & Personality LayerOOP Architecture: Encapsulated state updates, behavior logic, and persistent storage inside the core PandaCharacter class.
 
 Hardware Abstraction (vitals.py): Isolated low-level psutil dependencies. Implemented a hardware-driven blocking hunger_check loop during low-power states.
 
 Personality Engine (personality.py): Mapped system metrics to response strings via PandyVoice. Resolved immutable string lookup patterns to ensure reliable state hand-offs.
 
 Runtime Guardrails & Logging: Structured diagnostic logging payloads (f"CRITICAL SHUTDOWN - CPU: {cpu}% | Batt: {batt}%") and system-wide execution freezes during "stressed" states.
 
 Phase 2: Live AI Cloud Integration & Reactive Dashboard
 
 Modular Brain Integration (panda_brain_v1.py): Encapsulated natural language orchestration into PandaBrain with integrated semantic intent filtering (TextBlob).
 
 Live Network Handshake: Transitioned from offline fallbacks to HTTPS pipelines utilizing google-generativeai.
 
 Streamlit Reactive Dashboard (app.py): Deployed a local UI synchronizing companion vitals, energy metrics, and context-anchored chat sessions.
 
 Phase 3: Enterprise Multi-Tenant RAG Architecture 
 
 Vector Embeddings & Overlap Chunking : Engineered a recursive text splitter ($500\text{ chars} / 100\text{ char overlap}$) and persisted embeddings into ChromaDB. Applied explicit metadata filtering (tenant_id) for absolute multi-tenant database isolation.Multi-Format Ingestion: Built support for .pdf, .txt, and .docx parsing via python-docx memory buffers.
 
 Semantic Retrieval & LangChain Integration : Connected ChromaDB retrieval with LangChain's ChatGoogleGenerativeAI pipeline. Aligned vector query signatures (top_k) to construct strict, context-grounded prompt payloads with zero cross-tenant data leak.
 
 📂 Project StructurePlaintext├── app.py                  # Reactive Streamlit Web Dashboard
├── main.py                 # FastAPI Application Router & Endpoint Definitions
├── panda_brain_v1.py       # AI Operations Manager & Prompt Payload Handler
├── product_manager.py      # Core System Orchestration Script
├── personality.py          # PandyVoice Personality Mapping & Response Dictionary
├── vitals.py               # Hardware Metrics & Sensor Subsystem (psutil Wrapper)
├── vitals_engine.py        # Companion State Arithmetic & Metabolism Simulator
├── vector_store.py         # ChromaDB Vector Store Handler & Multi-Tenant Querying
├── services/
│   └── rag_chain.py        # LangChain Prompt Template & Gemini Integration Pipeline
├── pandy_memory.json       # Persistent Local Storage for Character State & History
└── requirements.txt        # System Dependencies
