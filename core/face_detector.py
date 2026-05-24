# core/face_detector.py
# Face detection using OpenCV Haarcascade
# Fast and lightweight - no deep learning needed for detection
# Just locates WHERE faces are in the image

import cv2
import os
import numpy as np
from config import config


def load_face_cascade():
    """
    Load the Haarcascade face detector
    First tries the models/ folder
    Falls back to OpenCV's built-in cascade
    
    Returns: cv2.CascadeClassifier object
    """
    # Try custom model path first
    custom_path = config.HAARCASCADE_PATH
    if os.path.exists(custom_path):
        cascade = cv2.CascadeClassifier(custom_path)
        if not cascade.empty():
            print(f"✅ Loaded cascade from: {custom_path}")
            return cascade

    # Fall back to OpenCV built-in
    builtin_path = cv2.data.haarcascades + \
                   "haarcascade_frontalface_default.xml"
    
    if os.path.exists(builtin_path):
        cascade = cv2.CascadeClassifier(builtin_path)
        if not cascade.empty():
            print(f"✅ Loaded built-in cascade")
            return cascade

    print("❌ Could not load face cascade")
    return None


def detect_faces(image_path):
    """
    Detect all faces in an image
    
    Args:
        image_path: path to the image file
    
    Returns:
        dict with:
        - success: bool
        - face_count: number of faces found
        - faces: list of face coordinate dicts
        - annotated_path: path to image with boxes drawn
        - error: error message if failed
    
    Example return:
    {
        "success": True,
        "face_count": 2,
        "faces": [
            {
                "x": 100, "y": 80,
                "width": 150, "height": 150,
                "face_index": 0
            },
            {
                "x": 300, "y": 90,
                "width": 140, "height": 140,
                "face_index": 1
            }
        ],
        "annotated_path": "uploads/images/annotated_xyz.jpg"
    }
    """
    # Validate image exists
    if not os.path.exists(image_path):
        return {
            "success": False,
            "face_count": 0,
            "faces": [],
            "annotated_path": None,
            "error": f"Image file not found: {image_path}"
        }

    try:
        # Load image with OpenCV
        image = cv2.imread(image_path)
        
        if image is None:
            return {
                "success": False,
                "face_count": 0,
                "faces": [],
                "annotated_path": None,
                "error": "Could not read image file"
            }

        # Convert to grayscale for detection
        # Haarcascade works better on grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Enhance contrast for better detection
        gray = cv2.equalizeHist(gray)

        # Load face detector
        face_cascade = load_face_cascade()
        if face_cascade is None:
            return {
                "success": False,
                "face_count": 0,
                "faces": [],
                "annotated_path": None,
                "error": "Face detector not available"
            }

        # Detect faces
        # scaleFactor: how much image size is reduced at each scale
        # minNeighbors: how many neighbors each candidate needs
        # minSize: minimum face size to detect
        detected = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        # Build faces list
        faces = []
        annotated_image = image.copy()

        if len(detected) > 0:
            for idx, (x, y, w, h) in enumerate(detected):
                faces.append({
                    "x": int(x),
                    "y": int(y),
                    "width": int(w),
                    "height": int(h),
                    "face_index": idx
                })

                # Draw rectangle on image
                cv2.rectangle(
                    annotated_image,
                    (x, y),
                    (x + w, y + h),
                    (108, 99, 255),  # Purple color (BGR)
                    2               # Line thickness
                )

                # Draw face number label
                label = f"Face {idx + 1}"
                cv2.putText(
                    annotated_image,
                    label,
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (108, 99, 255),
                    2
                )

        # Save annotated image
        annotated_path = save_annotated_image(
            annotated_image,
            image_path
        )

        face_count = len(faces)
        print(f"✅ Face detection: {face_count} faces found")

        return {
            "success": True,
            "face_count": face_count,
            "faces": faces,
            "annotated_path": annotated_path,
            "error": None
        }

    except Exception as e:
        error_msg = f"Face detection error: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "face_count": 0,
            "faces": [],
            "annotated_path": None,
            "error": error_msg
        }


def save_annotated_image(image, original_path):
    """
    Save the annotated image with face boxes drawn
    Returns: path to saved annotated image
    """
    try:
        # Create annotated filename
        folder = os.path.dirname(original_path)
        filename = os.path.basename(original_path)
        name, ext = os.path.splitext(filename)
        annotated_filename = f"annotated_{name}{ext}"
        annotated_path = os.path.join(folder, annotated_filename)

        cv2.imwrite(annotated_path, image)
        return annotated_path

    except Exception as e:
        print(f"❌ Error saving annotated image: {e}")
        return original_path


def crop_face(image_path, face_coords, padding=20):
    """
    Crop a specific face from image
    Useful for DeepFace analysis on individual faces
    
    Args:
        image_path: path to original image
        face_coords: dict with x, y, width, height
        padding: extra pixels around face
    
    Returns:
        cropped face image (numpy array) or None
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            return None

        h, w = image.shape[:2]

        x = max(0, face_coords["x"] - padding)
        y = max(0, face_coords["y"] - padding)
        x2 = min(w, face_coords["x"] + face_coords["width"] + padding)
        y2 = min(h, face_coords["y"] + face_coords["height"] + padding)

        cropped = image[y:y2, x:x2]
        return cropped

    except Exception as e:
        print(f"❌ Error cropping face: {e}")
        return None


def get_image_info(image_path):
    """
    Get basic image information
    Returns: dict with width, height, channels
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            return None

        h, w = image.shape[:2]
        channels = image.shape[2] if len(image.shape) > 2 else 1

        return {
            "width": w,
            "height": h,
            "channels": channels,
            "size_kb": round(os.path.getsize(image_path) / 1024, 1)
        }
    except Exception:
        return None