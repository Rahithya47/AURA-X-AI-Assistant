# utils/file_handler.py
# File upload handling and validation for AURA-X

import os
import uuid
import shutil
from datetime import datetime
from werkzeug.utils import secure_filename
from config import config


def allowed_file(filename, file_type="image"):
    """
    Check if file extension is allowed
    file_type: 'image', 'document', 'resume', 'video'
    """
    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    extension_map = {
        "image": config.ALLOWED_IMAGE_EXTENSIONS,
        "document": config.ALLOWED_DOCUMENT_EXTENSIONS,
        "resume": config.ALLOWED_RESUME_EXTENSIONS,
        "video": config.ALLOWED_VIDEO_EXTENSIONS
    }

    allowed = extension_map.get(file_type, set())
    return extension in allowed


def get_file_extension(filename):
    """Get file extension without the dot"""
    if "." in filename:
        return filename.rsplit(".", 1)[1].lower()
    return ""


def generate_unique_filename(original_filename):
    """
    Generate unique filename to avoid conflicts
    Example: photo.jpg → 2024_a1b2c3d4_photo.jpg
    """
    safe_name = secure_filename(original_filename)
    unique_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    extension = get_file_extension(safe_name)
    base_name = safe_name.rsplit(".", 1)[0] if "." in safe_name else safe_name

    return f"{timestamp}_{unique_id}_{base_name}.{extension}"


def save_uploaded_file(file, folder_key="images"):
    """
    Save uploaded file to correct folder
    Returns: (success, file_path, filename, error_message)
    """
    try:
        # Get target folder
        folder = config.UPLOAD_FOLDERS.get(folder_key, "uploads")

        # Make sure folder exists
        os.makedirs(folder, exist_ok=True)

        # Generate unique filename
        unique_filename = generate_unique_filename(file.filename)

        # Full path
        file_path = os.path.join(folder, unique_filename)

        # Save file
        file.save(file_path)

        return True, file_path, unique_filename, None

    except Exception as e:
        error_msg = f"Failed to save file: {str(e)}"
        print(f"❌ {error_msg}")
        return False, None, None, error_msg


def delete_file(file_path):
    """
    Delete a file safely
    Returns: (success, error_message)
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True, None
        else:
            return False, "File not found"
    except Exception as e:
        return False, str(e)


def get_file_size(file_path):
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except Exception:
        return 0


def ensure_folders_exist():
    """Create all required upload folders"""
    for folder_name, folder_path in config.UPLOAD_FOLDERS.items():
        os.makedirs(folder_path, exist_ok=True)
        print(f"✅ Folder ready: {folder_path}")