import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_fallback_secret_key_change_in_prod')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "database.db")}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload Configurations
    UPLOAD_FOLDER = os.path.join(BASE_DIR, os.getenv('UPLOAD_FOLDER', 'uploads'))
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    
    # Admin Seed Info
    ADMIN_FULL_NAME = os.getenv('ADMIN_FULL_NAME', 'System Administrator')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'AdminPass123!')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@capillary.med')
    
    # Default Credit System Settings
    NEW_USER_CREDITS = 5
