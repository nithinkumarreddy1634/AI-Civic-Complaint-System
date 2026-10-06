"""
Google AI Studio (Gemini) Service Integration.

Provides optional generative multimodal analysis, natural language complaint summarization,
and decision-support explainability when GOOGLE_API_KEY is configured.
Falls back gracefully to local heuristic/rule-based engine when API key is unset or offline.
"""
import logging
from typing import Optional, Dict, Any
from app.config import get_settings

logger = logging.getLogger("civicai.gemini")

class GeminiService:
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.GOOGLE_API_KEY
        self._client = None
        self._init_client()

    def _init_client(self):
        if not self.api_key:
            logger.info("GOOGLE_API_KEY not configured. Using local AI engine fallback.")
            return

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._client = genai.GenerativeModel("gemini-1.5-flash")
            logger.info("Google AI Studio (Gemini 1.5 Flash) initialized successfully.")
        except Exception as e:
            logger.warning(f"Failed to initialize Google Generative AI client: {e}")
            self._client = None

    @property
    def is_available(self) -> bool:
        return self._client is not None

    async def summarize_complaint(self, description: str, category: str) -> Dict[str, Any]:
        """
        Summarizes complaint description and extracts urgency insights via Gemini.
        """
        if not self.is_available:
            return {
                "summary": description[:100] + "..." if len(description) > 100 else description,
                "urgency_insight": "Standard heuristic evaluation applied.",
                "source": "local_fallback"
            }

        prompt = (
            f"Analyze this civic infrastructure complaint.\n"
            f"Category: {category}\n"
            f"Description: {description}\n\n"
            f"Provide a 1-sentence concise executive summary and assess immediate public hazard risk."
        )

        try:
            response = self._client.generate_content(prompt)
            return {
                "summary": response.text.strip(),
                "urgency_insight": "AI Studio multi-modal insight generated.",
                "source": "gemini-1.5-flash"
            }
        except Exception as e:
            logger.warning(f"Gemini API request failed: {e}. Falling back to local.")
            return {
                "summary": description[:100] + "..." if len(description) > 100 else description,
                "urgency_insight": "Local rule-based fallback.",
                "source": "local_fallback"
            }

_gemini_service = None

def get_gemini_service() -> GeminiService:
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
