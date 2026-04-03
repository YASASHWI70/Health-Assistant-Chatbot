"""
agents/symptom_extraction_agent.py - Extracts structured symptoms from free-text input.

Uses an LLM with a structured JSON output prompt to parse:
  - Symptom names
  - Severity (mild/moderate/severe)
  - Duration
  - Location (body part)
  - Modifiers (intermittent, worsening, etc.)
"""


""" 
User Input
   ↓
SYSTEM PROMPT (rules)
   ↓
Ollama LLM (llama3.2:1b)
   ↓
Raw text output (string)
   ↓
Clean markdown
   ↓
json.loads()
   ↓
Pydantic validation
   ↓
Final structured objects ✅
"""

import json
import re
from typing import List, Optional


from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

from backend.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from backend.utils.models import ExtractedSymptom
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class SymptomExtractionAgent:
    """
    Extracts structured medical symptoms from unstructured patient text.

    Converts natural language descriptions like "I've had a bad headache
    and fever for two days" into structured ExtractedSymptom objects.
    """

    SYSTEM_PROMPT = """You are a medical NLP system.

    STRICT RULES:
    - Return ONLY valid JSON array
    - Extract ALL symptoms mentioned
    - Each item MUST be an object
    - NEVER return a list of strings
    - NEVER return plain text

    Each item must follow:

    {
        "name": "symptom name",
        "severity": "mild | moderate | severe | null",
        "duration": "timeframe or null",
        "location": "body part or null",
        "modifiers": []
    }

    Example:
    [
        {
            "name": "fever",
            "severity": null,
            "duration": "2 days",
            "location": null,
            "modifiers": []
        }
    ]"""

    def __init__(self):
        self.llm = ChatOllama(
            model=OLLAMA_MODEL, # Set to llama3.2:1b in your config
            base_url=OLLAMA_BASE_URL,
            temperature=0.0,  # Zero temp for consistent extraction
            format="json"  # Enforces JSON format
        )
        logger.info("SymptomExtractionAgent initialized with Ollama")

    def extract(self, patient_text: str, pdf_text: Optional[str] = None) -> List[ExtractedSymptom]:
        """
        Extract structured symptoms from patient input.

        Args:
            patient_text: Free-text symptom description from the user
            pdf_text: Optional extracted text from uploaded medical PDF

        Returns:
            List of ExtractedSymptom objects
        """
        if not patient_text.strip():
            return []

        # Combine inputs
        full_text = patient_text
        if pdf_text:
            full_text += f"\n\n[Medical Report Excerpt]:\n{pdf_text[:2000]}"  # Limit PDF text

        try:
            messages = [
                SystemMessage(content=self.SYSTEM_PROMPT),
                HumanMessage(content=f"Extract symptoms from this patient text:\n\n{full_text}"),
            ]

            response = self.llm.invoke(messages)
            raw = response.content.strip()
            print("\n🔍 RAW MODEL OUTPUT:\n", raw)
            # Strip markdown code blocks if present
            raw = re.sub(r"```json|```", "", raw).strip()

            symptoms_data = json.loads(raw)

            # 🔥 FIX 1: Handle single object
            if isinstance(symptoms_data, dict):
                # If wrapped like {"symptoms": [...]}
                for val in symptoms_data.values():
                    # We only care if it's a list AND if there's actually a dictionary item inside it
                    if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
                        symptoms_data = val
                        break
                else:
                    # If no valid symptom list found inside, assume the dict itself is the only symptom
                    symptoms_data = [symptoms_data]

            # 🔥 Handle case where model returns list of strings
            if isinstance(symptoms_data, list) and all(isinstance(x, str) for x in symptoms_data):
                symptoms_data = [{"name": x} for x in symptoms_data]

            symptoms = []
            for item in symptoms_data:
                symptom = ExtractedSymptom(
                    name=item.get("name", "").lower().strip(),
                    severity=item.get("severity"),
                    duration=item.get("duration"),
                    location=item.get("location"),
                    modifiers=item.get("modifiers", []),
                )
                if symptom.name:  # Skip empty names
                    symptoms.append(symptom)

            logger.info(f"Extracted {len(symptoms)} symptoms from patient text")
            return symptoms

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in symptom extraction: {e}")
            return self._fallback_extraction(patient_text)
        except Exception as e:
            logger.error(f"SymptomExtractionAgent error: {e}")
            return self._fallback_extraction(patient_text)

    def _fallback_extraction(self, text: str) -> List[ExtractedSymptom]:
        """
        Simple keyword-based fallback when LLM extraction fails.

        Args:
            text: Patient text

        Returns:
            Basic list of ExtractedSymptom objects
        """
        logger.warning("Using fallback keyword-based symptom extraction")

        COMMON_SYMPTOMS = [
            "fever", "cough", "headache", "fatigue", "nausea", "vomiting",
            "diarrhea", "chest pain", "shortness of breath", "sore throat",
            "runny nose", "body aches", "muscle pain", "joint pain",
            "dizziness", "rash", "sweating", "chills", "loss of appetite",
            "abdominal pain", "back pain", "swelling", "weakness",
        ]

        text_lower = text.lower()
        found = []
        for symptom in COMMON_SYMPTOMS:
            if symptom in text_lower:
                found.append(ExtractedSymptom(name=symptom))

        return found

    def get_symptom_names(self, symptoms: List[ExtractedSymptom]) -> List[str]:
        """Helper to extract just symptom names."""
        return [s.name for s in symptoms]
