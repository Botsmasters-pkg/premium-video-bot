from typing import Optional, List, Dict
from datetime import datetime
from utils.database import Database
from models.user import User
from utils.logger import error_logger


class UserService:
    """User management service"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            user_data = self.db.get_user(user_id)
            if user_data:
                return User.from_dict(user_data)
            return None
        except Exception as e:
            error_logger.error(f"Failed to get user {user_id}: {e}")
            return None
    
    def create_user(self, user_id: int, username: str = "", name: str = "") -> User:
        """Create new user"""
        try:
            user = User(user_id, username, name)
            self.db.save_user(user_id, user.to_dict())
            return user
        except Exception as e:
            error_logger.error(f"Failed to create user {user_id}: {e}")
            return User(user_id, username, name)
    
    def update_user(self, user: User) -> None:
        """Update user"""
        try:
            user.update_last_active()
            self.db.save_user(user.id, user.to_dict())
        except Exception as e:
            error_logger.error(f"Failed to update user {user.id}: {e}")
    
    def get_or_create_user(self, user_id: int, username: str = "", name: str = "") -> User:
        """Get user or create if not exists"""
        user = self.get_user(user_id)
        if user is None:
            user = self.create_user(user_id, username, name)
        else:
            user.update_last_active()
            self.update_user(user)
        return user
    
    def get_all_users(self) -> List[User]:
        """Get all users"""
        try:
            users_data = self.db.get_all_users()
            return [User.from_dict(data) for data in users_data.values()]
        except Exception as e:
            error_logger.error(f"Failed to get all users: {e}")
            return []
    
    def get_active_users(self) -> List[User]:
        """Get active users (not banned)"""
        return [u for u in self.get_all_users() if not u.is_banned]
    
    def ban_user(self, user_id: int) -> bool:
        """Ban user"""
        try:
            user = self.get_user(user_id)
            if user:
                user.is_banned = True
                self.update_user(user)
                return True
            return False
        except Exception as e:
            error_logger.error(f"Failed to ban user {user_id}: {e}")
            return False
    
    def unban_user(self, user_id: int) -> bool:
        """Unban user"""
        try:
            user = self.get_user(user_id)
            if user:
                user.is_banned = False
                self.update_user(user)
                return True
            return False
        except Exception as e:
            error_logger.error(f"Failed to unban user {user_id}: {e}")
            return False
    
    def add_points(self, user_id: int, amount: int) -> bool:
        """Add points to user"""
        try:
            user = self.get_user(user_id)
            if user:
                user.add_points(amount)
                self.update_user(user)
                return True
            return False
        except Exception as e:
            error_logger.error(f"Failed to add points to user {user_id}: {e}")
            return False
    
    def remove_points(self, user_id: int, amount: int) -> bool:
        """Remove points from user"""
        try:
            user = self.get_user(user_id)
            if user:
                success = user.remove_points(amount)
                if success:
                    self.update_user(user)
                return success
            return False
        except Exception as e:
            error_logger.error(f"Failed to remove points from user {user_id}: {e}")
            return False
    
    def add_referral(self, user_id: int) -> bool:
        """Add referral to user and grant points"""
        try:
            user = self.get_user(user_id)
            if user:
                user.referrals += 1
                user.add_points(1)  # 1 referral = 1 point
                self.update_user(user)
                return True
            return False
        except Exception as e:
            error_logger.error(f"Failed to add referral for user {user_id}: {e}")
            return False
    
    def get_top_referrers(self, limit: int = 10) -> List[User]:
        """Get top referrers"""
        try:
            users = self.get_all_users()
            return sorted(users, key=lambda u: u.referrals, reverse=True)[:limit]
        except Exception as e:
            error_logger.error(f"Failed to get top referrers: {e}")
            return []
