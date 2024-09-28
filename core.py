import requests
import configparser
import logging
import os
import json
from logging.handlers import RotatingFileHandler
config = configparser.ConfigParser()


def load_config(config_path='config.ini'):
    """Loads the configuration from a config file.

Args:
    config_path (Any): The path to the configuration file, which can be a string or any other type that represents a file path.

Returns:
    Any: The loaded configuration data, which can be of any type depending on the configuration file format."""
    try:
        config.read(config_path)
        return config
    except configparser.Error as e:
        logging.error(f'Error reading config.ini: {e}')
        raise


def setup_logging(log_file='video_processing.log'):
    """Set up logging configuration.

Args:
    log_file (Any): The path to the log file where logs will be written. This can be a string or any other type that represents a file path.

Returns:
    Any: None, but configures the logging settings for the application."""
    log_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024,
        backupCount=5)
    logging.basicConfig(level=logging.INFO, format=
        '%(asctime)s - %(levelname)s - %(message)s', handlers=[log_handler])


def ensure_directory(directory):
    """Ensures that a directory exists.

Args:
    directory (Any): The path to the directory that needs to be checked or created. This can be a string or any other type that represents a directory path.

Returns:
    Any: None, but creates the directory if it does not exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f'Created directory: {directory}')
    else:
        logging.debug(f'Directory exists: {directory}')


def connect_to_mongodb():
    """Establishes a connection to MongoDB/CosmosDB.

Returns:
    Any: A connection object or client instance that can be used to interact with the database."""
    try:
        from pymongo import MongoClient
        db_uri = config.get('MongoDB', 'URI', fallback='your-default-uri')
        client = MongoClient(db_uri)
        client.admin.command('ping')
        return client
    except Exception as e:
        logging.error(f'MongoDB connection failed: {e}')
        return None


def get_mongodb_collection():
    """Retrieves the MongoDB collection after establishing a connection.

Returns:
    Any: The MongoDB collection object that can be used to perform database operations."""
    try:
        client = connect_to_mongodb()
        database_name = config.get('MongoDB', 'DatabaseName', fallback=
            'video_database')
        collection_name = config.get('MongoDB', 'CollectionName', fallback=
            'videos')
        db = client[database_name]
        collection = db[collection_name]
        return collection
    except Exception as e:
        logging.error(f'Could not retrieve MongoDB collection: {e}')
        return None


def load_priority_keywords(file_path='priority_keywords.json'):
    """Load priority keywords for analysis.

Args:
    file_path (Any): The path to the file containing priority keywords. This can be a string or any other type that represents a file path.

Returns:
    Any: A list or set of priority keywords loaded from the specified file."""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            logging.error(f'Could not load priority keywords: {e}')
    return []


def query_qwen_vl_chat(video_url, instruction='Describe this video.',
    use_vpc=False):
    """Sends a request to the Qwen-VL-Chat model API over HTTPS to process a video.

Args:
    video_url (str): The URL of the video file.
    instruction (str): The instruction or query to be passed to the AI model.
    use_vpc (bool): Whether to use the VPC endpoint instead of the public one.

Returns:
    str: The model's response, typically a description or analysis of the video."""
    public_endpoint = config.get('QwenVL', 'PublicEndpoint', fallback=
        'https://your-public-endpoint')
    vpc_endpoint = config.get('QwenVL', 'VpcEndpoint', fallback=
        'https://your-vpc-endpoint')
    access_key = config.get('QwenVL', 'AccessKey', fallback='your-access-key')
    endpoint = vpc_endpoint if use_vpc else public_endpoint
    priority_keywords = load_priority_keywords()
    if priority_keywords:
        instruction += ' Focus on these aspects: ' + ', '.join(
            priority_keywords)
    payload = {'video_url': video_url, 'instruction': instruction}
    headers = {'Authorization': f'Bearer {access_key}', 'Content-Type':
        'application/json'}
    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result.get('description', 'No description available.')
        else:
            logging.error(f'API Error {response.status_code}: {response.text}')
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f'Failed to connect to the API: {e}')
        return None
