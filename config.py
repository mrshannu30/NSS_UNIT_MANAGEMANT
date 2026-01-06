import os
from datetime import timedelta

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'nss_secret_key_change_this_in_production'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # MySQL Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or '3015'
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'nss_management'
    MYSQL_CURSORCLASS = 'DictCursor'
    
    # Upload Configuration
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    
    # Security Configuration
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Application Configuration
    APP_NAME = 'NSS Unit Management System'
    COLLEGE_NAME = 'Your College Name'
    NSS_UNIT_NAME = 'NSS Unit'
    
    # Pagination
    VOLUNTEERS_PER_PAGE = 20
    EVENTS_PER_PAGE = 10
    ATTENDANCE_PER_PAGE = 50
    
    # QR Code Configuration
    QR_CODE_SIZE = 10
    QR_CODE_BORDER = 4

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    MYSQL_DB = 'nss_management_test'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}