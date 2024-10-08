import logging
from core import setup_logging, load_config, ensure_directory, query_qwen_vl_chat, QwenVLModel
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
    """Checks if a given URL directly links to a video file.

Args:
    url (Any): The URL to check. This can be a string or any type that can be converted to a string.

Returns:
    Any: True if the URL is a direct video link, False otherwise. The return type can vary based on the implementation, but typically it will be a boolean value."""
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv',
        '.webm', '.ogg']
    if any(url.endswith(ext) for ext in video_extensions):
        return True
    try:
        response = requests.head(url, allow_redirects=True)
        content_type = response.headers.get('Content-Type', '')
        if 'video' in content_type:
            return True
    except requests.RequestException as e:
        logging.error(f'Failed to check URL content type: {e}')
    return False


def extract_video_url_from_html(html_content):
    """Extracts a video URL from HTML content.

Args:
    html_content (Any): The HTML content to parse. This can be a string or any type that can be processed as HTML.

Returns:
    Any: The extracted video URL as a string, or None if no URL is found. The return type may vary based on the implementation, but typically it will be a string or None."""
    soup = BeautifulSoup(html_content, 'html.parser')
    video_tag = soup.find('video')
    if video_tag:
        video_url = video_tag.get('src')
        if video_url:
            return video_url
    source_tag = soup.find('source')
    if source_tag:
        video_url = source_tag.get('src')
        if video_url:
            return video_url
    patterns = [
        '(?:"|\\\')((http[s]?:\\/\\/.*?\\.mp4|\\.mkv|\\.webm|\\.ogg))(?:\\"|\\\')'
        , '(?:"|\\\')((http[s]?:\\/\\/.*?video.*?))(?:\\"|\\\')']
    for pattern in patterns:
        match = re.search(pattern, html_content)
        if match:
            return match.group(1)
    return None


def download_video(url, filename):
    """Downloads a video from a URL and saves it to a file.

Args:
    url (Any): The URL of the video to download. This should be a string representing a valid video URL.
    filename (Any): The name to save the video as. This should be a string representing the desired file name, including the file extension.

Returns:
    Any: The path to the downloaded video file as a string, or None if the download fails. The return type may vary based on the implementation, but typically it will be a string or None."""
    config = load_config()
    download_dir = config.get('Paths', 'DownloadDirectory', fallback=
        'downloaded_videos')
    ensure_directory(download_dir)
    file_path = os.path.join(download_dir, filename)
    logging.info(f'Checking if URL {url} is a direct video link')
    if is_video_url(url):
        logging.info(f'URL is a direct video link, downloading from {url}')
        direct_url = url
    else:
        logging.info(
            f'URL {url} is not a direct video link, attempting to scrape the page for videos.'
            )
        try:
            response = requests.get(url)
            response.raise_for_status()
            if 'html' in response.headers.get('Content-Type', ''):
                direct_url = extract_video_url_from_html(response.text)
                if not direct_url:
                    logging.error(
                        f'Could not find a video link in the provided URL: {url}'
                        )
                    return None
            else:
                logging.error(
                    f'Content from URL {url} does not appear to be HTML.')
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f'Error during request: {e}')
            return None
    try:
        response = requests.get(direct_url, stream=True)
        response.raise_for_status()
        with open(file_path, 'wb') as f, tqdm(total=int(response.headers.
            get('content-length', 0)), unit='iB', unit_scale=True,
            unit_divisor=1024) as progress_bar:
            for data in response.iter_content(chunk_size=1024):
                size = f.write(data)
                progress_bar.update(size)
        logging.info(f'Video downloaded successfully: {filename}')
        return file_path
    except Exception as e:
        logging.error(f'Failed to download video: {e}', exc_info=True)
        return None


def process_video_pipeline(video_url, scene_threshold=None, custom_rules=
    None, output_dir=None):
    """Executes the full processing pipeline for a single video.

Args:
    video_url (Any): The URL of the video to process. This can be a string or any type that can be converted to a string.
    scene_threshold (Any): A threshold value used for scene detection. The type can vary based on the implementation, typically a float or integer.
    custom_rules (Any): Custom processing rules that may be applied during the video processing. This could be a dictionary or any other structure depending on the rules defined.
    output_dir (Any): The directory where the processed video will be saved. This should be a string representing a valid directory path.

Returns:
    Any: The result of the processing pipeline, which could vary based on the implementation. Typically, it may return a status message, a path to the output file, or None if processing fails."""
    config = load_config()
    scene_threshold = (scene_threshold if scene_threshold is not None else
        config.getfloat('SceneDetection', 'DefaultThreshold', fallback=0.3))
    output_dir = output_dir if output_dir is not None else config.get('Paths',
        'ProcessedDirectory', fallback='processed_videos/')
    logging.info(f'Starting pipeline for video: {video_url}')
    ensure_directory(output_dir)
    filename = os.path.basename(urlparse(video_url).path)
    local_filepath = download_video(video_url, filename)
    if local_filepath:
        metadata = extract_metadata(local_filepath)
        if metadata:
            scenes = detect_scenes(local_filepath, threshold=scene_threshold)
            qwen_model = QwenVLModel()
            qwen_description = qwen_model.process_video(local_filepath,
                metadata)
            video_info = {**metadata, 'qwen_description': qwen_description,
                'scenes': scenes}
            tags = apply_tags(video_info, custom_rules=custom_rules)
            classification = classify_video(video_info)
            video_info.update({'tags': tags, 'classification': classification})
            logging.info(
                f'Video classified as {classification} with tags: {tags}')
            export_to_json(video_info, output_dir=output_dir)
        else:
            logging.error(f'Metadata extraction failed for {local_filepath}.')
    else:
        logging.error(f'Failed to download video from URL: {video_url}')
