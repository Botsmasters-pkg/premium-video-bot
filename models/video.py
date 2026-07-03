from datetime import datetime
from typing import Optional


class Video:
    """Video model for database storage"""
    
    def __init__(self, file_id: str, file_unique_id: str, caption: str = ""):
        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.caption = caption
        self.uploaded_at = datetime.now().isoformat()
        self.uploaded_by = 0
    
    def to_dict(self) -> dict:
        """Convert video to dictionary"""
        return {
            "file_id": self.file_id,
            "file_unique_id": self.file_unique_id,
            "caption": self.caption,
            "uploaded_at": self.uploaded_at,
            "uploaded_by": self.uploaded_by
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Video':
        """Create video from dictionary"""
        video = Video(data['file_id'], data['file_unique_id'], data.get('caption', ''))
        video.uploaded_at = data.get('uploaded_at', datetime.now().isoformat())
        video.uploaded_by = data.get('uploaded_by', 0)
        return video
