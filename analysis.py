import ffmpeg
import logging
import os
from core import load_config

def extract_metadata(filepath):
    """Extracts enhanced video metadata using ffmpeg."""
    logging.debug(f"Extracting metadata for file: {filepath}")
    try:
        probe = ffmpeg.probe(filepath)
        metadata = {}

        video_info = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
        if video_info:
            metadata.update({
                'duration': float(probe['format']['duration']),
                'codec': video_info.get('codec_name'),
                'width': video_info.get('width'),
                'height': video_info.get('height'),
                'fps': eval(video_info['avg_frame_rate']),
            })
        audio_info = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
        if audio_info:
            metadata.update({
                'audio_codec': audio_info.get('codec_name'),
                'audio_channels': audio_info.get('channels'),
                'audio_sample_rate': audio_info.get('sample_rate'),
            })
        subtitle_info = next((s for s in probe['streams'] if s['codec_type'] == 'subtitle'), None)
        if subtitle_info:
            metadata['has_subtitle'] = True
        else:
            metadata['has_subtitle'] = False

        return metadata
    except Exception as e:
        logging.error(f"Error extracting metadata from {filepath}: {e}", exc_info=True)
        return None

def detect_scenes(filepath, threshold=0.3):
    """Detect scenes in the video and return a list of timestamps."""
    logging.debug(f"Detecting scenes for file: {filepath}")
    try:
        scenes = []
        ffmpeg_command = (
            ffmpeg
            .input(filepath)
            .filter('select', f'gt(scene,{threshold})')
            .output('dummy', vf='showinfo', format='null')
        )

        ffmpeg_output = ffmpeg_command.run(capture_stderr=True)[1]
        for line in ffmpeg_output.splitlines():
            if 'pts_time' in line:
                timestamp = line.split('pts_time:')[1].split(' ')[0]
                scenes.append(float(timestamp))

        logging.info(f"Detected {len(scenes)} scenes in {filepath}")
        return scenes
    except Exception as e:
        logging.error(f"Error during scene detection in {filepath}: {e}")
        return []

class QwenVLProcessor:
    def __init__(self, model_dir):
        self.config = load_config()
        # Load model here
        self.template_file = self.config.get('QwenVL', 'TemplateFile', fallback='templates.txt')
        self.load_templates()
    
    def load_templates(self):
        """Load processing templates from configuration."""
        self.templates = []
        with open(self.template_file, 'r') as f:
            self.templates = [line.strip() for line in f if line.strip()]

    def process_video(self, video_path):
        """Process video with multiple questions from the Qwen-VL model."""
        results = {}
        for question in self.templates:
            logging.debug(f"Processing video {video_path} with question: {question}")
            result = self._ask_model(video_path, question)  # "_ask_model" is a placeholder for actual processing logic
            results[question] = result

        return results
    
    def _ask_model(self, video_path, question):
        """Wrapper for interacting with the actual model (Placeholder)."""
        return "Generated description based on question: " + question