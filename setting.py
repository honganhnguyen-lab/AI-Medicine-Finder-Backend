from decouple import config

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',          # <-- add if you're using DRF
    # 'corsheaders',           # optional (for React dev)
    # 'storages',              # optional (for S3)

    # Your apps
    'api',                     # OR use 'api.apps.ApiConfig' if you have apps.py
    # If your app lives under backend/backend/api/, use:
    # 'backend.api',
    # or 'backend.api.apps.ApiConfig',
]

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = 'us-west-2' 
