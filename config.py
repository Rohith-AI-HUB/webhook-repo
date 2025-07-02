import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # MongoDB settings
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'webhook_db')
    
    # Application settings
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Webhook settings
    WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', None)  # GitHub webhook secret
    VERIFY_SSL = os.getenv('VERIFY_SSL', 'True').lower() == 'true'
    
    # UI settings
    REFRESH_INTERVAL = int(os.getenv('REFRESH_INTERVAL', 15))  # seconds
    MAX_EVENTS_DISPLAY = int(os.getenv('MAX_EVENTS_DISPLAY', 50))
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'webhook.log')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    MONGODB_URI = 'mongodb://localhost:27017/'
    DATABASE_NAME = 'webhook_db_dev'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    MONGODB_URI = os.getenv('MONGODB_URI')
    
    # Ensure secret key is set in production
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_NAME = 'webhook_db_test'
    MONGODB_URI = 'mongodb://localhost:27017/'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])

# GitHub webhook event types we care about
SUPPORTED_EVENTS = [
    'push',
    'pull_request'
]

# Event formatting templates
EVENT_TEMPLATES = {
    'push': '{author} pushed to {to_branch} on {timestamp}',
    'pull_request': '{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}',
    'merge': '{author} merged branch {from_branch} to {to_branch} on {timestamp}'
}

# Database collection names
COLLECTIONS = {
    'events': 'events',
    'statistics': 'statistics'
}

# API response limits
API_LIMITS = {
    'max_events': 100,
    'default_events': 50
}

# Webhook security settings
WEBHOOK_SETTINGS = {
    'timeout': 30,  # seconds
    'max_payload_size': 1024 * 1024,  # 1 MB
    'allowed_ips': [
        # GitHub webhook IP ranges (update as needed)
        '192.30.252.0/22',
        '185.199.108.0/22',
        '140.82.112.0/20'
    ]
}