import os
import yaml
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from openai import OpenAI
from src.schemas.youtube import VideoSummary
from src.config.settings import settings
# import google.generativeai as genai  <-- Commented out processed by request
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    @abstractmethod
    def generate_summary(self, title: str, text: str) -> str:
        pass


class GroqProvider(LLMProvider):
    def __init__(self, config: Dict[str, Any]):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment")

        self.model = config.get("model")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 1024)
        self.client = OpenAI(
            api_key=self.api_key, base_url="https://api.groq.com/openai/v1"
        )

    def generate_summary(self, title: str, text: str) -> str:
        prompt = f"Summarize this technical AI content concisely:\nTitle: {title}\nContent: {text}"
        logger.info(f"  Calling Groq API...")
        logger.info(f"    Model: {self.model}")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            summary = response.choices[0].message.content.strip()
            logger.info(f"  ✓ Summary generated: {len(summary)} chars")
            return summary
        except Exception as e:
            logger.error(f"  ✗ Groq API error: {str(e)}")
            return f"Error during Groq summarization: {str(e)}"

# Commented out Gemini Provider to avoid dependency issues
# class GeminiProvider(LLMProvider):
#     def __init__(self, config: Dict[str, Any]):
#         self.api_key = os.getenv("GEMINI_API_KEY")
#         ...

class OllamaProvider(LLMProvider):
    """
    Local LLM Provider using Ollama (OpenAI Compatible API).
    """
    def __init__(self, config: Dict[str, Any] = None):
        # We can pull from settings directly, or use config dict if provided
        self.base_url = settings.OLLAMA_BASE_URL
        self.model_name = settings.OLLAMA_MODEL
        
        # Override with config if present
        if config:
            self.model_name = config.get("model", self.model_name)
            self.base_url = config.get("base_url", self.base_url)

        self.client = OpenAI(
            base_url=self.base_url,
            api_key="ollama", # required but ignored
        )
        logger.info(f"Initialized Ollama Provider (URL: {self.base_url}, Model: {self.model_name})")

    def generate_summary(self, title: str, text: str) -> str:
        prompt = f"Summarize this technical AI content concisely:\nTitle: {title}\nContent: {text}"
        logger.info(f"  Calling Ollama ({self.model_name})...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
            )
            summary = response.choices[0].message.content.strip()
            logger.info(f"  ✓ Summary generated: {len(summary)} chars")
            return summary
        except Exception as e:
            logger.error(f"  ✗ Ollama API error: {str(e)}")
            # Fallback or re-raise?
            return f"Error during Ollama summarization: {str(e)}"


class LLMWriter:
    def __init__(self, config_path: str = "src/config/config.yaml"):
        # We prioritize Ollama if configured, or check config.yaml
        # For this refactor, we just default to Ollama if not specified
        
        # Simple logic: If we are here, user wants Ollama (based on conversation)
        # But let's keep it somewhat dynamic
        
        try:
            with open(config_path, "r") as f:
                full_config = yaml.safe_load(f)
            provider_name = full_config.get("llm", {}).get("provider", "ollama")
            specific_config = full_config.get("llm", {}).get(provider_name, {})
        except FileNotFoundError:
            # Fallback if config file missing
            provider_name = "ollama"
            specific_config = {}

        if provider_name == "ollama":
            self.provider = OllamaProvider(specific_config)
        elif provider_name == "groq":
            self.provider = GroqProvider(specific_config)
        # elif provider_name == "gemini":
        #     self.provider = GeminiProvider(specific_config)
        else:
             # Default fallback to Ollama if unknown
            logger.warning(f"Unknown provider '{provider_name}', falling back to Ollama")
            self.provider = OllamaProvider(specific_config)

    def process_content(self, title: str, text: str) -> VideoSummary:
        summary = self.provider.generate_summary(title, text)
        return VideoSummary(title=title, summary=summary)


if __name__ == "__main__":
    # Test
    writer = LLMWriter()
    test_title = "Ollama Test"
    test_text = "This is a test content to verify if local Ollama instance is working correctly with the new provider implementation."
    result = writer.process_content(test_title, test_text)
    print(f"Summary: {result.summary}")
