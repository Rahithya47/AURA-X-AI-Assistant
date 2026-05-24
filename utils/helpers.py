# utils/helpers.py
# Common helper functions used across AURA-X

import os
import uuid
from datetime import datetime


def success_response(data=None, message="Success"):
    """
    Standard JSON success response
    Used by all API routes
    """
    response = {
        "status": "success",
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    if data is not None:
        response["data"] = data
    return response


def error_response(message="An error occurred", code=400):
    """
    Standard JSON error response
    Used by all API routes
    """
    return {
        "status": "error",
        "message": message,
        "code": code,
        "timestamp": datetime.now().isoformat()
    }, code


def format_file_size(size_bytes):
    """
    Convert bytes to human readable format
    Example: 1048576 → "1.0 MB"
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def generate_unique_id():
    """Generate a unique ID string"""
    return str(uuid.uuid4())


def get_timestamp():
    """Get current timestamp as formatted string"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def sanitize_filename(filename):
    """
    Make filename safe for saving
    Remove special characters
    """
    import re
    # Keep only alphanumeric, dots, hyphens, underscores
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    return filename