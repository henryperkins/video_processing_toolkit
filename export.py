import json
import logging
import os
from core import ensure_directory


def export_to_json(data, output_dir):
    """Export processed video data to a JSON file.

Args:
    data (Any): Processed video data including metadata, tags, and classification.
    output_dir (Any): Directory where the JSON file should be exported.

Returns:
    Any: The result of the export operation, which may include success status or error messages."""
    ensure_directory(output_dir)
    filename = os.path.join(output_dir, f"{data['filename']}.json")
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        logging.info(f'Data exported to {filename}')
    except Exception as e:
        logging.error(f'Failed to export data to {filename}: {e}')
