import subprocess
import logging
import csv
import json
import os
from core import query_qwen_vl_chat, ensure_directory
from moviepy.editor import VideoFileClip
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector


def segment_video(input_video, output_dir, segment_length=15,
    max_resolution='720p', max_fps=30):
    """Segments a video into smaller clips with specified resolution and FPS limits.

Args:
    input_video (str): Path to the input video file.
    output_dir (str): Directory to save the segmented clips.
    segment_length (int, optional): Length of each segment in seconds. Defaults to 15.
    max_resolution (str, optional): Maximum resolution for the output clips (e.g., "720p", "1080p"). Defaults to "720p".
    max_fps (int, optional): Maximum frame rate for the output clips. Defaults to 30.

Returns:
    Any: The result of the segmentation process, which may include information about the created segments or an error message if the process fails."""
    try:
        ensure_directory(output_dir)
        if max_resolution == '720p':
            scale_filter = (
                'scale=trunc(min(iw\\,1280)/2)*2:trunc(min(ih\\,720)/2)*2')
        elif max_resolution == '1080p':
            scale_filter = (
                'scale=trunc(min(iw\\,1920)/2)*2:trunc(min(ih\\,1080)/2)*2')
        else:
            scale_filter = (
                'scale=trunc(min(iw\\,1280)/2)*2:trunc(min(ih\\,720)/2)*2')
        command = ['ffmpeg', '-i', input_video, '-vf',
            f'{scale_filter},fps={max_fps}', '-c:v', 'libx264', '-c:a',
            'copy', '-f', 'segment', '-segment_time', str(segment_length),
            f'{output_dir}/clip_%03d.mp4']
        subprocess.run(command, check=True)
        logging.info(
            f"Video '{input_video}' segmented into {segment_length}-second clips."
            )
    except subprocess.CalledProcessError as e:
        logging.error(f'Error segmenting video: {e}')


def extract_metadata(filepath):
    """Extracts video metadata using FFmpeg.

Args:
    filepath (str): The path to the video file.

Returns:
    dict: A dictionary containing the extracted metadata, or None if extraction fails."""
    command = ['ffmpeg', '-i', filepath, '-v', 'quiet', '-print_format',
        'json', '-show_format', '-show_streams']
    try:
        output = subprocess.check_output(command)
        metadata = json.loads(output.decode('utf-8'))
        video_stream = None
        for stream in metadata['streams']:
            if stream['codec_type'] == 'video':
                video_stream = stream
                break
        if video_stream:
            logging.info(f'Extracted metadata for {filepath}')
            return {'duration': float(metadata['format']['duration']),
                'bit_rate': int(metadata['format']['bit_rate']),
                'resolution':
                f"{video_stream['width']}x{video_stream['height']}",
                'frame_rate': video_stream['r_frame_rate'], 'codec':
                video_stream['codec_name'], 'size': os.path.getsize(filepath)}
        else:
            logging.warning(f'No video stream found in {filepath}')
            return None
    except subprocess.CalledProcessError as e:
        logging.error(f'Failed to extract metadata: {e}')
        return None


def detect_scenes(filepath, threshold=30.0):
    """Detects scene changes in a video using the `scenedetect` library.

Args:
    filepath (str): The path to the video file.
    threshold (float, optional): Sensitivity threshold for scene detection. Defaults to 30.0.

Returns:
    list: A list of dictionaries, each containing the start and end time of a scene, or an empty list if no scenes are detected."""
    video_manager = VideoManager([filepath])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))
    video_manager.set_downscale_factor()
    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)
    scenes = scene_manager.get_scene_list()
    scene_list = [{'start_time': scene[0].get_seconds(), 'end_time': scene[
        1].get_seconds()} for scene in scenes]
    logging.info(f'Detected {len(scene_list)} scenes in {filepath}')
    return scene_list


def extract_scene_segment(video_path, start_time, end_time, output_dir=
    'scene_segments'):
    """Extracts a scene segment from a video using MoviePy.

Args:
    video_path (str): The path to the video file from which the segment will be extracted.
    start_time (float): The start time of the segment in seconds.
    end_time (float): The end time of the segment in seconds.
    output_dir (str): Directory where the extracted segment will be saved.

Returns:
    Any: The result of the extraction process, which may include information about the created segment or an error message if the process fails."""
    ensure_directory(output_dir)
    filename = os.path.basename(video_path).split('.')[0]
    segment_path = os.path.join(output_dir,
        f'{filename}_{start_time:.2f}-{end_time:.2f}.mp4')
    try:
        video = VideoFileClip(video_path)
        segment = video.subclip(start_time, end_time)
        segment.write_videofile(segment_path, codec='libx264', audio_codec=
            'aac')
        video.close()
        logging.info(f'Extracted scene segment: {segment_path}')
        return segment_path
    except Exception as e:
        logging.error(f'Error extracting scene segment: {e}')
        return None
