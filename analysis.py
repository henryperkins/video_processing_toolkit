import subprocess
import logging
import json
import os

def extract_metadata(filepath):
    """
    Extract video metadata using FFmpeg.

    Args:
        filepath (str): The path to the video file.

    Returns:
        dict: Extracted metadata like resolution, frame rate, codec, etc.
    """
    command = [
        'ffmpeg',
        '-i', filepath,
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams'
    ]
    try:
        output = subprocess.check_output(command)
        metadata = json.loads(output.decode('utf-8'))
        logging.info(f"Extracted metadata for {filepath}")
        return {
            'duration': float(metadata['format']['duration']),
            'bit_rate': int(metadata['format']['bit_rate']),
            'resolution': f"{metadata['streams'][0]['width']}x{metadata['streams'][0]['height']}",
            'frame_rate': metadata['streams'][0]['r_frame_rate'],
            'codec': metadata['streams'][0]['codec_name'],
            'size': os.path.getsize(filepath)
        }
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to extract metadata: {e}")
        return None


def detect_scenes(filepath, threshold=0.3):
    """
    Detect scene changes in a video file using FFmpeg's `select` filter.

    Args:
        filepath (str): The path to the video file.
        threshold (float): Threshold for detecting a scene change.
        
    Returns:
        list: A list of timestamps where scene changes occur.
    """
    command = [
        'ffmpeg',
        '-i', filepath,
        '-vf', f'select=\'gt(scene,{threshold})\',metadata=print:file=-',
        '-an',
        '-f', 'null',
        '-'
    ]
    
    scene_timestamps = []
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        for line in output.decode('utf-8').split('\n'):
            if 'pts_time:' in line:
                time_str = line.split('pts_time:')[1].split(' ')[0]
                scene_timestamps.append(float(time_str))
        logging.info(f"Detected {len(scene_timestamps)} scenes in {filepath}")
        return scene_timestamps
    except subprocess.CalledProcessError as e:
        logging.error(f"Scene detection failed: {e}")
        return []