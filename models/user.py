from datetime import datetime
from typing import List


class User:
    """User model for database storage"""
    
    def __init__(self, user_id: int, username: str = "", name: str = ""):
        self.id = user_id
        self.username = username
        self.name = name
        self.points = 0
        self.free_videos_left = 2
        self.videos_remaining = 0
        self.videos_watched: List[int] = []
        self.repeat_index = 0
        self.referrals = 0
        self.is_banned = False
        self.join_date = datetime.now().isoformat()
        self.last_active = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """Convert user to dictionary"""
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "points": self.points,
            "free_videos_left": self.free_videos_left,
            "videos_remaining": self.videos_remaining,
            "videos_watched": self.videos_watched,
            "repeat_index": self.repeat_index,
            "referrals": self.referrals,
            "is_banned": self.is_banned,
            "join_date": self.join_date,
            "last_active": self.last_active
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'User':
        """Create user from dictionary"""
        user = User(data['id'], data.get('username', ''), data.get('name', ''))
        user.points = data.get('points', 0)
        user.free_videos_left = data.get('free_videos_left', 2)
        user.videos_remaining = data.get('videos_remaining', 0)
        user.videos_watched = data.get('videos_watched', [])
        user.repeat_index = data.get('repeat_index', 0)
        user.referrals = data.get('referrals', 0)
        user.is_banned = data.get('is_banned', False)
        user.join_date = data.get('join_date', datetime.now().isoformat())
        user.last_active = data.get('last_active', datetime.now().isoformat())
        return user
    
    def add_points(self, amount: int) -> None:
        """Add points to user"""
        self.points += amount
        self.videos_remaining += amount * 5  # 1 point = 5 videos
    
    def remove_points(self, amount: int) -> bool:
        """Remove points from user"""
        if self.points >= amount:
            self.points -= amount
            return True
        return False
    
    def consume_video(self) -> bool:
        """Consume one video from available videos"""
        if self.free_videos_left > 0:
            self.free_videos_left -= 1
            return True
        elif self.videos_remaining > 0:
            self.videos_remaining -= 1
            return True
        return False
    
    def update_last_active(self) -> None:
        """Update last active timestamp"""
        self.last_active = datetime.now().isoformat()
