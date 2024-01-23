import pytest
from unittest.mock import patch, MagicMock
from uploader import FileUploader

class TestFileUploader:

    def test_read_config_dict(self):
        config = {'key': 'value'}
        uploader = FileUploader(config)
        assert uploader.config == config

    @patch('builtins.open')
    def test_read_config_yaml(self, mock_open):
        path = '~/collection'
        f = mock_open.return_value
        f.method.return_value = path
        with patch('yaml.safe_load') as mock_load:
            uploader = FileUploader('config.yaml')
            mock_open.assert_called_once()
            mock_load.assert_called_once()

    def test_read_config_ini(self):
        with patch('configparser.ConfigParser.read') as mock_read:
            uploader = FileUploader('config.ini')
            mock_read.assert_called_once()

    @patch('builtins.open')
    def test_read_config_json(self, mock_open):
        with patch('json.load') as mock_load:
            uploader = FileUploader('config.json')
            mock_open.assert_called_once()
            mock_load.assert_called_once()

    def test_read_config_invalid(self):
        with pytest.raises(ValueError):
            uploader = FileUploader('config.txt')

    def test_create_s3_client(self):
        with patch('boto3.client') as mock_client:
            uploader = FileUploader({'AWS': {'s3_access_key': 'key', 's3_secret_key': 'secret'}})
            uploader.create_s3_client()
            mock_client.assert_called_once_with('s3', aws_access_key_id='key', aws_secret_access_key='secret')

    def test_create_gcs_client(self):
        with patch('google.cloud.storage.Client.from_service_account_json') as mock_client:
            uploader = FileUploader({'GCS': {'gcs_credentials': 'credentials.json'}})
            uploader.create_gcs_client()
            mock_client.assert_called_once_with('credentials.json')

    def test_list_files(self):
        with patch('os.path.exists', return_value=True), patch('os.walk', return_value=[('root', 'dirs', ['file1', 'file2'])]):
            uploader = FileUploader({})
            files = uploader.list_files('directory')
            assert files == ['root/file1', 'root/file2']

    def test_upload_to_s3(self):
        with patch.object(FileUploader, 'create_s3_client', return_value=MagicMock()):
            uploader = FileUploader({'AWS': {'s3_bucket': 'bucket'}})
            uploader.upload_to_s3('file')
            uploader.create_s3_client().upload_file.assert_called_once_with('file', 'bucket', 'file')

    def test_upload_to_gcs(self):
        with patch.object(FileUploader, 'create_gcs_client', return_value=MagicMock()):
            uploader = FileUploader({'GCS': {'gcs_bucket': 'bucket'}})
            uploader.upload_to_gcs('file')
            uploader.create_gcs_client().get_bucket().blob().upload_from_filename.assert_called_once_with('file')
    

    @patch.object(FileUploader, 'list_files', return_value=['file1.jpg', 'file2.pdf'])
    @patch.object(FileUploader, 'upload_to_s3')
    @patch.object(FileUploader, 'upload_to_gcs')
    def test_upload_files(self, mock_upload_to_gcs, mock_upload_to_s3, mock_list_files):
        config = {
            'FileTypes': {
                's3_file_types': 'jpg,png',
                'gcs_file_types': 'pdf,doc'
            }
        }
        uploader = FileUploader(config)
        uploader.upload_files('directory')

        mock_list_files.assert_called_once_with('directory')
        mock_upload_to_s3.assert_called_once_with('file1.jpg')
        mock_upload_to_gcs.assert_called_once_with('file2.pdf')


if __name__ == '__main__':
    pytest.main()