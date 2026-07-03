from typing import Optional, List, Dict
from utils.database import Database
from models.video import Video
from models.user import User
from utils.logger import error_logger


class VideoService:
    """Video management service"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def add_video(self, file_id: str, file_unique_id: str, caption: str = "", uploaded_by: int = 0) -> bool:
        """Add video to database"""
        try:
            # Check for duplicates
            existing = self.get_video_by_unique_id(file_unique_id)
            if existing:
                error_logger.warning(f"Duplicate video attempted: {file_unique_id}")
                return False
            
            video = Video(file_id, file_unique_id, caption)
            video.uploaded_by = uploaded_by
            self.db.add_video(video.to_dict())
            return True
        except Exception as e:
            error_logger.error(f"Failed to add video: {e}")
            return False
    
    def get_videos(self) -> List[Video]:
        """Get all videos"""
        try:
            videos_data = self.db.get_videos()
            return [Video.from_dict(data) for data in videos_data]
        except Exception as e:
            error_logger.error(f"Failed to get videos: {e}")
            return []
    
    def get_video_by_unique_id(self, file_unique_id: str) -> Optional[Video]:
        """Get video by unique ID"""
        try:
            videos = self.get_videos()
            for video in videos:
                if video.file_unique_id == file_unique_id:
                    return video
            return None
        except Exception as e:
            error_logger.error(f"Failed to get video by unique ID: {e}")
            return None
    
    def delete_video(self, index: int) -> bool:
        """Delete video by index"""
        try:
            videos = self.get_videos()
            if 0 <= index < len(videos):
                self.db.delete_video(index)
                return True
            return False
        except Exception as e:
            error_logger.error(f"Failed to delete video: {e}")
            return False
    
    def get_next_video(self, user: User) -> Optional[Video]:
        """Get next video for user
        
        Logic:
        1. User gets 2 free videos
        2. Then uses points (1 point = 5 videos)
        3. Shows unseen videos first
        4. After all seen, repeats from beginning
        """
        try:
            videos = self.get_videos()
            if not videos:
                return None
            
            # Check if user can watch video
            if user.free_videos_left <= 0 and user.videos_remaining <= 0:
                return None
            
            # Find unseen videos
            unseen = [v for i, v in enumerate(videos) if i not in user.videos_watched]
            
            if unseen:
                # Return first unseen video
                video = unseen[0]
                video_index = videos.index(video)
            else:
                # All videos watched, repeat from beginning
                video = videos[user.repeat_index % len(videos)]
                video_index = user.repeat_index % len(videos)
                user.repeat_index += 1
            
            # Record video as watched
            if video_index not in user.videos_watched:
                user.videos_watched.append(video_index)
            
            # Consume video
            user.consume_video()
            
            return video
        except Exception as e:
            error_logger.error(f"Failed to get next video for user {user.id}: {e}")
            return None
    
    def get_video_stats(self) -> Dict:
        """Get video statistics"""
        try:
            videos = self.get_videos()
            return {
                "total_videos": len(videos),
                "last_uploaded": videos[-1].uploaded_at if videos else None
            }
        except Exception as e:
            error_logger.error(f"Failed to get video stats: {e}")
            return {}
