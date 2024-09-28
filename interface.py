import argparse
import logging
from core import load_config, ensure_directory, setup_logging, query_qwen_vl_chat
from analysis import segment_video
from workflow import process_video_pipeline
import json
import csv
import os


def csv_to_json(csv_file, output_json_file, max_resolution='720p', max_fps=30):
    """Converts CSV to JSON with resolution and FPS limits.

Args:
    csv_file (Any): The input CSV file to be converted.
    output_json_file (Any): The output JSON file where the converted data will be saved.
    max_resolution (Any): The maximum resolution allowed for the video data.
    max_fps (Any): The maximum frames per second allowed for the video data.

Returns:
    Any: The result of the conversion process, which may include success status or error messages."""
    videos = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            video_data = {'file_name': row['file_name'], 'file_size': row[
                'file_size'], 'last_modified': row['last_modified'],
                'public_url': row['public_url'], 'segments': [],
                'max_resolution': max_resolution, 'max_fps': max_fps}
            videos.append(video_data)
    for video in videos:
        output_dir = os.path.join('segmented_videos', video['file_name'])
        segment_video(video['public_url'], output_dir, 15, video[
            'max_resolution'], video['max_fps'])
        for i in range(1, 999):
            segment_url = f"{video['public_url'][:-4]}_clip_{i:03d}.mp4"
            if os.path.exists(os.path.join(output_dir, f'clip_{i:03d}.mp4')):
                video['segments'].append(segment_url)
            else:
                break
    with open(output_json_file, 'w') as json_file:
        json.dump(videos, json_file, indent=2)
        print(f'JSON output successfully written to {output_json_file}')


def run_inference_on_videos(videos):
    """Runs inference on video segments, handling resolution and FPS.

Args:
    videos (Any): A collection of video segments on which inference will be performed.

Returns:
    Any: The results of the inference process, which may include predictions or analysis results."""
    all_results = []
    for video in videos:
        file_name = video['file_name']
        segment_results = []
        for segment_url in video['segments']:
            description = query_qwen_vl_chat(segment_url, instruction=
                'Describe this video segment.', max_resolution=video[
                'max_resolution'], max_fps=video['max_fps'])
            segment_results.append({'segment_url': segment_url,
                'description': description})
        all_results.append({'file_name': file_name, 'segments':
            segment_results})
    return all_results


def parse_arguments():
    """Parses command-line arguments provided by the user.

Returns:
    Namespace: Parsed command-line arguments, which can be accessed as attributes."""
    config = load_config()
    parser = argparse.ArgumentParser(description=
        'Comprehensive Video Processing Toolkit')
    default_output = config.get('Paths', 'ProcessedDirectory', fallback=
        'processed_videos/')
    default_scene_threshold = config.getfloat('SceneDetection',
        'DefaultThreshold', fallback=0.3)
    default_qwen_instruction = config.get('QwenVL', 'DefaultInstruction',
        fallback='Describe this video.')
    parser.add_argument('--urls', nargs='+', help=
        'List of video URLs to process')
    parser.add_argument('--csv', type=str, help=
        'Path to the CSV file containing video URLs and metadata')
    parser.add_argument('--config', type=str, help=
        'Path to the configuration file', default='config.ini')
    parser.add_argument('--output', type=str, help='Output directory',
        default=default_output)
    parser.add_argument('--log_level', type=str, help=
        'Set the logging level', choices=['DEBUG', 'INFO', 'WARNING',
        'ERROR', 'CRITICAL'], default='INFO')
    parser.add_argument('--scene_threshold', type=float, help=
        'Threshold for scene detection', default=default_scene_threshold)
    parser.add_argument('--qwen_instruction', type=str, help=
        'Instruction passed to Qwen-VL', default=default_qwen_instruction)
    parser.add_argument('--use_vpc', action='store_true', help=
        'Use the VPC endpoint for Qwen-VL API calls')
    args = parser.parse_args()
    if not args.urls and not args.csv:
        parser.error(
            'You must provide either --urls or --csv to indicate which videos to process.'
            )
    return args


def read_video_metadata_from_csv(csv_file):
    """Reads video metadata from a CSV file created with rclone.

Args:
    csv_file (str): Path to the CSV file containing video metadata.

Returns:
    list: A list of dictionaries containing video metadata (e.g., filename, file_size, public_url)."""
    videos = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        required_columns = ['file_name', 'file_size', 'last_modified',
            'public_url']
        for col in required_columns:
            if col not in reader.fieldnames:
                logging.error(
                    f"The CSV file must contain the following columns: {', '.join(required_columns)}"
                    )
                return []
        for row in reader:
            if row.get('public_url'):
                videos.append({'file_name': row.get('file_name'),
                    'file_size': row.get('file_size'), 'last_modified': row
                    .get('last_modified'), 'public_url': row.get('public_url')}
                    )
    return videos


def main():
    """Main function to handle video processing.

This function orchestrates the overall video processing workflow, including reading metadata, running inference, and converting formats.

Returns:
    Any: The outcome of the video processing, which may include success status or error messages."""
    args = parse_arguments()
    setup_logging(log_file='video_processing.log')
    logging.getLogger().setLevel(args.log_level)
    config = load_config(args.config)
    ensure_directory(args.output)
    if args.csv:
        logging.info(f'Reading videos from CSV file: {args.csv}')
        max_resolution = args.max_resolution or config.get('Processing',
            'MaxResolution', fallback='720p')
        max_fps = args.max_fps or config.getint('Processing', 'MaxFPS',
            fallback=30)
        csv_to_json(args.csv, 'videos_with_segments.json', max_resolution,
            max_fps)
        with open('videos_with_segments.json', 'r') as f:
            videos = json.load(f)
        inference_results = run_inference_on_videos(videos)
    else:
        videos = [{'public_url': url} for url in args.urls]
        for video_info in videos:
            video_url = video_info.get('public_url')
            filename = video_info.get('file_name', None)
            logging.info(f'Processing video: {filename} from URL: {video_url}')
            process_video_pipeline(video_url=video_url, scene_threshold=
                args.scene_threshold, custom_rules=None, output_dir=args.output
                )


if __name__ == '__main__':
    main()
