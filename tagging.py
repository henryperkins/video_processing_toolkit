import logging

def apply_tags(video_info, custom_rules=None):
    """Apply tags to video based on metadata and optional custom rules."""
    tags = []

    # Default Rules
    if video_info.get('fps', 0) > 30:
        tags.append('High-FPS')
    if video_info.get('width', 0) >= 1920:
        tags.append('HD')
    if video_info.get('has_subtitle'):
        tags.append('Subtitled')
    
    # Additional Qwen2-VL based rules
    if 'Action' in video_info.get('qwen_description', ''):
        tags.append('Action')
    if 'Water' in video_info.get('qwen_description', ''):
        tags.append('Water-related content')
    
    # Apply custom rules if provided
    if custom_rules:
        apply_custom_rules(video_info, tags, custom_rules)
    
    logging.info(f"Tags applied: {tags}")
    return tags

def classify_video(video_info):
    """Classify the video into a category based on certain rules."""
    classification = 'Uncategorized'
    
    if 'Sports' in video_info.get('qwen_description', ''):
        classification = 'Sports'
    elif video_info.get('duration', 0) > 3600:
        classification = 'Feature-length'
    elif 'Action' in video_info.get('qwen_description', ''):
        classification = 'Action'
    elif 'Documentary' in video_info.get('qwen_description', ''):
        classification = 'Documentary'
    
    logging.info(f"Classification applied: {classification}")
    return classification

def apply_custom_rules(video_info, tags, custom_rules):
    """Applies custom tagging rules."""
    for rule in custom_rules:
        # Custom rule example: Adds a specific tag if a keyword is in the description
        if rule['keyword'] in video_info.get('qwen_description', ''):
            tags.append(rule['tag'])
            logging.debug(f"Custom Rule Applied: {rule['tag']} due to presence of {rule['keyword']}")