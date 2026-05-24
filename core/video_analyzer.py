"""
Video Analysis Module
=====================
Extracts frames and analyzes video content
"""

import cv2
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import timedelta

from config import Config
from core.face_detector import face_detector
from core.emotion_analyzer import emotion_analyzer


class VideoAnalyzer:
    """Analyze videos by extracting and processing frames"""
    
    def __init__(self):
        self.output_dir = Config.UPLOAD_IMAGES / 'video_frames'
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_frames(
        self, 
        video_path: str, 
        interval_seconds: float = 1.0,
        max_frames: int = 30
    ) -> Dict:
        """
        Extract frames from video at regular intervals
        
        Args:
            video_path: Path to video file
            interval_seconds: Seconds between frame captures
            max_frames: Maximum number of frames to extract
            
        Returns:
            dict with extracted frame paths
        """
        try:
            cap = cv2.VideoCapture(str(video_path))
            
            if not cap.isOpened():
                return {
                    "success": False,
                    "error": "Could not open video file"
                }
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            frame_interval = int(fps * interval_seconds)
            
            # Create output directory for this video
            video_name = Path(video_path).stem
            output_subdir = self.output_dir / video_name
            output_subdir.mkdir(parents=True, exist_ok=True)
            
            extracted_frames = []
            frame_count = 0
            saved_count = 0
            
            while cap.isOpened() and saved_count < max_frames:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    # Save frame
                    timestamp = frame_count / fps
                    frame_path = output_subdir / f"frame_{saved_count:04d}_{timestamp:.2f}s.jpg"
                    cv2.imwrite(str(frame_path), frame)
                    
                    extracted_frames.append({
                        "frame_number": saved_count,
                        "timestamp": round(timestamp, 2),
                        "timestamp_formatted": str(timedelta(seconds=int(timestamp))),
                        "path": str(frame_path)
                    })
                    
                    saved_count += 1
                
                frame_count += 1
            
            cap.release()
            
            return {
                "success": True,
                "video_info": {
                    "filename": Path(video_path).name,
                    "duration": round(duration, 2),
                    "fps": round(fps, 2),
                    "total_frames": total_frames
                },
                "extracted_frames": extracted_frames,
                "frame_count": len(extracted_frames)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_video(
        self, 
        video_path: str,
        interval_seconds: float = 2.0,
        max_frames: int = 15
    ) -> Dict:
        """
        Full video analysis with face detection and emotion analysis
        """
        try:
            # Extract frames
            extraction = self.extract_frames(video_path, interval_seconds, max_frames)
            
            if not extraction['success']:
                return extraction
            
            frame_analyses = []
            emotion_timeline = []
            total_faces = 0
            
            for frame_info in extraction['extracted_frames']:
                frame_path = frame_info['path']
                
                # Face detection
                face_result = face_detector.detect(frame_path)
                
                # Emotion analysis
                emotion_result = emotion_analyzer.analyze(frame_path)
                
                frame_analysis = {
                    "frame": frame_info['frame_number'],
                    "timestamp": frame_info['timestamp'],
                    "face_count": face_result.get('face_count', 0),
                }
                
                if emotion_result['success'] and emotion_result.get('analyses'):
                    analysis = emotion_result['analyses'][0]
                    frame_analysis['emotion'] = analysis['emotion']['dominant']
                    frame_analysis['emotion_confidence'] = analysis['emotion']['confidence']
                    frame_analysis['age'] = analysis['age']['estimated']
                    frame_analysis['gender'] = analysis['gender']['predicted']
                    
                    emotion_timeline.append({
                        "time": frame_info['timestamp'],
                        "emotion": analysis['emotion']['dominant']
                    })
                
                total_faces += face_result.get('face_count', 0)
                frame_analyses.append(frame_analysis)
            
            # Generate summary
            summary = self._generate_summary(frame_analyses, emotion_timeline)
            
            return {
                "success": True,
                "video_info": extraction['video_info'],
                "frame_analyses": frame_analyses,
                "emotion_timeline": emotion_timeline,
                "summary": summary
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_summary(
        self, 
        frame_analyses: List[Dict], 
        emotion_timeline: List[Dict]
    ) -> Dict:
        """Generate summary of video analysis"""
        if not frame_analyses:
            return {}
        
        # Count emotions
        emotion_counts = {}
        for item in emotion_timeline:
            emotion = item['emotion']
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Calculate averages
        ages = [f['age'] for f in frame_analyses if 'age' in f]
        avg_age = sum(ages) / len(ages) if ages else 0
        
        # Dominant emotion
        dominant_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else 'unknown'
        
        return {
            "total_frames_analyzed": len(frame_analyses),
            "emotion_distribution": emotion_counts,
            "dominant_emotion": dominant_emotion,
            "average_age": round(avg_age, 1),
            "frames_with_faces": sum(1 for f in frame_analyses if f.get('face_count', 0) > 0),
            "total_face_detections": sum(f.get('face_count', 0) for f in frame_analyses)
        }
    
    def get_video_info(self, video_path: str) -> Dict:
        """Get basic video information"""
        try:
            cap = cv2.VideoCapture(str(video_path))
            
            if not cap.isOpened():
                return {"success": False, "error": "Could not open video"}
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = total_frames / fps if fps > 0 else 0
            
            cap.release()
            
            return {
                "success": True,
                "info": {
                    "filename": Path(video_path).name,
                    "duration_seconds": round(duration, 2),
                    "duration_formatted": str(timedelta(seconds=int(duration))),
                    "fps": round(fps, 2),
                    "total_frames": total_frames,
                    "resolution": f"{width}x{height}",
                    "width": width,
                    "height": height
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}


# Singleton instance
video_analyzer = VideoAnalyzer()