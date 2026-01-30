"""
AI Newsletter - Main Entry Point
Runs the YouTube pipeline and generates daily digest
"""

import json
from src.utils.logger import setup_logging
from src.pipelines.youtube_pipeline import YouTubePipeline


def main():
    """Main execution function"""

    # Setup logging
    logger = setup_logging(log_level="INFO", log_dir="logs", console=True)

    logger.info("=" * 80)
    logger.info("AI NEWSLETTER - YOUTUBE PIPELINE")
    logger.info("=" * 80)

    try:
        # Initialize pipeline
        logger.info("\nInitializing pipeline...")
        pipeline = YouTubePipeline(config_path="src/config/config.yaml")

        # Run pipeline
        logger.info("Starting pipeline execution...\n")
        result = pipeline.run()

        # Display results
        print("\n" + "=" * 80)
        print("PIPELINE COMPLETE")
        print("=" * 80)
        print(f"\nDate: {result['date']}")
        print(f"Total Items: {len(result['items'])}")
        print("=" * 80)

        if result["items"]:
            print("\nGENERATED CONTENT:\n")
            for idx, item in enumerate(result["items"], 1):
                print(f"\n[{idx}] {item['title']}")
                print(f"    Type: {item['type']}")
                print(f"    Link: {item['link']}")
                print(f"    Summary:")
                print(f"    {item['summary']}")
                print("-" * 80)
        else:
            print("\n⚠ No new content found in the last 24 hours")

        # Save to file
        output_file = "daily_digest.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Results saved to: {output_file}")
        print("=" * 80 + "\n")

        return 0

    except Exception as e:
        logger.error(f"\n❌ Pipeline failed: {str(e)}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")
        print("Check logs for details.\n")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
