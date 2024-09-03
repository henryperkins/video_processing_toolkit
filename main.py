from core import setup_logging, load_config, ensure_directory
from interface import parse_arguments
from workflow import process_video_pipeline
import logging
import os
import json

def main():
    """Main entry point for executing the video processing pipeline."""
    # Parse command-line arguments
    args = parse_arguments()

    # Set up logging with the specified log level
    setup_logging(log_file='video_processing.log')
    logging.getLogger().setLevel(args.log_level)  # Set to the specific log level provided in the CLI arguments

    # Load configuration from the specified Configuration File
    config = load_config(args.config)

    # Ensure output directory exists
    ensure_directory(args.output)

    # Load custom tagging rules if provided
    custom_rules = None
    if args.tag_rules:
        try:
            with open(args.tag_rules, 'r') as f:
                custom_rules = json.load(f)
            logging.info(f"Custom tagging rules loaded from {args.tag_rules}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Failed to load custom tagging rules: {e}")
            exit(1)

    # Iterate over provided URLs and process each video
    for url in args.urls:
        logging.info(f"Processing video from URL: {url}")
        process_video_pipeline(url, scene_threshold=args.scene_threshold, custom_rules=custom_rules)

if __name__ == '__main__':
    main()