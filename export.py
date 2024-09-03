import json
import logging
import os

def export_to_json(data, output_dir):
    """Export processed data to a JSON file."""
    ensure_directory(output_dir)  # Ensure the output directory exists
    filename = os.path.join(output_dir, f"{data['filename']}.json")
    
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        logging.info(f"Data exported to {filename}")
    except Exception as e:
        logging.error(f"Failed to export data to {filename}: {e}")