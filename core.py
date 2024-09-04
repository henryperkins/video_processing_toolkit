import requests
import configparser
import logging
import os
import pymongo
from pymongo.mongo_client import MongoClient  # MongoDB client to interact with MongoDB and Cosmos DB

# Setup configuration parser
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
    log_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s', 
                        handlers=[log_handler])


def ensure_directory(directory):
    """Ensures that a directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Created directory: {directory}")
    else:
        logging.debug(f"Directory exists: {directory}")


def connect_to_mongodb():
    """Connect to the MongoDB cluster using the details in the config.ini file."""
    mongodb_uri = config.get('MongoDB', 'URI')
    client = MongoClient(mongodb_uri)

    try:
        # This will trigger a connection validation to the MongoDB instance
        client.admin.command('ping')
        logging.info("Connected successfully to MongoDB server.")
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        raise
    
    return client


def get_mongodb_collection():
    """Retrieve the specific MongoDB database and collection."""
    client = connect_to_mongodb()
    database_name = config.get('MongoDB', 'DatabaseName')
    collection_name = config.get('MongoDB', 'CollectionName')
    
    return client[database_name][collection_name]


def query_qwen_vl_chat(video_url, instruction="Describe this video.", use_vpc=False):
    """
    Send a request to the Qwen-VL-Chat model API over HTTPS to process a video.

    Args:
        video_url (str): The URL of the video file.
        instruction (str): The instruction or query to be passed to the AI model.
        use_vpc (bool): Whether to use the VPC endpoint instead of the public one.

    Returns:
        str: The model's response, typically a description or analysis of the video.
    """
    endpoint = config.get("QwenVL", "VpcEndpoint") if use_vpc else config.get("QwenVL", "PublicEndpoint")
    access_key = config.get("QwenVL", "AccessKey")

    # Prepare the request payload
    payload = {
        "video_url": video_url,
        "instruction": instruction,
    }

    # Set the Authorization header with the access key
    headers = {
        "Authorization": f"Bearer {access_key}",
        "Content-Type": "application/json"
    }

    try:
        # Send the POST request to the model's API over HTTPS
        response = requests.post(endpoint, json=payload, headers=headers)

        # Handle the response, checking for status_code 200 (Success)
        if response.status_code == 200:
            result = response.json()
            return result.get("description", "No description available.")
        else:
            logging.error(f"API Error {response.status_code}: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        # Handle request exceptions (network issues, timeouts, etc.)
        logging.error(f"Failed to connect to the API: {e}")
        return None


# Example usage of connecting to the MongoDB and querying collection
if __name__ == "__main__":
    try:
        collection = get_mongodb_collection()
        logging.info(f"Sample document from collection: {collection.find_one()}")
    except Exception as e:
        logging.error(f"Error during MongoDB operation: {e}")
