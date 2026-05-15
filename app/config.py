import os


class Config:
    """Base configuration loaded from environment variables."""

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY_CSRF', 'KEY-CSRF-ACA-DEBE-IR')
    DEBUG = False

    # MySQL
    HOST_BD = os.environ.get('HOST_BD', 'dev.jonnattan.com')
    PORT_BD = int(os.environ.get('PORT_BD', 3306))
    USER_BD = os.environ.get('USER_BD', '----')
    PASS_BD = os.environ.get('PASS_BD', '*****')
    SCHEMA_BD = os.environ.get('SCHEMA_BD', '*****')

    # AWS
    AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY', 'None')
    AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY', 'None')
    AWS_PINPOINT_APP_ID = os.environ.get('AWS_PINPOINT_APP_ID', 'None')
    AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET', 'None')
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

    # APIs / Integrations
    NOTIFICATION_URL = os.environ.get('NOTIFICATION_URL', 'None')
    NOTIFICATION_API_KEY = os.environ.get('NOTIFICATION_API_KEY', 'None')
    LOGIA_API_KEY = os.environ.get('LOGIA_API_KEY', 'None')
    LOGIA_BASE_URL = os.environ.get('LOGIA_BASE_URL', 'None')
    UCC_API_KEY = os.environ.get('UCC_API_KEY', 'None')
    PAGE_API_KEY = os.environ.get('PAGE_API_KEY', 'None')
    GEO_API_KEY = os.environ.get('GEO_API_KEY', 'None')
    GEO_API_URL = os.environ.get('GEO_API_URL', 'None')
    LLM_API_KEY = os.environ.get('LLM_API_KEY', 'None')
    LLM_AES_KEY = os.environ.get('LLM_AES_KEY', 'None')
    LLM_URL = os.environ.get('LLM_URL', 'None')
    LLM_NAME = os.environ.get('LLM_NAME', 'None')
    LLM_MODEL = os.environ.get('LLM_MODEL', 'None')
    CHATBOT_API_KEY = os.environ.get('CHATBOT_API_KEY', 'None')
    FILE_CHAT_KEY = os.environ.get('FILE_CHAT_KEY', 'None')
    ATTLASIAN_TOKEN = os.environ.get('ATTLASIAN_TOKEN', 'None')
    ATTLASIAN_USER = os.environ.get('ATTLASIAN_USER', 'None')
    ATTLASIAN_URL = os.environ.get('ATTLASIAN_URL', 'None')
    WAZA_BEARER_TOKEN = os.environ.get('WAZA_BEARER_TOKEN', 'None')
    PHONE_ID = os.environ.get('PHONE_ID', 'None')
    WAZA_API_VERSION = os.environ.get('WAZA_API_VERSION', 'None')
    UUID_WZ = os.environ.get('UUID_WZ', 'None')
    SLACK_NOTIFICATION = os.environ.get('SLACK_NOTIFICATION', 'None')
    BEARER_MIDDLEWARE = os.environ.get('BEARER_MIDDLEWARE', 'None')
    API_KEY_ROBOT_UPTIME = os.environ.get('API_KEY_ROBOT_UPTIME', '')
    TRANSBOT_ID = int(os.environ.get('TRANSBOT_ID', -1))

    # Security / Encryption
    AES_KEY = os.environ.get('AES_KEY', 'None')
    RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY', 'NO_SECRET_KEY')
    HCAPTCHA_SECRET_KEY = os.environ.get('HCAPTCHA_SECRET_KEY', 'NO_SECRET_KEY')

    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
