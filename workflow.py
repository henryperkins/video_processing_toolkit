import logging
from core import setup_logging, load_config, ensure_directory, query_qwen_vl_chat
from analysis import extract_metadata, detect_scenes
from tagging import apply_tags, classify_video
from export import export_to_json
import os
import requests
from tqdm import tqdm
from urllib.parse import urlparse

def process_video_pipeline(video_url, scene_threshold=None, custom_rules=None, output_dir=None):
    """
    Executes the full processing pipeline for a single video.

    Args:
        video_url (str): The URL of the video to process.
        scene_threshold (float or None): Threshold for scene detection.
        custom_rules (list or None): Custom tagging rules.
        output_dir (str or None): Directory path to save processed information.
    """
    config = load_config()  # Load configuration settings

    # Use defaults from config.ini if not provided via arguments
    scene_threshold = scene_threshold if scene_threshold is not None else config.getfloat('SceneDetection',
                                                                                         'DefaultThreshold',
                                                                                         fallback=0.3)
    output_dir = output_dir if output_dir is not None else config.get('Paths', 'ProcessedDirectory', fallback='processed_videos/')
    
    logging.info(f"Starting pipeline for video: {video_url}")
    ensure_directory(output_dir)  # Ensure the output directory exists

    # Create a filename based on the URL
    filename = os.path.basename(urlparse(video_url).path)

    # Download Video
    local_filepath = download_video(video_url, filename)
    
    if local_filepath:
        # Extract Metadata
        metadata = extract_metadata(local_filepath)
        if metadata:
            # Perform Scene Detection with the specified threshold
            scenes = detect_scenes(local_filepath, threshold=scene_threshold)

            # Process video using Qwen2-VL Chat Model via API
            instruction = config.get('QwenVL', 'DefaultInstruction', fallback="Describe this video.")
            qwen_description = query_qwen_vl_chat(video_url, instruction=instruction)

            # Aggregate metadata, scenes, and AI descriptions
            video_info = {**metadata, 'qwen_description': qwen_description, 'scenes': scenes}

            # Apply Tags and Classification with optional custom rules
            tags = apply_tags(video_info, custom_rules=custom_rules)
            classification = classify_video(video_info)

            # Update video information with tags and classification data
            video_info.update({
                'tags': tags,
                'classification': classification
            })

            logging.info(f"Video classified as {classification} with tags: {tags}")
            
            # Export the processed data to JSON in the specified output directory
            export_to_json(video_info, output_dir=output_dir)
        else:
            logging.error(f"Metadata extraction failed for {local_filepath}.")
    else:
        logging.error(f"Failed to download video from URL: {video_url}")


def download_video(url, filename):
    """Downloads a video and stores it in the specified directory.
    
    Args:
        url (str): The URL of the video to download.
        filename (str): The name to save the downloaded file as.
        
    Returns:
        str or None: The path to the downloaded file or None if the download failed.
    """
    config = load_config()  # Load configuration
    download_dir = config.get('Paths', 'DownloadDirectory', fallback='downloaded_videos')
    ensure_directory(download_dir)
    file_path = os.path.join(download_dir, filename)

    logging.info(f"Downloading video from {url}")

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(file_path, 'wb') as f, tqdm(
            total=int(response.headers.get('content-length', 0)),
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar:
            for data in response.iter_content(chunk_size=1024):
                size = f.write(data)
                progress_bar.update(size)
        
        logging.info(f"Video downloaded successfully: {filename}")
        return file_path
    except Exception as e:
        logging.error(f"Failed to download {url}: {e}", exc_info=True)
        return None