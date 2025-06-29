import requests
from typing import List, Dict, Tuple
import re
import os

class EnvironmentalExpert:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")  # Load from environment variable
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.last_sources = []
        self.system_prompt = """You are a senior environmental scientist. Provide:
1. Precise definitions
2. Current statistics (2020-2024)
3. 1 geographic example
4. 2 mitigation strategies
Format:
• Key Point: Detail (Source)
• Example: Location - Result
Never ask questions. Max 8 bullet points."""

    def get_response(self, user_query: str) -> str:
        self.last_sources = []
        prompt = self._enhance_query(user_query)
        
        payload = {
            "inputs": self._format_prompt(prompt),
            "parameters": {
                "max_new_tokens": 350,
                "temperature": 0.4,
                "do_sample": False,
                "return_full_text": False
            }
        }
        
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        response.raise_for_status()
        
        return self._process_response(response.json()[0]['generated_text'])

    def get_last_sources(self) -> List[str]:
        return list(set(self.last_sources))

    def _enhance_query(self, query: str) -> str:
        enhancements = {
            r'carbon|co2': " Include current atmospheric levels (ppm) and sequestration methods.",
            r'water|rain': " Focus on FAO water stress indices and conservation techniques.",
            r'pollut|emission': " Reference WHO air quality guidelines and reduction technologies."
        }
        
        for pattern, enhancement in enhancements.items():
            if re.search(pattern, query, re.IGNORECASE):
                return f"{query}. {enhancement}"
        return query

    def _format_prompt(self, user_input: str) -> str:
        return f"""<|system|>
{self.system_prompt}</s>
<|user|>
{user_input}</s>
<|assistant|>"""

    def _process_response(self, text: str) -> str:
        # Extract sources
        sources = re.findall(r'\((.*?)\)', text)
        self.last_sources.extend(s for s in sources if len(s) < 50)  # Filter out long parens
        
        # Clean formatting
        text = re.sub(r'\n+', '\n', text)  # Remove extra newlines
        text = re.sub(r'(\w)\.(\w)', r'\1. \2', text)  # Add space after periods
        
        # Ensure bullet points
        if not text.lstrip().startswith(('•', '-')):
            text = '• ' + text.replace('\n', '\n• ')
        
        # Limit to 8 bullet points
        bullets = [line for line in text.split('\n') if line.strip().startswith(('•', '-'))]
        if len(bullets) > 8:
            text = '\n'.join(bullets[:8]) + "\n[...]"
        
        return text.strip()