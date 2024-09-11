# Comprehensive Video Processing Toolkit

## Overview

This toolkit is designed to automate the process of downloading, analyzing, tagging, and classifying video content. It leverages AI-powered content analysis (via Qwen2-VL-Chat API) alongside traditional video processing techniques to provide rich metadata and insights about video files.

## Key Features

- Video downloading from various sources (direct links and HTML pages)
- Metadata extraction using FFmpeg
- Scene detection for granular video analysis
- AI-powered content description using Qwen2-VL-Chat API
- Custom tagging system based on metadata and AI-generated descriptions
- Video classification into high-level categories
- Exportation of processed data in JSON format
- Integration with MongoDB/Cosmos DB for data storage (optional)

## Prerequisites

- Python 3.6 or higher
- FFmpeg installed and accessible from PATH
- MongoDB instance (optional, for data storage)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/video-processing-toolkit.git
   cd video-processing-toolkit
   ```

2. Set up a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Configure the `config.ini` file with your settings, including API endpoints and access keys.

## Usage

Run the script using the command-line interface:

```
python interface.py --urls http://example.com/video1.mp4 http://example.com/video2.mp4 --output processed_videos --log_level INFO
```

### Command-line Arguments

- `--urls`: List of video URLs to process (required)
- `--config`: Path to the configuration file (default: 'config.ini')
- `--output`: Output directory for processed data (default: from config.ini)
- `--log_level`: Set the logging level (choices: DEBUG, INFO, WARNING, ERROR, CRITICAL; default: INFO)
- `--scene_threshold`: Threshold for scene detection (default: from config.ini)
- `--qwen_instruction`: Instruction passed to Qwen-VL API (default: from config.ini)
- `--use_vpc`: Use the VPC endpoint for Qwen-VL API calls (flag)

## Configuration

The `config.ini` file contains various settings:

- Paths for downloaded and processed videos
- MongoDB connection details
- Qwen-VL API endpoints and access key
- Default values for scene detection and AI instructions

## Customization

- `custom_tags.json`: Define custom tagging rules based on metadata and AI-generated descriptions.
- `priority_keywords.json`: Specify keywords for the AI model to prioritize during content analysis.

## Output

The toolkit generates a JSON file for each processed video, containing:

- Video metadata (duration, resolution, codec, etc.)
- Scene change timestamps
- AI-generated content description
- Applied tags
- High-level classification

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- FFmpeg for video processing capabilities
- Qwen2-VL-Chat API for AI-powered content analysis
