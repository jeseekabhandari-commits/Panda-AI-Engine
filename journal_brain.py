import google.generativeai as genai
import json

class JournalRouter:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def analyze_entry(self, entry_text):
        """Forces the LLM to return strict JSON data."""
        prompt = f"""
        Analyze the following journal entry. Return ONLY a JSON object with these keys:
        - "sentiment_score": (int 1-10)
        - "dominant_mood": (string)
        - "summary_tag": (string - keep it under 3 words)
        
        Entry: {entry_text}
        """
        
        response = self.model.generate_content(prompt)
        
        # Clean the response to ensure it's valid JSON
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)