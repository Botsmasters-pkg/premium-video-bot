import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional
from utils.logger import error_logger
from config import DATABASE_FILE, BACKUP_DIR


class Database:
    """Atomic JSON database with corruption recovery"""
    
    def __init__(self, db_file: str = DATABASE_FILE):
        self.db_file = db_file
        self.lock_file = f"{db_file}.lock"
        self._ensure_db_exists()
    
    def _ensure_db_exists(self) -> None:
        """Ensure database file exists"""
        if not os.path.exists(self.db_file):
            try:
                default_db = {
                    "users": {},
                    "videos": [],
                    "admin_buttons": [],
                    "force_join_channels": [],
                    "force_join_enabled": True,
                    "metadata": {
                        "version": "1.0.0",
                        "last_backup": "",
                        "created_at": datetime.now().isoformat()
                    }
                }
                self._write_json(self.db_file, default_db)
            except Exception as e:
                error_logger.error(f"Failed to create database: {e}")
    
    def _write_json(self, filepath: str, data: Dict) -> None:
        """Atomically write JSON to file"""
        try:
            # Write to temporary file first
            temp_file = f"{filepath}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            if os.path.exists(filepath):
                os.remove(filepath)
            os.rename(temp_file, filepath)
        except Exception as e:
            error_logger.error(f"Failed to write JSON: {e}")
            # Cleanup temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise
    
    def _read_json(self, filepath: str) -> Dict:
        """Read JSON with corruption recovery"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            error_logger.warning(f"Database corrupted: {filepath}. Attempting recovery.")
            return self._recover_from_backup()
        except Exception as e:
            error_logger.error(f"Failed to read JSON: {e}")
            return self._recover_from_backup()
    
    def _recover_from_backup(self) -> Dict:
        """Recover from latest backup"""
        try:
            if not os.path.exists(BACKUP_DIR):
                return self._default_db()
            
            backups = sorted(
                [f for f in os.listdir(BACKUP_DIR) if f.endswith('.json')],
                reverse=True
            )
            
            if not backups:
                return self._default_db()
            
            backup_path = os.path.join(BACKUP_DIR, backups[0])
            with open(backup_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            error_logger.error(f"Recovery failed: {e}")
            return self._default_db()
    
    @staticmethod
    def _default_db() -> Dict:
        """Return default database structure"""
        return {
            "users": {},
            "videos": [],
            "admin_buttons": [],
            "force_join_channels": [],
            "force_join_enabled": True,
            "metadata": {
                "version": "1.0.0",
                "last_backup": "",
                "created_at": datetime.now().isoformat()
            }
        }
    
    def load(self) -> Dict:
        """Load database"""
        return self._read_json(self.db_file)
    
    def save(self, data: Dict) -> None:
        """Save database"""
        self._write_json(self.db_file, data)
    
    def backup(self) -> str:
        """Create backup"""
        try:
            os.makedirs(BACKUP_DIR, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(BACKUP_DIR, f"database_backup_{timestamp}.json")
            
            data = self.load()
            self._write_json(backup_file, data)
            
            # Update last backup time
            data['metadata']['last_backup'] = datetime.now().isoformat()
            self.save(data)
            
            return backup_file
        except Exception as e:
            error_logger.error(f"Backup failed: {e}")
            raise
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user data"""
        data = self.load()
        return data['users'].get(str(user_id))
    
    def save_user(self, user_id: int, user_data: Dict) -> None:
        """Save user data"""
        data = self.load()
        data['users'][str(user_id)] = user_data
        self.save(data)
    
    def get_all_users(self) -> Dict:
        """Get all users"""
        data = self.load()
        return data.get('users', {})
    
    def add_video(self, video_data: Dict) -> None:
        """Add video"""
        data = self.load()
        data['videos'].append(video_data)
        self.save(data)
    
    def get_videos(self) -> List[Dict]:
        """Get all videos"""
        data = self.load()
        return data.get('videos', [])
    
    def delete_video(self, index: int) -> None:
        """Delete video by index"""
        data = self.load()
        if 0 <= index < len(data['videos']):
            del data['videos'][index]
            self.save(data)
    
    def add_admin_button(self, button_data: Dict) -> None:
        """Add admin button"""
        data = self.load()
        data['admin_buttons'].append(button_data)
        self.save(data)
    
    def get_admin_buttons(self) -> List[Dict]:
        """Get admin buttons"""
        data = self.load()
        return data.get('admin_buttons', [])
    
    def update_admin_button(self, button_id: str, button_data: Dict) -> None:
        """Update admin button"""
        data = self.load()
        buttons = data['admin_buttons']
        for i, btn in enumerate(buttons):
            if btn['button_id'] == button_id:
                buttons[i] = button_data
                break
        self.save(data)
    
    def delete_admin_button(self, button_id: str) -> None:
        """Delete admin button"""
        data = self.load()
        data['admin_buttons'] = [
            btn for btn in data['admin_buttons'] if btn['button_id'] != button_id
        ]
        self.save(data)
    
    def add_force_join_channel(self, channel_id: str) -> None:
        """Add force join channel"""
        data = self.load()
        if channel_id not in data['force_join_channels']:
            data['force_join_channels'].append(channel_id)
            self.save(data)
    
    def remove_force_join_channel(self, channel_id: str) -> None:
        """Remove force join channel"""
        data = self.load()
        if channel_id in data['force_join_channels']:
            data['force_join_channels'].remove(channel_id)
            self.save(data)
    
    def get_force_join_channels(self) -> List[str]:
        """Get force join channels"""
        data = self.load()
        return data.get('force_join_channels', [])
    
    def set_force_join_enabled(self, enabled: bool) -> None:
        """Enable/disable force join"""
        data = self.load()
        data['force_join_enabled'] = enabled
        self.save(data)
    
    def is_force_join_enabled(self) -> bool:
        """Check if force join is enabled"""
        data = self.load()
        return data.get('force_join_enabled', True)
