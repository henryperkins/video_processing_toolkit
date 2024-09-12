# Comprehensive Video Processing Toolkit

## Overview

This toolkit automates downloading, analyzing, tagging, and classifying videos. It leverages the Qwen2-VL multimodal AI model for content understanding, along with traditional video processing techniques, to provide rich metadata and insights.

## Key Features

- **Video Download:** Downloads videos from various sources (direct links and HTML pages).
- **Metadata Extraction:** Extracts technical metadata using FFmpeg (duration, resolution, codecs, etc.).
- **Scene Detection:** Identifies scene changes for granular video analysis.
- **AI-Powered Analysis:**  Analyzes video content using the Qwen2-VL model, generating descriptions and insights.
- **Customizable Tagging:**  Applies tags based on metadata, Qwen2-VL output, and custom rules.
- **Video Classification:**  Classifies videos into categories (e.g., sports, music).
- **Data Export:** Exports processed data in JSON format.
- **MongoDB Integration (Optional):** Stores data in a MongoDB database.

## Prerequisites

- **Python 3.7 or higher:** [https://www.python.org/downloads/](https://www.python.org/downloads/)
- **FFmpeg:** Install FFmpeg on your system. Instructions vary by operating system.
- **MongoDB (Optional):**  If you want to use MongoDB for storage, install it and set up a database.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/henryperkins/video_processing_toolkit.git
   cd video_processing_toolkit
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download the Qwen2-VL Model:**
   - Download the model files from Hugging Face: [https://huggingface.co/Qwen/Qwen2-VL-7B-Instruct](https://huggingface.co/Qwen/Qwen2-VL-7B-Instruct)
   - Extract the model files to the directory specified in your `config.ini` file (see below).

5. **Configure `config.ini`:**
   - Create a `config.ini` file in the project directory and customize the settings:
     ```ini
     [Paths]
     DownloadDirectory = downloaded_videos
     ProcessedDirectory = processed_videos

     [MongoDB]
     URI = your_mongodb_uri  ; Replace with your actual MongoDB URI
     DatabaseName = your_database_name
     CollectionName = your_collection_name

     [Qwen]
     ModelDir = /path/to/your/qwen2-vl-model  ; Replace with the path to the extracted model files

     [Concurrency]
     MaxWorkers = 5

     [SceneDetection]
     DefaultThreshold = 30.0

     [QwenVL]
     DefaultInstruction = Describe this video.
     ```

## Usage

1. **Run the script:**
   ```bash
   python interface.py --urls <video_url_1> <video_url_2> ... --output <output_directory>
   ```
   - Replace `<video_url_1>`, `<video_url_2>`, etc. with the URLs of the videos you want to process.
   - Replace `<output_directory>` with the directory where you want to save the processed JSON files.

2. **(Optional) Use a CSV file:**
   - Create a CSV file with columns `file_name`, `file_size`, `last_modified`, and `public_url` containing video information.
   - Run the script with the `--csv` option:
     ```bash
     python interface.py --csv <path_to_csv_file> --output <output_directory>
     ```

## Output

The toolkit generates a JSON file for each processed video in the specified output directory. The JSON file contains:

- Video metadata (duration, resolution, codec, etc.)
- Scene change timestamps
- Qwen2-VL generated description
- Applied tags
- Video classification

## Examples

- **Process videos from URLs:**
  ```bash
  python interface.py --urls https://www.example.com/video1.mp4 https://www.example.com/video2.mp4 --output processed_videos
  ```

- **Process videos from a CSV file:**
  ```bash
  python interface.py --csv video_list.csv --output processed_videos
  ```

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License.
