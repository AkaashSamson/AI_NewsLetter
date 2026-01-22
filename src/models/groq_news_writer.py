"""
GroqNewsWriter Module
Role: Summarize content using Groq API via OpenAI Python client.
Uses llama-3.3-70b-versatile model for fast, efficient summarization.
"""

from typing import Dict, Any
import os
from dotenv import load_dotenv

try:
    from openai import OpenAI

    LLM_API_AVAILABLE = True
except ImportError:
    LLM_API_AVAILABLE = False

# Load environment variables
load_dotenv()


class GroqNewsWriter:
    """Summarizes news content using Groq API with OpenAI Python client."""

    # Available Groq models for text generation
    AVAILABLE_MODELS = {
        "mixtral-8x7b-32768": "Mixtral 8x7B - Balanced performance",
        "llama-3.3-70b-versatile": "Llama 3.3 70B - Best quality",
        "llama-3.1-70b-versatile": "Llama 3.1 70B - Fast & reliable",
    }

    def __init__(self, model: str = "llama-3.3-70b-versatile", api_key: str = None):
        """
        Initialize GroqNewsWriter with OpenAI client pointing to Groq API.

        Args:
            model: Groq model to use (default: llama-3.3-70b-versatile)
            api_key: Groq API key (uses env var GROQ_API_KEY if not provided)
        """
        if api_key is None:
            api_key = os.getenv("GROQ_API_KEY")

        if not api_key and LLM_API_AVAILABLE:
            raise ValueError(
                "Groq API key not provided or found in GROQ_API_KEY env var"
            )

        if not api_key:
            raise RuntimeError(
                "OpenAI client not installed. Install with: pip install openai"
            )

        self.model = model
        self.api_key = api_key

        # Initialize OpenAI client pointing to Groq API
        self.client = (
            OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            if LLM_API_AVAILABLE
            else None
        )

    def summarize(self, title: str, text: str, max_lines: int = 6) -> str:
        """
        Summarize content using Groq.

        Args:
            title: Content title
            text: Content text to summarize
            max_lines: Maximum lines in summary (default: 6)

        Returns:
            Summary text
        """
        if not LLM_API_AVAILABLE:
            raise RuntimeError(
                "OpenAI client not installed. Install with: pip install openai"
            )

        if not self.client:
            raise RuntimeError("LLM client not initialized")

        if not text or len(text.strip()) < 50:
            return "Content too short to summarize."

        prompt = f"""You are a professional news summarizer. Your task is to create a concise, neutral summary.

Title: {title}

Content:
{text}

Please provide a summary in exactly {max_lines} lines or fewer. 
- Use neutral, professional tone
- Preserve technical meaning and important details
- Do NOT mention sources or links
- Do NOT include URLs
- Be concise and clear

Summary:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=512,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional news summarizer. Create concise, accurate summaries without including URLs or sources.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                top_p=0.9,
            )

            summary = response.choices[0].message.content.strip()
            return summary

        except Exception as e:
            print(f"Error summarizing content: {e}")
            return f"Could not summarize. Error: {str(e)}"

    def process_content(self, title: str, text: str) -> Dict[str, Any]:
        """
        Process content and return title + summary.

        Args:
            title: Content title
            text: Content text

        Returns:
            Dict with 'title' and 'summary' keys
        """
        summary = self.summarize(title, text)

        return {"title": title, "summary": summary}

    @staticmethod
    def get_available_models() -> Dict[str, str]:
        """Get available Groq models."""
        return GroqNewsWriter.AVAILABLE_MODELS
