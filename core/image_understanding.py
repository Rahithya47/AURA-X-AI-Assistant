# core/image_understanding.py
# Main image analysis pipeline
# Combines face detection + emotion + age + gender
# This is the single function called by the API route

import os
import cv2
from datetime import datetime

from core.face_detector import detect_faces, get_image_info
from core.emotion_analyzer import (
    analyze_face_deepface,
    analyze_multiple_faces,
    get_emotion_emoji
)


def understand_image(image_path):
    """
    Complete image analysis pipeline
    
    Step 1: Detect faces using OpenCV
    Step 2: Analyze each face with DeepFace
    Step 3: Attempt identity recognition (Phase 6)
    Step 4: Return combined result
    
    Args:
        image_path: path to uploaded image
    
    Returns:
        Complete analysis dict
    
    Example:
    {
        "success": True,
        "faces_detected": 2,
        "image_info": {"width": 640, "height": 480},
        "faces": [
            {
                "face_index": 0,
                "emotion": "happy",
                "emotion_display": "Happy",
                "emotion_emoji": "😊",
                "emotion_confidence": 87.3,
                "emotion_scores": {...},
                "age": 24,
                "age_range": "20-28",
                "gender": "Male",
                "gender_confidence": 96.2,
                "identity": "Unknown",
                "identity_confidence": 0
            }
        ],
        "annotated_image_path": "uploads/images/annotated_xyz.jpg",
        "annotated_image_url": "/uploads/images/annotated_xyz.jpg",
        "summary": "1 face detected: Happy Male, ~20-28 years"
    }
    """
    print(f"\n📸 Starting image analysis: {image_path}")

    # Validate image exists
    if not os.path.exists(image_path):
        return {
            "success": False,
            "faces_detected": 0,
            "faces": [],
            "error": "Image file not found",
            "annotated_image_path": None,
            "annotated_image_url": None,
            "summary": "Error: Image not found"
        }

    # ─────────────────────────────────────────
    # STEP 1: Get Image Info
    # ─────────────────────────────────────────
    image_info = get_image_info(image_path)

    # ─────────────────────────────────────────
    # STEP 2: Detect Faces
    # ─────────────────────────────────────────
    print("🔍 Detecting faces...")
    detection_result = detect_faces(image_path)

    if not detection_result["success"]:
        return {
            "success": False,
            "faces_detected": 0,
            "faces": [],
            "image_info": image_info,
            "error": detection_result.get("error", "Detection failed"),
            "annotated_image_path": None,
            "annotated_image_url": None,
            "summary": "Face detection failed"
        }

    face_count = detection_result["face_count"]
    detected_faces = detection_result["faces"]
    annotated_path = detection_result["annotated_path"]

    print(f"✅ Found {face_count} face(s)")

    # ─────────────────────────────────────────
    # STEP 3: No Faces Found
    # ─────────────────────────────────────────
    if face_count == 0:
        annotated_url = get_image_url(annotated_path)
        return {
            "success": True,
            "faces_detected": 0,
            "faces": [],
            "image_info": image_info,
            "error": None,
            "annotated_image_path": annotated_path,
            "annotated_image_url": annotated_url,
            "summary": "No faces detected in this image"
        }

    # ─────────────────────────────────────────
    # STEP 4: Analyze Each Face
    # ─────────────────────────────────────────
    print("🧠 Analyzing faces with DeepFace...")

    analyzed_faces = []

    for face_coords in detected_faces:
        face_index = face_coords.get("face_index", 0)
        print(f"  → Analyzing face {face_index + 1}...")

        # Run emotion/age/gender analysis
        analysis = analyze_face_deepface(image_path, face_coords)

        # ─────────────────────────────────────
        # STEP 5: Identity Recognition
        # Phase 6 will add real recognition
        # For now, attempt recognition
        # ─────────────────────────────────────
        identity_result = attempt_identity_recognition(
            image_path, face_coords
        )

        # ─────────────────────────────────────
        # Build face result
        # ─────────────────────────────────────
        emotion = analysis.get("emotion", "neutral")
        emoji = get_emotion_emoji(emotion)

        face_result = {
            # Face position
            "face_index": face_index,
            "position": {
                "x": face_coords.get("x", 0),
                "y": face_coords.get("y", 0),
                "width": face_coords.get("width", 0),
                "height": face_coords.get("height", 0)
            },

            # Emotion data
            "emotion": emotion,
            "emotion_display": analysis.get(
                "emotion_display", emotion.capitalize()
            ),
            "emotion_emoji": emoji,
            "emotion_confidence": analysis.get(
                "emotion_confidence", 0
            ),
            "emotion_scores": analysis.get("emotion_scores", {}),

            # Age data
            "age": analysis.get("age", 0),
            "age_range": analysis.get("age_range", "Unknown"),

            # Gender data
            "gender": analysis.get("gender", "Unknown"),
            "gender_confidence": analysis.get("gender_confidence", 0),

            # Identity data
            "identity": identity_result.get("name", "Unknown"),
            "identity_confidence": identity_result.get(
                "confidence", 0
            ),
            "identity_info": identity_result.get("info", None),

            # Analysis status
            "analysis_success": analysis.get("success", False)
        }

        analyzed_faces.append(face_result)

    # ─────────────────────────────────────────
    # STEP 6: Build Summary
    # ─────────────────────────────────────────
    summary = build_summary(face_count, analyzed_faces)

    # Get annotated image URL for frontend
    annotated_url = get_image_url(annotated_path)

    print(f"✅ Analysis complete: {summary}")

    return {
        "success": True,
        "faces_detected": face_count,
        "faces": analyzed_faces,
        "image_info": image_info,
        "error": None,
        "annotated_image_path": annotated_path,
        "annotated_image_url": annotated_url,
        "summary": summary,
        "timestamp": datetime.now().isoformat()
    }


def attempt_identity_recognition(image_path, face_coords):
    """
    Try to identify a face
    
    Phase 3: Returns Unknown (placeholder)
    Phase 6: Will use real face_recognizer module
    
    Returns:
        dict with name, confidence, info
    """
    try:
        # Try to import face recognizer (Phase 6)
        from core.face_recognizer import recognize_face
        return recognize_face(image_path, face_coords)
    except ImportError:
        # Face recognizer not built yet
        pass
    except Exception as e:
        print(f"⚠️ Identity recognition error: {e}")

    # Return Unknown for now
    return {
        "name": "Unknown",
        "confidence": 0,
        "info": None
    }


def build_summary(face_count, faces):
    """
    Build a human-readable summary of results
    
    Example:
    "2 faces detected: Face 1 - Happy Male ~22-28 yrs | 
                       Face 2 - Neutral Female ~30-38 yrs"
    """
    if face_count == 0:
        return "No faces detected"

    if face_count == 1:
        face = faces[0]
        emotion = face.get("emotion_display", "Unknown")
        gender = face.get("gender", "Unknown")
        age_range = face.get("age_range", "Unknown")
        identity = face.get("identity", "Unknown")
        emoji = face.get("emotion_emoji", "")

        if identity != "Unknown":
            return (f"1 face recognized: {identity} | "
                    f"{emoji} {emotion} | "
                    f"{gender} | ~{age_range} years")
        else:
            return (f"1 face detected: "
                    f"{emoji} {emotion} | "
                    f"{gender} | ~{age_range} years")
    else:
        parts = [f"{face_count} faces detected:"]
        for face in faces:
            emotion = face.get("emotion_display", "?")
            gender = face.get("gender", "?")
            age = face.get("age_range", "?")
            emoji = face.get("emotion_emoji", "")
            idx = face.get("face_index", 0) + 1
            parts.append(f"Face {idx}: {emoji}{emotion} {gender} ~{age}")

        return " | ".join(parts)


def get_image_url(image_path):
    """
    Convert file path to URL accessible from browser
    
    Example:
    "uploads/images/photo.jpg" → "/uploads/images/photo.jpg"
    """
    if not image_path:
        return None

    # Normalize path separators
    url = image_path.replace("\\", "/")

    # Add leading slash if missing
    if not url.startswith("/"):
        url = "/" + url

    return url