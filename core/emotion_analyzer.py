# core/emotion_analyzer.py
# Emotion, Age, and Gender analysis using DeepFace
# DeepFace is a deep learning library that wraps multiple
# face analysis models into one simple interface

import os
import cv2
import numpy as np

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def analyze_face_deepface(image_path, face_coords=None):
    """
    Analyze a face using DeepFace
    Extracts: emotion, age, gender
    
    Args:
        image_path: path to image file
        face_coords: optional dict with x,y,width,height
                     if provided, analyzes only that face region
    
    Returns:
        dict with emotion, age, gender data
    
    Example:
    {
        "success": True,
        "emotion": "happy",
        "emotion_confidence": 87.3,
        "emotion_scores": {
            "happy": 87.3,
            "neutral": 8.2,
            "sad": 2.1,
            "angry": 1.4,
            "surprise": 0.8,
            "fear": 0.1,
            "disgust": 0.1
        },
        "age": 24,
        "age_range": "20-28",
        "gender": "Male",
        "gender_confidence": 96.2
    }
    """
    try:
        # Import DeepFace here to handle import errors gracefully
        from deepface import DeepFace

        # If face coordinates provided, crop to that region
        if face_coords:
            image = cv2.imread(image_path)
            if image is not None:
                x = face_coords.get("x", 0)
                y = face_coords.get("y", 0)
                w = face_coords.get("width", 100)
                h = face_coords.get("height", 100)

                # Add padding
                padding = 20
                img_h, img_w = image.shape[:2]
                x1 = max(0, x - padding)
                y1 = max(0, y - padding)
                x2 = min(img_w, x + w + padding)
                y2 = min(img_h, y + h + padding)

                cropped = image[y1:y2, x1:x2]

                # Save temp cropped image
                temp_path = image_path.replace(
                    os.path.basename(image_path),
                    "temp_crop.jpg"
                )
                cv2.imwrite(temp_path, cropped)
                analyze_path = temp_path
            else:
                analyze_path = image_path
        else:
            analyze_path = image_path

        # Run DeepFace analysis
        # actions: what we want to analyze
        # enforce_detection: False = don't crash if no face found
        results = DeepFace.analyze(
            img_path=analyze_path,
            actions=["emotion", "age", "gender"],
            enforce_detection=False,
            silent=True
        )

        # DeepFace returns list if multiple faces
        # Take first result
        if isinstance(results, list):
            result = results[0]
        else:
            result = results

        # Extract emotion data
        emotions = result.get("emotion", {})
        dominant_emotion = result.get("dominant_emotion", "neutral")

        # Get confidence for dominant emotion
        emotion_confidence = round(
            emotions.get(dominant_emotion, 0), 1
        )

        # Round all emotion scores
        emotion_scores = {
            emotion: round(score, 1)
            for emotion, score in emotions.items()
        }

        # Extract age
        age = result.get("age", 0)
        age_range = calculate_age_range(age)

        # Extract gender
        gender_data = result.get("gender", {})
        if isinstance(gender_data, dict):
            # Returns dict like {"Man": 96.2, "Woman": 3.8}
            dominant_gender = result.get(
                "dominant_gender", "Unknown"
            )
            gender_confidence = round(
                gender_data.get(dominant_gender, 0), 1
            )
            # Normalize gender label
            gender = "Male" if dominant_gender == "Man" else "Female"
        else:
            # Sometimes returns string directly
            gender = str(gender_data)
            gender_confidence = 0.0

        # Clean up temp file
        if face_coords and os.path.exists(temp_path):
            os.remove(temp_path)

        print(f"✅ DeepFace analysis: {dominant_emotion} "
              f"({emotion_confidence}%) | "
              f"Age: {age} | Gender: {gender}")

        return {
            "success": True,
            "emotion": dominant_emotion,
            "emotion_display": dominant_emotion.capitalize(),
            "emotion_confidence": emotion_confidence,
            "emotion_scores": emotion_scores,
            "age": int(age),
            "age_range": age_range,
            "gender": gender,
            "gender_confidence": gender_confidence,
            "error": None
        }

    except ImportError:
        error_msg = "DeepFace not installed. Run: pip install deepface"
        print(f"❌ {error_msg}")
        return get_fallback_analysis(error_msg)

    except Exception as e:
        error_msg = f"Analysis error: {str(e)}"
        print(f"❌ {error_msg}")
        return get_fallback_analysis(error_msg)


def calculate_age_range(age):
    """
    Convert exact age estimate to a range
    DeepFace returns approximate age like 24
    We convert to range like "20-28"
    
    Args:
        age: integer age estimate
    
    Returns:
        string like "20-28"
    """
    age = int(age)

    # Define age brackets
    if age < 5:
        return "0-5"
    elif age < 13:
        return f"{max(0, age-3)}-{age+3}"
    elif age < 20:
        return f"{max(13, age-3)}-{age+3}"
    elif age < 30:
        return f"{max(18, age-4)}-{age+4}"
    elif age < 40:
        return f"{age-4}-{age+4}"
    elif age < 50:
        return f"{age-5}-{age+5}"
    elif age < 60:
        return f"{age-5}-{age+5}"
    else:
        return f"{max(55, age-6)}-{age+6}"


def get_emotion_emoji(emotion):
    """
    Return emoji for each emotion
    """
    emoji_map = {
        "happy": "😊",
        "sad": "😢",
        "angry": "😠",
        "surprise": "😲",
        "fear": "😨",
        "disgust": "🤢",
        "neutral": "😐",
        "unknown": "❓"
    }
    return emoji_map.get(emotion.lower(), "😐")


def get_fallback_analysis(error_msg):
    """
    Return a safe fallback when analysis fails
    """
    return {
        "success": False,
        "emotion": "unknown",
        "emotion_display": "Unknown",
        "emotion_confidence": 0,
        "emotion_scores": {},
        "age": 0,
        "age_range": "Unknown",
        "gender": "Unknown",
        "gender_confidence": 0,
        "error": error_msg
    }


def analyze_multiple_faces(image_path, faces_list):
    """
    Analyze multiple faces found in an image
    
    Args:
        image_path: path to original image
        faces_list: list of face coordinate dicts
    
    Returns:
        list of analysis results, one per face
    """
    results = []

    if not faces_list:
        return results

    for face_coords in faces_list:
        analysis = analyze_face_deepface(image_path, face_coords)
        analysis["face_index"] = face_coords.get("face_index", 0)
        results.append(analysis)

    return results