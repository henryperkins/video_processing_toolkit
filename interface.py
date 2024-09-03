import argparse
import logging
from core import load_config, setup_logging, ensure_directory

def parse_arguments():
    """Parses command-line arguments provided by the user."""
    config = load_config()  # Load configuration from the config.ini file
    
    parser = argparse.ArgumentParser(description='Comprehensive Video Processing Toolkit')

    # Set default values from the config file
    default_output = config.get('Paths', 'ProcessedDirectory', fallback='processed_videos/')
    default_scene_threshold = config.getfloat('SceneDetection', 'DefaultThreshold', fallback=0.3)
    default_tag_rules = config.get('Rules', 'CustomTagRules', fallback=None)
    
    parser.add_argument('--urls', nargs='+', help='List of video URLs to process', required=True)
    parser.add_argument('--config', type=str, help='Path to the configuration file', default='config.ini')
    parser.add_argument('--output', type=str, help='Output directory', default=default_output)
    parser.add_argument('--log_level', type=str, help='Set the logging level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO')
    
    # Additional Options
    parser.add_argument('--scene_threshold', type=float, help='Threshold for scene detection', default=default_scene_threshold)
    parser.add_argument('--tag_rules', type=str, help='Path to a custom tag rules file', default=default_tag_rules)

    logging.debug("Arguments parsed from command line.")
    return parser.parse_args()

def main():
    """Main function that initializes the CLI and coordinates the processing."""
    args = parse_arguments()

    # Setup logging with the chosen log level
    setup_logging(log_level=args.log_level)

    # Load configuration from the specified config file
    config = load_config(args.config)

    # Ensure output directory exists
    ensure_directory(args.output)

    # Example Process: Iterate over provided URLs and process each video
    for url in args.urls:
        logging.info(f"Processing video from URL: {url}")
        
        # Integrate other modules or workflows
        from workflow import process_video_pipeline  # Import here to avoid circular dependencies at the top
        process_video_pipeline(url)

if __name__ == '__main__':
    main()