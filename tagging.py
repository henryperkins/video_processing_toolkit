import logging
import json
import os

def load_custom_tags(custom_rules_path):
    """Loads custom tagging rules from a JSON file."""
    if not custom_rules_path or not os.path.isfile(custom_rules_path):
        logging.warning(f"Custom tag rules file {custom_rules_path} not found.")
        return {}
    with open(custom_rules_path, 'r') as file:
        return json.load(file)


def apply_tags(video_info, custom_rules=None):
    """
    Applies tags to a video based on its metadata and AI-generated description.

    Args:
        video_info (dict): A dictionary containing video metadata and AI-generated description.
        custom_rules (str or None): Path to the custom rules JSON file.

    Returns:
        list: List of applied tags.
    """
    tags = []
    
    # Apply default tagging rules based on metadata
    if 'resolution' in video_info and '4K' in video_info['resolution']:
        tags.append("High Resolution")
    
    if 'duration' in video_info and video_info['duration'] > 600:
        tags.append("Extended Play")

    if video_info.get('codec') == "h264":
        tags.append("H.264 Codec")

    # Analyze AI-generated description for additional tags
    description = video_info.get('qwen_description', "").lower()
    
    if "action" in description:
        tags.append("Action")

    if "night shot" in description:
        tags.append("Night-time Filming")
    
    # (Add more rules/keywords as necessary)

    # Apply custom rules if available
    if custom_rules:
        custom_tags_rules = load_custom_tags(custom_rules)
        tags = apply_custom_rules(video_info, tags, custom_tags_rules)

    return list(set(tags))  # Remove duplicates


def apply_custom_rules(video_info, tags, custom_tags_rules):
    """
    Applies custom rules provided in a JSON file for tagging the video.

    Args:
        video_info (dict): A dictionary containing video metadata and AI-generated descriptions.
        tags (list): List of already applied tags during the default rules processing.
        custom_tags_rules (dict): Dictionary of custom rules.

    Returns:
        list: Updated list of tags after applying custom rules.
    """
    rules = custom_tags_rules.get("rules", [])
    for rule in rules:
        if 'description_keywords' in rule:
            keywords = set(rule['description_keywords'])
            if keywords.intersection(set(video_info.get('qwen_description', "").split())):
                tags.extend(rule['tags'])

        if 'metadata_conditions' in rule:
            conditions = rule.get('metadata_conditions', {})
            resolution = video_info.get('resolution', "")
            duration = video_info.get('duration', 0)
            if (conditions.get('resolution') == resolution and 
                duration > conditions.get('duration_gt', 0)):
                tags.extend(rule['tags'])

    return list(set(tags))  # Remove duplicates


def classify_video(video_info):
    """
    Classifies a video into a high-level category based on its tags and metadata.

    Args:
        video_info (dict): A dictionary containing tagged video metadata.

    Returns:
        str: Classification of the video (e.g., "Action", "Documentary").
    """
    tags = video_info.get('tags', [])
    
    if "Action" in tags or "High Intensity" in tags:
        return "Action"
    
    if "Documentary Footage" in tags or "Narrative" in video_info.get('qwen_description', "").lower():
        return "Documentary"

    if "Aerial Shot" in tags or "Drone Footage" in tags:
        return "Cinematic"

    # (Add more conditional classification logic as needed)
    
    return "Unclassified"  # Default classification if no rules apply
