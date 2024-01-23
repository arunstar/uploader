# uploader

`uploader` python module uploads files from a directory to AWS S3 and Google Cloud Storage (GCS). It supports a variety of file types and uses a configuration file for easy customization.

## Installation

You can install this module using pip:

```bash
pip install .
```

## Usage

```python
from uploader import FileUploader

uploader = FileUploader('config.ini') # or 'config.ini', 'config.json', or a dictionary
directory_to_upload = '/path/to/your/directory'
uploader.upload_files(directory_to_upload)
```

### Expected format for config file

```ini
[AWS]
s3_bucket = sacumen_bucket_name
s3_access_key = sacumen_s3_access_key
s3_secret_key = sacumen_s3_secret_key

[GCS]
gcs_bucket = sacumen_project_id
gcs_credentials = sacumen_gcs_credentials_json_file_path

[FileTypes]
s3_file_types = jpg,png,svg,webp,mp3,mp4,mpeg4,wmv,3gp,webm
gcs_file_types = doc,docx,csv,pdf
```

### Run tests

```bash
pytest
```

### Run tests (with coverage)

```bash
pytest --cov=uploader
# With html report
pytest --cov=. --cov-report html
```
