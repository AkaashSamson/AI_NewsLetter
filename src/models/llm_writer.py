import os
import yaml
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from openai import OpenAI
from src.schemas.youtube import VideoSummary
import google.generativeai as genai
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
        logger.info(f"    Temperature: {self.temperature}")
        logger.info(f"    Max tokens: {self.max_tokens}")
        logger.info(f"    Input length: {len(text)} chars")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            summary = response.choices[0].message.content.strip()
            logger.info(f"  ✓ Summary generated: {len(summary)} chars")
            logger.info(
                f"    Tokens used: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}"
            )
            return summary
        except Exception as e:
            logger.error(f"  ✗ Groq API error: {str(e)}")
            return f"Error during Groq summarization: {str(e)}"


class GeminiProvider(LLMProvider):
    def __init__(self, config: Dict[str, Any]):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=self.api_key)
        self.model_name = config.get("model", "gemini-1.5-pro")
        self.temperature = config.get("temperature", 0.5)
        self.max_tokens = config.get("max_tokens", 2048)
        self.model = genai.GenerativeModel(self.model_name)

    def generate_summary(self, title: str, text: str) -> str:
        prompt = f"Summarize this technical AI content concisely:\nTitle: {title}\nContent: {text}"
        logger.info(f"  Calling Gemini API...")
        logger.info(f"    Model: {self.model_name}")
        logger.info(f"    Temperature: {self.temperature}")
        logger.info(f"    Max tokens: {self.max_tokens}")
        logger.info(f"    Input length: {len(text)} chars")

        try:
            generation_config = genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            )
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            summary = response.text.strip()
            logger.info(f"  ✓ Summary generated: {len(summary)} chars")
            return summary
        except Exception as e:
            logger.error(f"  ✗ Gemini API error: {str(e)}")
            return f"Error during Gemini summarization: {str(e)}"


class LLMWriter:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, "r") as f:
            full_config = yaml.safe_load(f)

        provider_name = full_config["llm"]["provider"]
        specific_config = full_config["llm"][provider_name]

        if provider_name == "groq":
            self.provider = GroqProvider(specific_config)
        elif provider_name == "gemini":
            self.provider = GeminiProvider(specific_config)
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")

    def process_content(self, title: str, text: str) -> VideoSummary:
        summary = self.provider.generate_summary(title, text)
        return VideoSummary(title=title, summary=summary)


if __name__ == "__main__":
    # Test the Groq LLM
    writer = LLMWriter(config_path="src/config/config.yaml")

    test_title = "GPT-4 Breakthrough in Reasoning"
    test_text = """
    OpenAI has announced a significant breakthrough in GPT-4's reasoning capabilities.
    The model now demonstrates improved performance on complex multi-step problems,
    showing better logical consistency and error detection. Benchmarks indicate a 25%
    improvement in mathematical reasoning tasks compared to previous versions.
    """
    result = writer.process_content(test_title, test_text)

    print("=" * 60)
    print(f"Title: {result['title']}")
    print("=" * 60)
    print(f"Summary:\n{result['summary']}")
    print("=" * 60)
