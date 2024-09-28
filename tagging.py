import logging
import json
import os


def load_custom_tags(custom_rules_path):
    """Loads custom tagging rules from a JSON file.

Args:
    custom_rules_path (Any): The path to the JSON file containing custom tagging rules.

Returns:
    Any: The content of the JSON file, which may include custom tagging rules or an error message if loading fails."""
    if not custom_rules_path or not os.path.isfile(custom_rules_path):
        logging.warning(f'Custom tag rules file {custom_rules_path} not found.'
            )
        return {}
    with open(custom_rules_path, 'r') as file:
        return json.load(file)


def apply_tags(video_info, custom_rules=None):
    """Applies tags to a video based on its metadata, AI-generated description, and custom rules.

Args:
    video_info (dict): A dictionary containing video metadata and AI-generated description.
    custom_rules (str or None): Path to the custom rules JSON file.

Returns:
    list: List of applied tags, which may include default tags and any additional tags defined in custom rules."""
    tags = []
    if 'resolution' in video_info and '4K' in video_info['resolution']:
        tags.append('High Resolution')
    if 'duration' in video_info and video_info['duration'] > 600:
        tags.append('Extended Play')
    if video_info.get('codec') == 'h264':
        tags.append('H.264 Codec')
    description = video_info.get('qwen_description', '').lower()
    if 'action' in description:
        tags.append('Action')
    if 'night shot' in description:
        tags.append('Night-time Filming')
    if custom_rules:
        custom_tags_rules = load_custom_tags(custom_rules)
        tags = apply_custom_rules(video_info, tags, custom_tags_rules)
    return list(set(tags))


def apply_custom_rules(video_info, tags, custom_tags_rules):
    """Applies custom rules provided in a JSON file to tag the video.

Args:
    video_info (dict): A dictionary containing video metadata and AI-generated descriptions.
    tags (list): List of already applied tags during the default rules processing.
    custom_tags_rules (dict): Dictionary of custom rules that specify how to modify or add tags.

Returns:
    list: Updated list of tags after applying custom rules, which may include modifications to existing tags or new tags added based on the custom rules."""
    rules = custom_tags_rules.get('rules', [])
    for rule in rules:
        if 'description_keywords' in rule:
            keywords = set(rule.get('description_keywords', []))
            if keywords.intersection(set(video_info.get('qwen_description',
                '').split())):
                tags.extend(rule.get('tags', []))
        if 'metadata_conditions' in rule:
            conditions = rule.get('metadata_conditions', {})
            resolution = video_info.get('resolution', '')
            duration = video_info.get('duration', 0)
            if conditions.get('resolution'
                ) == resolution and duration > conditions.get('duration_gt', 0
                ):
                tags.extend(rule.get('tags', []))
    return list(set(tags))


def classify_video(video_info):
    """Classifies a video into a high-level category based on its tags and metadata.

Args:
    video_info (dict): A dictionary containing tagged video metadata, which is used to determine the classification.

Returns:
    str: Classification of the video (e.g., "Action", "Documentary"), representing the high-level category the video belongs to."""
    tags = video_info.get('tags', [])
    if 'Action' in tags or 'High Intensity' in tags:
        return 'Action'
    if 'Documentary Footage' in tags or 'Narrative' in video_info.get(
        'qwen_description', '').lower():
        return 'Documentary'
    if 'Aerial Shot' in tags or 'Drone Footage' in tags:
        return 'Cinematic'
    return 'Unclassified'
