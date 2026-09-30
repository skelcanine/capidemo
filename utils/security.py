import os
import werkzeug.utils
from PIL import Image
from flask import current_app

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    """
    Check if the file has an allowed extension (.jpg, .jpeg, .png).
    """
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def validate_image_header(file_stream):
    """
    Strict image header / MIME verification using Pillow.
    Ensures that uploaded file content is a genuine image (JPG, JPEG, PNG).
    """
    try:
        # Seek back to beginning before reading
        file_stream.seek(0)
        img = Image.open(file_stream)
        img.verify()
        
        # Reset file pointer again so it can be saved to disk
        file_stream.seek(0)
        
        # Verify format is JPEG or PNG
        if img.format not in ['JPEG', 'PNG']:
            return False
        return True
    except Exception as e:
        return False

def sanitize_user_filename(filename):
    """
    Sanitize filename to prevent path traversal attacks.
    """
    return werkzeug.utils.secure_filename(filename)
