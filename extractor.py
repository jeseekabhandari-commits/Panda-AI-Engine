import os
import json
from pathlib import Path
from google import genai
from google.genai import types

class MeetingNoteExtractor:
    def __init__(self, output_dir="processed_meetings"):
        self.output_dir = Path(__file__).resolve().parent.parent / output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.client = genai.Client()
        self.model_name = 'gemini-2.5-flash'
        # 🎯 HARDCODED KEY ENTRY ZONE:
        # Paste your exact key string here (with or without any prefixes)
        api_key = "PASTE_YOUR_EXACT_KEY_HERE"
        
        # Initialize the modern native Google client
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-2.5-flash' # Upgraded to modern baseline standard

    def run_pipeline(self, video_path: str) -> dict:
        """Processes video files directly using the unified API architecture client."""
        try:
            print(f"🚀 Initializing modern API upload for: {Path(video_path).name}")
            
            # The unified client safely routes modern authentication parameters directly
            video_file_instance = self.client.files.upload(file=Path(video_path))
            print(f"📡 File uploaded to Google Media Server. Name: {video_file_instance.name}")
            
            structured_prompt = (
                "You are an expert secretary. Analyze this video recording thoroughly.\n"
                "Listen to the audio and inspect visual notes where applicable.\n"
                "You MUST return a JSON object with exactly the following keys:\n"
                "{\n"
                "  \"meeting_title\": \"Descriptive title of the lecture or discussion\",\n"
                "  \"key_decisions\": [\"Key decision/rule 1\", \"Key decision/rule 2\"],\n"
                "  \"detailed_summary\": \"A highly detailed paragraph summarizing the major themes.\"\n"
                "}"
            )
            
            print("🧠 Querying Gemini architecture model with structured parameters...")
            
            # Modern generation config definition matching modern syntax standards
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[video_file_instance, structured_prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            raw_response_text = response.text.strip()
            validated_data = self._safely_parse_and_heal_json(raw_response_text)
            
            output_file = self.output_dir / f"{Path(video_path).stem}_summary.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(validated_data, f, indent=4)
                
            print(f"💾 Persisted validated summary to: {output_file.name}")
            return validated_data

        except Exception as e:
            print(f"❌ Modern Core pipeline crashed: {str(e)}")
            raise e

    def _safely_parse_and_heal_json(self, raw_text: str) -> dict:
        """Parses raw text and heals missing keys to prevent downstream UI crashes."""
        cleaned = raw_text.replace("```json", "").replace("```", "").strip()
        
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            print("⚠️ Raw response was not valid JSON. Deploying blank fallback object.")
            parsed = {}

        schema_defaults = {
            "meeting_title": "Untitled Meeting / Lecture Note",
            "key_decisions": ["No distinct decisions parsed from recording."],
            "detailed_summary": "The model failed to return a structured summary. Please check the video input."
        }
        
        final_valid_dict = {}
        for key, default_value in schema_defaults.items():
            if key not in parsed or not parsed[key]:
                final_valid_dict[key] = default_value
            else:
                final_valid_dict[key] = parsed[key]
                
        return final_valid_dict