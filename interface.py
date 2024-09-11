import argparse
import logging
from core import load_config, ensure_directory, setup_logging
from workflow import process_video_pipeline

def parse_arguments():
    """
    Parses command-line arguments provided by the user.

    Returns:
        Namespace: Parsed command-line arguments.
    """
    config = load_config()  # Load configuration from the config.ini file

    parser = argparse.ArgumentParser(description='Comprehensive Video Processing Toolkit')

    # Set default values from the config file
    default_output = config.get('Paths', 'ProcessedDirectory', fallback='processed_videos/')
    default_scene_threshold = config.getfloat('SceneDetection', 'DefaultThreshold', fallback=0.3)
    default_qwen_instruction = config.get('QwenVL', 'DefaultInstruction', fallback="Describe this video.")
    
    parser.add_argument('--urls', nargs='+', help='List of video URLs to process', required=True)
    parser.add_argument('--config', type=str, help='Path to the configuration file', default='config.ini')
    parser.add_argument('--output', type=str, help='Output directory', default=default_output)
    parser.add_argument('--log_level', type=str, help='Set the logging level',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO')
    
    # Processing options
    parser.add_argument('--scene_threshold', type=float, help='Threshold for scene detection', default=default_scene_threshold)
    parser.add_argument('--qwen_instruction', type=str, help='Instruction passed to Qwen-VL', default=default_qwen_instruction)
    parser.add_argument('--use_vpc', action='store_true', help='Use the VPC endpoint for Qwen-VL API calls')

    args = parser.parse_args()
    return args

def main():
    """Main function that initializes the CLI and coordinates the processing."""
    args = parse_arguments()

    # Setup logging with the specified log level
    setup_logging(log_file='video_processing.log')
    logging.getLogger().setLevel(args.log_level)  # Set to the specific log level provided in the CLI arguments

    # Load configuration from the specified config file
    config = load_config(args.config)

    # Ensure output directory exists
    ensure_directory(args.output)

    # Iterate over provided URLs and process each video
    for url in args.urls:
        logging.info(f"Processing video from URL: {url}")
        
        # Run the full processing pipeline for the video
        process_video_pipeline(
            video_url=url,
            scene_threshold=args.scene_threshold,
            custom_rules=None,  # Optional: load custom rules if needed
            output_dir=args.output
        )

if __name__ == '__main__':
    main()