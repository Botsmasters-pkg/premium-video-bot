from typing import List, Dict, Optional
from utils.database import Database
from utils.logger import broadcast_logger
import time


class BroadcastService:
    """Broadcast message service"""
    
    def __init__(self, db: Database):
        self.db = db
        self.is_broadcasting = False
        self.is_paused = False
        self.broadcast_stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "failed_users": []
        }
    
    def start_broadcast(self, message: str, target: str = "all") -> Dict:
        """Start broadcast
        
        Args:
            message: Message to broadcast
            target: 'all', 'active', or list of user IDs
        """
        self.is_broadcasting = True
        self.is_paused = False
        self.broadcast_stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "failed_users": []
        }
        
        broadcast_logger.info(f"Broadcast started. Target: {target}")
        return {
            "status": "started",
            "message": message,
            "target": target
        }
    
    def pause_broadcast(self) -> None:
        """Pause broadcast"""
        self.is_paused = True
        broadcast_logger.info("Broadcast paused")
    
    def resume_broadcast(self) -> None:
        """Resume broadcast"""
        self.is_paused = False
        broadcast_logger.info("Broadcast resumed")
    
    def cancel_broadcast(self) -> None:
        """Cancel broadcast"""
        self.is_broadcasting = False
        self.is_paused = False
        broadcast_logger.info(f"Broadcast cancelled. Stats: {self.broadcast_stats}")
    
    def record_success(self, user_id: int) -> None:
        """Record successful send"""
        self.broadcast_stats["success"] += 1
    
    def record_failure(self, user_id: int, reason: str) -> None:
        """Record failed send"""
        self.broadcast_stats["failed"] += 1
        self.broadcast_stats["failed_users"].append({
            "user_id": user_id,
            "reason": reason
        })
    
    def get_stats(self) -> Dict:
        """Get broadcast statistics"""
        return self.broadcast_stats.copy()
