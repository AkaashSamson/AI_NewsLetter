"""
LLMWriter Module
Role: Summarize content using configurable LLM providers.
Uses factory pattern to support multiple LLM backends (Groq, Anthropic, OpenAI, etc.)

Current Implementation: Groq API via OpenAI Python client
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

try:
    from openai import OpenAI

    LLM_API_AVAILABLE = True
except ImportError:
    LLM_API_AVAILABLE = False

# Load environment variables
load_dotenv()


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 512,
        temperature: float = 0.7,
        **kwargs,
    ) -> str:
        """
        Generate a completion from the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated text completion
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Get the current model name."""
        pass


class GroqProvider(LLMProvider):
    """Groq LLM provider implementation using OpenAI Python client."""

    # Available Groq models
    AVAILABLE_MODELS = {
        "mixtral-8x7b-32768": "Mixtral 8x7B - Balanced performance",
        "llama-3.3-70b-versatile": "Llama 3.3 70B - Best quality",
        "llama-3.1-70b-versatile": "Llama 3.1 70B - Fast & reliable",
    }

    def __init__(self, api_key: str = None, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize Groq provider.

        Args:
            api_key: Groq API key (uses GROQ_API_KEY env var if not provided)
            model: Model to use (default: llama-3.3-70b-versatile)
        """
        if not LLM_API_AVAILABLE:
            raise RuntimeError(
                "OpenAI client not installed. Install with: pip install openai"
            )

        if api_key is None:
            api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "Groq API key not provided or found in GROQ_API_KEY env var"
            )

        self.api_key = api_key
        self.model = model

        # Initialize OpenAI client pointing to Groq API
        self.client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 512,
        temperature: float = 0.7,
        **kwargs,
    ) -> str:
        """Generate completion using Groq API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=kwargs.get("top_p", 0.9),
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"Groq API error: {str(e)}")

    def get_model_name(self) -> str:
        """Get current model name."""
        return self.model

    @staticmethod
    def get_available_models() -> Dict[str, str]:
        """Get available Groq models."""
        return GroqProvider.AVAILABLE_MODELS


class LLMWriter:
    """
    Factory-based LLM writer for content summarization.
    Supports multiple LLM providers through abstraction layer.
    """

    # Supported providers
    SUPPORTED_PROVIDERS = ["groq"]

    def __init__(
        self,
        provider: str = "groq",
        model: str = None,
        api_key: str = None,
        **provider_config,
    ):
        """
        Initialize LLMWriter with specified provider.

        Args:
            provider: LLM provider to use ("groq", future: "anthropic", "openai")
            model: Model name (provider-specific, uses default if not provided)
            api_key: API key for provider (uses env var if not provided)
            **provider_config: Additional provider-specific configuration
        """
        self.provider_name = provider
        self.provider = self._create_provider(
            provider, model, api_key, **provider_config
        )

    def _create_provider(
        self, provider_name: str, model: str = None, api_key: str = None, **config
    ) -> LLMProvider:
        """
        Factory method to create appropriate LLM provider.

        Args:
            provider_name: Name of provider ("groq", etc.)
            model: Model name
            api_key: API key
            **config: Additional configuration

        Returns:
            Initialized LLMProvider instance
        """
        if provider_name == "groq":
            kwargs = {"api_key": api_key}
            if model:
                kwargs["model"] = model
            return GroqProvider(**kwargs, **config)

        # Future providers can be added here:
        # elif provider_name == "anthropic":
        #     return AnthropicProvider(api_key=api_key, model=model, **config)
        # elif provider_name == "openai":
        #     return OpenAIProvider(api_key=api_key, model=model, **config)

        else:
            raise ValueError(
                f"Unsupported provider: {provider_name}. "
                f"Supported providers: {', '.join(self.SUPPORTED_PROVIDERS)}"
            )

    def summarize(self, title: str, text: str, max_lines: int = 6) -> str:
        """
        Summarize content using configured LLM provider.

        Args:
            title: Content title
            text: Content text to summarize
            max_lines: Maximum lines in summary (default: 6)

        Returns:
            Summary text
        """
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

        messages = [
            {
                "role": "system",
                "content": "You are a professional news summarizer. Create concise, accurate summaries without including URLs or sources.",
            },
            {"role": "user", "content": prompt},
        ]

        try:
            summary = self.provider.generate_completion(
                messages=messages, max_tokens=512, temperature=0.7
            )
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

    def get_provider_info(self) -> Dict[str, str]:
        """Get information about current provider and model."""
        return {"provider": self.provider_name, "model": self.provider.get_model_name()}

    @staticmethod
    def get_supported_providers() -> List[str]:
        """Get list of supported LLM providers."""
        return LLMWriter.SUPPORTED_PROVIDERS


if __name__ == "__main__":
    import json
    
    # Test the factory pattern with Groq provider
    print("Testing LLMWriter with factory pattern...\n")
    
    # Initialize with Groq (default)
    writer = LLMWriter(provider="groq", model="llama-3.3-70b-versatile")
    
    # Display provider info
    provider_info = writer.get_provider_info()
    print(f"Provider: {provider_info['provider']}")
    print(f"Model: {provider_info['model']}\n")
    
    # Test summarization
    test_title = "The Future of Artificial Intelligence"
    test_text = """
    Artificial intelligence continues to evolve rapidly, with new breakthroughs in natural language 
    processing, computer vision, and machine learning. Large language models like GPT-4 and Claude 
    have demonstrated remarkable capabilities in understanding and generating human-like text. 
    Meanwhile, researchers are exploring more efficient training methods, ethical AI development, 
    and ways to make AI systems more interpretable and trustworthy. The industry is also seeing 
    increased focus on AI safety and alignment, ensuring these powerful systems benefit humanity.
    """
    
    print("Generating summary...")
    result = writer.process_content(test_title, test_text)
    
    print("\nResult:")
    print(json.dumps(result, indent=2))
    
    print(f"\nSupported providers: {', '.join(LLMWriter.get_supported_providers())}")
