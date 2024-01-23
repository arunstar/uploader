from setuptools import setup, find_packages

setup(
    name='storage',
    version='0.1',
    author='Arun M',
    description='File Util for S3 and GCS.',
    url='https://github.com/arunstar/uploader',
    packages=find_packages(exclude=['tests*']),
    python_requires='>=3.7',
    install_requires=[
        'boto3',
        'google-cloud-storage',
    ],
)