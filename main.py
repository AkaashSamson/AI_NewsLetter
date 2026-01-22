"""
AI Newsletter - Main Entry Point
Daily Intelligence Agent with Groq LLM Integration
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def main():
    """Main entry point for the AI Newsletter system."""

    print("\n" + "=" * 80)
    print("AI NEWSLETTER - DAILY INTELLIGENCE AGENT")
    print("Powered by Groq LLM")
    print("=" * 80 + "\n")

    try:
        # Get configuration from environment
        groq_api_key = os.getenv("GROQ_API_KEY")
        youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        output_path = os.getenv("OUTPUT_JSON_PATH", "daily_digest.json")
        sources_csv = os.getenv("SOURCES_CSV_PATH", "youtube_sources.csv")

        # Validate required keys
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")

        if not youtube_api_key:
            raise ValueError("YOUTUBE_API_KEY not found in .env file")

        if not os.path.exists(sources_csv):
            raise FileNotFoundError(f"YouTube sources file not found: {sources_csv}")

        print(f"Configuration:")
        print(f"  Groq Model: {groq_model}")
        print(f"  Sources CSV: {sources_csv}")
        print(f"  Output File: {output_path}")
        print()

        # Import pipeline
        from src.pipelines import main_youtube_pipeline

        # Run pipeline
        print("[PHASE 1] Processing YouTube Sources...")
        print("-" * 80)

        result = main_youtube_pipeline(
            youtube_api_key=youtube_api_key,
            groq_api_key=groq_api_key,
            groq_model=groq_model,
            output_file=output_path,
            sources_file=sources_csv,
        )

        # Display results
        print("-" * 80)
        print("\n✓ Pipeline Completed Successfully!\n")
        print(f"Results:")
        print(f"  Date: {result.get('date', 'N/A')}")
        print(f"  Items Generated: {result.get('count', 0)}")
        print(f"  Output File: {output_path}")
        print()
        print("=" * 80 + "\n")

        return 0

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}\n")
        print("Setup required:")
        print("  1. Create/verify .env file with:")
        print("     GROQ_API_KEY=your_groq_key")
        print("     YOUTUBE_API_KEY=your_youtube_key")
        print("  2. Ensure youtube_sources.csv exists")
        print()
        return 1

    except FileNotFoundError as e:
        print(f"\n❌ File Error: {e}\n")
        print("Please ensure all required files exist")
        print()
        return 1

    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        print("Check docs/TROUBLESHOOTING.md for common issues")
        print()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
