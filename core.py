import requests
import configparser
import logging
import os
from logging.handlers import RotatingFileHandler

# Initial configurations and logging setup
config = configparser.ConfigParser()

def load_config(config_path='config.ini'):
    """Loads the configuration from a config file."""
    try:
        config.read(config_path)
        return config
    except configparser.Error as e:
        logging.error(f"Error reading config.ini: {e}")
        raise

def setup_logging(log_file='video_processing.log'):
    """Set up logging configuration."""
    log_handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[log_handler])

def ensure_directory(directory):
    """Ensures that a directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Created directory: {directory}")
    else:
        logging.debug(f"Directory exists: {directory}")

def connect_to_mongodb():
    """Establishes a connection to MongoDB/CosmosDB."""
    try:
        from pymongo import MongoClient
        db_uri = config.get("MongoDB", "URI", fallback="your-default-uri")
        client = MongoClient(db_uri)
        # Since ping and connection checks might vary, a dedicated method is useful
        client.admin.command('ping')  
        return client
    except Exception as e:
        logging.error(f"MongoDB connection failed: {e}")
        return None

def get_mongodb_collection():
    """Retrieves the MongoDB collection after establishing a connection."""
    try:
        client = connect_to_mongodb()
        database_name = config.get("MongoDB", "DatabaseName", fallback="video_database")
        collection_name = config.get("MongoDB", "CollectionName", fallback="videos")
        db = client[database_name]
        collection = db[collection_name]
        return collection
    except Exception as e:
        logging.error(f"Could not retrieve MongoDB collection: {e}")
        return None

def load_priority_keywords(file_path='priority_keywords.json'):
    """Load priority keywords for analysis."""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            logging.error(f"Could not load priority keywords: {e}")
    return []

def query_qwen_vl_chat(video_url, instruction="Describe this video.", use_vpc=False):
    """
    Sends a request to the Qwen-VL-Chat model API over HTTPS to process a video.

    Args:
        video_url (str): The URL of the video file.
        instruction (str): The instruction or query to be passed to the AI model.
        use_vpc (bool): Whether to use the VPC endpoint instead of the public one.

    Returns:
        str: The model's response, typically a description or analysis of the video.
    """
    # Load from config with fallbacks
    public_endpoint = config.get("QwenVL", "PublicEndpoint", fallback="https://your-public-endpoint")
    vpc_endpoint = config.get("QwenVL", "VpcEndpoint", fallback="https://your-vpc-endpoint")
    access_key = config.get("QwenVL", "AccessKey", fallback="your-access-key")

    # Choose the endpoint depending on VPC flag
    endpoint = vpc_endpoint if use_vpc else public_endpoint

    # Add priority keywords to the instruction
    priority_keywords = load_priority_keywords()
    if priority_keywords:
        instruction += " Focus on these aspects: " + ", ".join(priority_keywords)

    # Prepare the request payload
    payload = {
        "video_url": video_url,
        "instruction": instruction,
    }

    # Set the Authorization header with the access key.
    headers = {
        "Authorization": f"Bearer {access_key}",
        "Content-Type": "application/json"
    }

    try:
        # Send a POST request to the model's API over HTTPS
        response = requests.post(endpoint, json=payload, headers=headers)

        # Handle the response and return the description from the AI model
        if response.status_code == 200:
            result = response.json()
            return result.get("description", "No description available.")
        else:
            logging.error(f"API Error {response.status_code}: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to connect to the API: {e}")
        return None
