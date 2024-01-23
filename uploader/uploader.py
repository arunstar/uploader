import os
import boto3
import logging
import yaml
import json
from google.cloud import storage
from configparser import ConfigParser

logging.basicConfig(level=logging.INFO)


class FileUploader:

    def __init__(self, config_file):
        """
        Initialize the FileUploader instance with the configuration from the specified file.

        :param config_file: Path to the configuration file (e.g., 'config.ini').
        """
        self.config = self.read_config(config_file)

    def read_config(self, config):
        """
        Read and parse the configuration from the specified file.

        :param config: Path to the configuration file or a dictionary.
        :return: Parsed configuration as a dictionary.
        """
        
        if isinstance(config, dict):
            return config
        elif config.endswith(('.yaml', '.yml')):
            with open(config, 'r') as f:
                return yaml.safe_load(f)
        elif config.endswith('.ini'):
            parser = ConfigParser()
            parser.read(config)
            return {s: dict(parser.items(s)) for s in parser.sections()}
        elif config.endswith('.json'):
            with open(config, 'r') as f:
                return json.load(f)
        else:
            raise ValueError('Error reading configuration from {config}. Invalid config format.')
    

    def create_s3_client(self):
        """
        Create an AWS S3 client using the provided access key and secret key.

        :return: Boto3 S3 client.
        """
        try:
            s3_key_id = self.config['AWS']['s3_access_key']
            s3_secret = self.config['AWS']['s3_secret_key']
            return boto3.client('s3', aws_access_key_id=s3_key_id, aws_secret_access_key=s3_secret)
        except Exception as e:
            logging.error(f"Error creating AWS S3 client: {str(e)}")

    def create_gcs_client(self):
        """
        Create a Google Cloud Storage client using the provided credentials file.

        :return: Google Cloud Storage client.
        """
        try:
            credentials_path = self.config['GCS']['gcs_credentials']
            return storage.Client.from_service_account_json(credentials_path)
        except Exception as e:
            logging.error(f"Error creating Google Cloud Storage client: {str(e)}")

    def list_files(self, directory):
        """
        Recursively list all files in the specified directory and its subdirectories.

        :param directory: Path to the directory.
        :return: List of file paths.
        """
        
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")

        try:
            file_list = []
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_list.append(os.path.join(root, file))
            return file_list
        except Exception as e:
            logging.error(f"Error listing files in {directory}: {str(e)}")

    def upload_to_s3(self, file_path):
        """
        Upload a file to AWS S3.

        :param file_path: Path to the file to be uploaded.
        """
        try:
            s3_client = self.create_s3_client()
            s3_bucket = self.config['AWS']['s3_bucket']
            s3_client.upload_file(file_path, s3_bucket, os.path.basename(file_path))
            logging.info(f"Uploaded {file_path} to AWS S3.")
        except Exception as e:
            logging.error(f"Error uploading {file_path} to AWS S3: {str(e)}")

    def upload_to_gcs(self, file_path):
        """
        Upload a file to Google Cloud Storage.

        :param file_path: Path to the file to be uploaded.
        """
        try:
            gcs_client = self.create_gcs_client()
            gcs_bucket = self.config['GCS']['gcs_bucket']
            bucket = gcs_client.get_bucket(gcs_bucket)
            blob = bucket.blob(os.path.basename(file_path))
            blob.upload_from_filename(file_path)
            logging.info(f"Uploaded {file_path} to Google Cloud Storage.")
        except Exception as e:
            logging.error(f"Error uploading {file_path} to Google Cloud Storage: {str(e)}")

    def upload_files(self, directory):
        """
        Upload files from the specified directory to AWS S3 or Google Cloud Storage based on file types.

        :param directory: Path to the directory containing files to be uploaded.
        """
        try:
            file_types_s3 = self.config['FileTypes']['s3_file_types'].split(',')
            file_types_gcs = self.config['FileTypes']['gcs_file_types'].split(',')

            files = self.list_files(directory)

            for file in files:
                file_type = file.split('.')[-1]
                if file_type in file_types_s3:
                    self.upload_to_s3(file)
                elif file_type in file_types_gcs:
                    self.upload_to_gcs(file)
        except Exception as e:
            logging.error(f"Error uploading files from {directory}: {str(e)}")


