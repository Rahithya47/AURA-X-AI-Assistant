"""
Face Recognition Module
=======================
Identifies known people using face encodings
Uses face_recognition library (dlib-based)
"""

import face_recognition
import numpy as np
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import shutil

from config import Config
from database.db_manager import db


class FaceRecognizer:
    """Recognize known faces from a personal database"""
    
    def __init__(self):
        self.tolerance = Config.FACE_RECOGNITION_TOLERANCE
        self.model = Config.FACE_DETECTION_MODEL
        
        # Cache for known faces
        self.known_encodings: List[np.ndarray] = []
        self.known_names: List[str] = []
        self.known_ids: List[int] = []
        
        # Load known faces from database
        self._load_known_faces()
    
    def _load_known_faces(self):
        """Load all known face encodings from database"""
        try:
            results = db.get_all_face_encodings()
            
            self.known_encodings = []
            self.known_names = []
            self.known_ids = []
            
            for row in results:
                if row['face_encoding']:
                    encoding = pickle.loads(row['face_encoding'])
                    self.known_encodings.append(encoding)
                    self.known_names.append(row['name'])
                    self.known_ids.append(row['id'])
            
            print(f"✅ Loaded {len(self.known_encodings)} known faces")
            
        except Exception as e:
            print(f"❌ Error loading known faces: {e}")
    
    def encode_face(self, image_path: str) -> Optional[np.ndarray]:
        """
        Generate face encoding from image
        
        Args:
            image_path: Path to image file
            
        Returns:
            128-dimensional face encoding or None
        """
        try:
            image = face_recognition.load_image_file(str(image_path))
            encodings = face_recognition.face_encodings(image, model=self.model)
            
            if len(encodings) == 0:
                return None
            
            return encodings[0]
            
        except Exception as e:
            print(f"Error encoding face: {e}")
            return None
    
    def add_person(
        self, 
        name: str, 
        image_path: str, 
        profession: str = None,
        skills: str = None,
        notes: str = None
    ) -> Dict:
        """
        Add a new person to the known faces database
        
        Args:
            name: Person's name
            image_path: Path to their photo
            profession: Their profession/job
            skills: Their skills (comma-separated)
            notes: Additional notes
            
        Returns:
            dict with success status
        """
        try:
            # Generate face encoding
            encoding = self.encode_face(image_path)
            
            if encoding is None:
                return {
                    "success": False,
                    "error": "No face detected in image. Please use a clear photo."
                }
            
            # Create folder for person
            person_folder = Config.KNOWN_FACES_FOLDER / name.lower().replace(' ', '_')
            person_folder.mkdir(parents=True, exist_ok=True)
            
            # Copy image
            image_path = Path(image_path)
            new_photo_path = person_folder / image_path.name
            shutil.copy2(image_path, new_photo_path)
            
            # Serialize encoding
            encoding_blob = pickle.dumps(encoding)
            
            # Add to database
            person_id = db.add_person(
                name=name,
                profession=profession,
                skills=skills,
                notes=notes,
                photo_path=str(new_photo_path),
                face_encoding=encoding_blob
            )
            
            # Update cache
            self.known_encodings.append(encoding)
            self.known_names.append(name)
            self.known_ids.append(person_id)
            
            return {
                "success": True,
                "message": f"Added {name} to known faces! ✅",
                "person_id": person_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def recognize(self, image_path: str) -> Dict:
        """
        Recognize faces in an image
        
        Args:
            image_path: Path to image file
            
        Returns:
            dict with recognition results
        """
        try:
            # Load image
            image = face_recognition.load_image_file(str(image_path))
            
            # Find faces
            face_locations = face_recognition.face_locations(image, model=self.model)
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            if len(face_encodings) == 0:
                return {
                    "success": True,
                    "face_count": 0,
                    "message": "No faces detected in image",
                    "faces": []
                }
            
            results = []
            
            for i, (face_encoding, face_location) in enumerate(zip(face_encodings, face_locations)):
                # Default: Unknown
                name = "Unknown"
                person_id = None
                confidence = 0
                profile = None
                
                if len(self.known_encodings) > 0:
                    # Compare with known faces
                    matches = face_recognition.compare_faces(
                        self.known_encodings,
                        face_encoding,
                        tolerance=self.tolerance
                    )
                    
                    # Calculate distances
                    face_distances = face_recognition.face_distance(
                        self.known_encodings,
                        face_encoding
                    )
                    
                    if True in matches:
                        # Find best match
                        best_idx = np.argmin(face_distances)
                        
                        if matches[best_idx]:
                            name = self.known_names[best_idx]
                            person_id = self.known_ids[best_idx]
                            confidence = round((1 - face_distances[best_idx]) * 100, 2)
                            
                            # Get full profile
                            profile = db.get_person_by_id(person_id)
                
                # Bounding box (top, right, bottom, left)
                top, right, bottom, left = face_location
                
                face_result = {
                    "face_id": i + 1,
                    "identity": {
                        "name": name,
                        "person_id": person_id,
                        "confidence": confidence,
                        "is_known": name != "Unknown"
                    },
                    "bounding_box": {
                        "x": left,
                        "y": top,
                        "width": right - left,
                        "height": bottom - top
                    }
                }
                
                # Add profile if known
                if profile:
                    face_result["profile"] = {
                        "profession": profile.get('profession', ''),
                        "skills": profile.get('skills', ''),
                        "notes": profile.get('notes', '')
                    }
                
                results.append(face_result)
            
            return {
                "success": True,
                "face_count": len(results),
                "faces": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def remove_person(self, person_id: int) -> Dict:
        """Remove a person from known faces"""
        try:
            person = db.get_person_by_id(person_id)
            
            if not person:
                return {"success": False, "error": "Person not found"}
            
            # Delete from database
            db.delete_person(person_id)
            
            # Reload cache
            self._load_known_faces()
            
            return {
                "success": True,
                "message": f"Removed {person['name']} from known faces"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_person(self, person_id: int, **kwargs) -> Dict:
        """Update person details"""
        try:
            db.update_person(person_id, **kwargs)
            
            return {
                "success": True,
                "message": "Person updated successfully"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_all_people(self) -> List[Dict]:
        """Get all known people"""
        return db.get_all_people()
    
    def reload_faces(self):
        """Reload known faces from database"""
        self._load_known_faces()


# Singleton instance
face_recognizer = FaceRecognizer()