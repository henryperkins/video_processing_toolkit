import logging
from core import setup_logging, load_config, ensure_directory, query_qwen_vl_chat
from analysis import extract_metadata, detect_scenes
from tagging import apply_tags, classify_video
from export import export_to_json
import os
import requests
from tqdm import tqdm
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re

def is_video_url(url):
    """Check if the URL directly links to a video file based on its extension or the headers."""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.ogg']
    if any(url.endswith(ext) for ext in video_extensions):
        return True

    try:
        response = requests.head(url, allow_redirects=True)
        content_type = response.headers.get('Content-Type', '')
        if 'video' in content_type:
            return True
    except requests.RequestException as e:
        logging.error(f"Failed to check URL content type: {e}")

    return False

def extract_video_url_from_html(html_content):
    """Scrape HTML content to find a likely video URL."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Look for <video> tags
    video_tag = soup.find('video')
    if video_tag:
        video_url = video_tag.get('src')
        if video_url:
            return video_url

    # Look for <source> tags under <video> or standalone <source>
    source_tag = soup.find('source')
    if source_tag:
        video_url = source_tag.get('src')
        if video_url:
            return video_url

    # Look for URLs in embedded JS or other sources
    patterns = [
        r'(?:"|\')((http[s]?:\/\/.*?\.mp4|\.mkv|\.webm|\.ogg))(?:\"|\')',
        r'(?:"|\')((http[s]?:\/\/.*?video.*?))(?:\"|\')'
    ]

    for pattern in patterns:
        match = re.search(pattern, html_content)
        if match:
            return match.group(1)

    return None

def download_video(url, filename):
    """Downloads a video and stores it in the specified directory."""
    config = load_config()
    download_dir = config.get('Paths', 'DownloadDirectory', fallback='downloaded_videos')
    ensure_directory(download_dir)
    file_path = os.path.join(download_dir, filename)

    logging.info(f"Checking if URL {url} is a direct video link")

    if is_video_url(url):
        logging.info(f"URL is a direct video link, downloading from {url}")
        direct_url = url
    else:
        logging.info(f"URL {url} is not a direct video link, attempting to scrape the page for videos.")
        response = requests.get(url)
        if 'html' in response.headers.get('Content-Type', ''):
            direct_url = extract_video_url_from_html(response.text)
            if not direct_url:
                logging.error(f"Could not find a video link in the provided URL: {url}")
                return None
        else:
            logging.error(f"Content from URL {url} does not appear to be HTML.")
            return None

    try:
        response = requests.get(direct_url, stream=True)
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
        logging.error(f"Failed to download video: {e}", exc_info=True)
        return None

def process_video_pipeline(video_url, scene_threshold=None, custom_rules=None, output_dir=None):
    """Executes the full processing pipeline for a single video."""
    config = load_config()

    scene_threshold = scene_threshold if scene_threshold is not None else config.getfloat('SceneDetection',
                                                                                         'DefaultThreshold',
                                                                                         fallback=0.3)
    output_dir = output_dir if output_dir is not None else config.get('Paths', 'ProcessedDirectory', fallback='processed_videos/')
    
    logging.info(f"Starting pipeline for video: {video_url}")
    ensure_directory(output_dir)

    # Create a filename based on the URL
    filename = os.path.basename(urlparse(video_url).path)

    # Download the Video
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

            # Apply Tags and Classification
            tags = apply_tags(video_info, custom_rules=custom_rules)
            classification = classify_video(video_info)

            # Update video information with tags and classification
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