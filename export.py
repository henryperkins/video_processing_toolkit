import json
import logging
import os
from core import ensure_directory

def export_to_json(data, output_dir):
    """
    Export processed video data to a JSON file.

    Args:
        data (dict): Processed video data including metadata, tags, and classification.
        output_dir (str): Directory where the JSON file should be exported.
    """
    ensure_directory(output_dir)  # Ensure the output directory exists
    
    # Create the output file path using the video's filename
    filename = os.path.join(output_dir, f"{data['filename']}.json")
    
    try:
        # Write the data to a JSON file with pretty-print formatting
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        logging.info(f"Data exported to {filename}")
    except Exception as e:
        logging.error(f"Failed to export data to {filename}: {e}")
