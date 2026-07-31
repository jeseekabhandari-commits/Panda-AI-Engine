import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
class MeetingNoteExtractor:
    def __init__(self, output_dir="processed_meetings"):
        self.output_dir = Path(__file__).resolve().parent.parent / output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.client = genai.Client()
        self.model_name = 'gemini-2.0-flash'
        # 🎯 HARDCODED KEY ENTRY ZONE:
        # Paste your exact key string here (with or without any prefixes)
        api_key = "PASTE_YOUR_EXACT_KEY_HERE"
        
        # Initialize the modern native Google client
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-2.0-flash' # Upgraded to modern baseline standard

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

class JobMetadataExtractor:
    def __init__(self, output_dir="processed_jobs"):
        self.output_dir = Path(__file__).resolve().parent / output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
      
        # Load API key safely from environment variable
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY not found in environment variables!")

        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-2.5-flash'
    def extract_job_metadata(self, raw_text: str) -> dict:
        """Processes raw job description text using Gemini structured JSON generation."""
        if not raw_text or not raw_text.strip():
            return self._safely_parse_and_heal_json("{}")

        try:
            print("🧠 Querying Gemini architecture model for structured job metadata...")
            
            structured_prompt = (
                "You are an expert technical recruiter. Analyze the provided job description thoroughly.\n"
                "Extract key details into a JSON object with strictly the following keys:\n"
                "{\n"
                '  "tech_skills": ["List of technical tools, languages, frameworks"],\n'
                '  "soft_skills": ["List of interpersonal or soft skills"],\n'
                '  "experience_level": "e.g., Senior, 3+ years, Entry Level"\n'
                "}\n\n"
                f"Job Description:\n\"\"\"{raw_text}\"\"\""
            )

            # Gemini generation call using structured JSON configuration
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=structured_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            raw_response_text = response.text.strip()
            validated_data = self._safely_parse_and_heal_json(raw_response_text)
            return validated_data

        except Exception as e:
            print(f"❌ Gemini Extraction pipeline error: {str(e)}")
            return self._safely_parse_and_heal_json("{}")

    def _safely_parse_and_heal_json(self, raw_text: str) -> dict:
        """Parses raw response text and heals missing keys to prevent downstream pipeline crashes."""
        cleaned = raw_text.replace("```json", "").replace("```", "").strip()
        
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            print("⚠️ Response was not valid JSON. Deploying fallback default schema.")
            parsed = {}

        schema_defaults = {
            "tech_skills": [],
            "soft_skills": [],
            "experience_level": "Not specified"
        }
        
        final_valid_dict = {}
        for key, default_value in schema_defaults.items():
            if key not in parsed or parsed[key] is None:
                final_valid_dict[key] = default_value
            else:
                final_valid_dict[key] = parsed[key]
                
        return final_valid_dict    

import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types


class ResumeExtractor:
    def __init__(self):
        load_dotenv(override=True)
        
        # Load API key cleanly from environment variables
        raw_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
        api_key = raw_key.strip().strip("'").strip('"')
        
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY missing in .env file!")

        # Initialize the GenAI client with your dynamically loaded API key
        self.client = genai.Client(api_key=api_key)
        
        # Using gemini-3.5-flash from your active key list
        self.model_name = "gemini-3.5-flash"
        
    def extract_resume_skills(self, raw_resume_text: str) -> dict:
        """Uses Gemini to parse raw resume text and extract technical/core skills into JSON."""
        if not raw_resume_text or not raw_resume_text.strip():
            return self._safely_parse_and_heal_json("{}")

        try:
            print(f"🧠 Querying {self.model_name} for resume skills...")
            
            structured_prompt = (
                "You are an expert technical recruiter and resume parser.\n"
                "Extract all technical skills, programming languages, frameworks, databases, tools, "
                "and core methodologies from the resume text below.\n"
                "Return ONLY a valid JSON object matching this schema:\n"
                "{\n"
                '  "candidate_skills": ["skill1", "skill2", "skill3"]\n'
                "}\n\n"
                f"Resume Text:\n\"\"\"{raw_resume_text}\"\"\""
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=structured_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            raw_response_text = response.text.strip()
            validated_data = self._safely_parse_and_heal_json(raw_response_text)
            return validated_data

        except Exception as e:
            print(f"❌ Gemini Resume Extraction pipeline error: {str(e)}")
            return self._safely_parse_and_heal_json("{}")

    def _safely_parse_and_heal_json(self, raw_text: str) -> dict:
        """Parses raw response text and heals missing keys to prevent downstream pipeline crashes."""
        cleaned = raw_text.replace("```json", "").replace("```", "").strip()
        
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            print("⚠️ Response was not valid JSON. Deploying fallback default schema.")
            parsed = {}

        schema_defaults = {
            "candidate_skills": []
        }
        
        final_valid_dict = {}
        for key, default_value in schema_defaults.items():
            if key not in parsed or parsed[key] is None:
                final_valid_dict[key] = default_value
            else:
                final_valid_dict[key] = parsed[key]
                
        return final_valid_dict