"""
file_utils.py - Secure file handling utilities
"""
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

# Define allowed file extensions
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'xlsx', 'xls', 'csv'}

def allowed_file(filename, file_type='image'):
    """
    Check if a file has an allowed extension
    
    Args:
        filename (str): The filename to check
        file_type (str): The type of file ('image' or 'document')
        
    Returns:
        bool: True if the file extension is allowed, False otherwise
    """
    if '.' not in filename:
        return False
        
    ext = filename.rsplit('.', 1)[1].lower()
    
    if file_type == 'image':
        return ext in ALLOWED_IMAGE_EXTENSIONS
    elif file_type == 'document':
        return ext in ALLOWED_DOCUMENT_EXTENSIONS
    
    return False

def save_file(file, upload_folder, file_type='image'):
    """
    Securely save an uploaded file
    
    Args:
        file: The file object from the request
        upload_folder (str): The folder to save the file in
        file_type (str): The type of file ('image' or 'document')
        
    Returns:
        str: The path to the saved file, or None if the file couldn't be saved
    """
    if file and allowed_file(file.filename, file_type):
        # Secure the filename to prevent directory traversal attacks
        filename = secure_filename(file.filename)
        
        # Generate a random UUID to prefix the filename
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Make sure the upload folder exists
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        return unique_filename
    
    return None