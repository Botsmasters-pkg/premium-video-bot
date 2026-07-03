from telebot import TeleBot
from telebot.types import Message
from config import ADMIN_IDS, OWNER_ID
from utils.database import Database
from services.user_service import UserService
from services.video_service import VideoService
from keyboards.admin_keyboards import get_admin_menu
from utils.logger import bot_logger
import csv
from datetime import datetime
import os


class AdminHandlers:
    """Admin message handlers"""
    
    def __init__(self, bot: TeleBot, db: Database):
        self.bot = bot
        self.db = db
        self.user_service = UserService(db)
        self.video_service = VideoService(db)
        self.admin_states = {}  # Track admin states for multi-step operations
        self.register_handlers()
    
    def register_handlers(self) -> None:
        """Register all admin handlers"""
        self.bot.message_handler(commands=['admin'])(self.handle_admin_panel)
        self.bot.message_handler(regexp=r'⬅ User Menu')(self.handle_user_menu)
        self.bot.message_handler(regexp=r'➕ Upload Video')(self.handle_upload_video)
        self.bot.message_handler(regexp=r'🎞 Video Stats')(self.handle_video_stats)
        self.bot.message_handler(regexp=r'🗑 Delete Video')(self.handle_delete_video)
        self.bot.message_handler(regexp=r'📊 Statistics')(self.handle_statistics)
        self.bot.message_handler(regexp=r'➕ Add Points')(self.handle_add_points)
        self.bot.message_handler(regexp=r'➖ Remove Points')(self.handle_remove_points)
        self.bot.message_handler(regexp=r'📊 User Points')(self.handle_user_points)
        self.bot.message_handler(regexp=r'📢 Broadcast')(self.handle_broadcast)
        self.bot.message_handler(regexp=r'🚫 Ban User')(self.handle_ban_user)
        self.bot.message_handler(regexp=r'✅ Unban User')(self.handle_unban_user)
        self.bot.message_handler(regexp=r'🏆 Top Referrers')(self.handle_top_referrers)
        self.bot.message_handler(regexp=r'📁 Users CSV')(self.handle_users_csv)
        self.bot.message_handler(regexp=r'📁 Referral CSV')(self.handle_referral_csv)
        self.bot.message_handler(regexp=r'💾 Backup Database')(self.handle_backup)
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id == OWNER_ID or user_id in ADMIN_IDS
    
    def handle_admin_panel(self, message: Message) -> None:
        """Handle /admin command"""
        if not self.is_admin(message.from_user.id):
            self.bot.send_message(message.chat.id, "❌ You don't have permission to access admin panel.")
            return
        
        self.bot.send_message(
            message.chat.id,
            "🔧 **Admin Panel**\n\nSelect an option:",
            parse_mode='Markdown',
            reply_markup=get_admin_menu()
        )
    
    def handle_user_menu(self, message: Message) -> None:
        """Handle back to user menu"""
        if not self.is_admin(message.from_user.id):
            return
        
        from keyboards.user_keyboards import get_main_menu
        user = self.user_service.get_user(message.from_user.id)
        if user:
            self.bot.send_message(
                message.chat.id,
                "⬅ Returning to user menu...",
                reply_markup=get_main_menu(user.id)
            )
    
    def handle_upload_video(self, message: Message) -> None:
        """Handle video upload"""
        if not self.is_admin(message.from_user.id):
            return
        
        msg = self.bot.send_message(
            message.chat.id,
            "📹 Send the video file(s). You can send multiple videos in sequence. Send /done when finished."
        )
        self.admin_states[message.from_user.id] = 'waiting_for_video'
    
    def handle_video_stats(self, message: Message) -> None:
        """Handle video statistics"""
        if not self.is_admin(message.from_user.id):
            return
        
        try:
            stats = self.video_service.get_video_stats()
            videos = self.video_service.get_videos()
            
            stats_text = f"""
🎞 **Video Statistics**

📊 Total Videos: `{stats.get('total_videos', 0)}`
📅 Last Uploaded: `{stats.get('last_uploaded', 'N/A')}`

📋 Recent Videos:
            """
            
            for i, video in enumerate(videos[-5:], 1):
                stats_text += f"\n{i}. {video.caption[:30]}... (ID: {video.file_unique_id[:10]}...)"
            
            self.bot.send_message(
                message.chat.id,
                stats_text,
                parse_mode='Markdown'
            )
        except Exception as e:
            bot_logger.error(f"Error in handle_video_stats: {e}")
            self.bot.send_message(message.chat.id, "❌ An error occurred.")
    
    def handle_delete_video(self, message: Message) -> None:
        """Handle video deletion"""
        if not self.is_admin(message.from_user.id):
            return
        
        msg = self.bot.send_message(
            message.chat.id,
            "🗑 Enter the video index to delete (0-based):"
        )
        self.admin_states[message.from_user.id] = 'waiting_for_delete_index'
    
    def handle_statistics(self, message: Message) -> None:
        """Handle general statistics"""
        if not self.is_admin(message.from_user.id):
            return
        
        try:
            users = self.user_service.get_all_users()
            active_users = self.user_service.get_active_users()
            total_points = sum(u.points for u in users)
            total_referrals = sum(u.referrals for u in users)
            
            stats_text = f"""
📊 **Global Statistics**

👥 Total Users: `{len(users)}`
✅ Active Users: `{len(active_users)}`
🚫 Banned Users: `{len(users) - len(active_users)}`
💎 Total Points: `{total_points}`
👥 Total Referrals: `{total_referrals}`
🎬 Total Videos: `{len(self.video_service.get_videos())}`
            """
            
            self.bot.send_message(
                message.chat.id,
                stats_text,
                parse_mode='Markdown'
            )
        except Exception as e:
            bot_logger.error(f"Error in handle_statistics: {e}")
            self.bot.send_message(message.chat.id, "❌ An error occurred.")
    
    def handle_add_points(self, message: Message) -> None:
        """Handle adding points"""
        if not self.is_admin(message.from_user.id):
            return
        
        msg = self.bot.send_message(
            message.chat.id,
            "📝 Enter user ID and points (format: user_id points):"
        )
        self.admin_states[message.from_user.id] = 'waiting_for_add_points'
    
    def handle_remove_points(self, message: Message) -> None:
        """Handle removing points"""
        if not self.is_admin(message.from_user.id):
            return
        
        msg = self.bot.send_message(
            message.chat.id,
            "📝 Enter user ID and points (format: user_id points):"
        )
        self.admin_states[message.from_user.id] = 'waiting_for_remove_points'
    
    def handle_user_points(self, message: Message) -> None:
        """Handle checking user points"""
        if not self.is_admin(message.from_user.id):
            return
        
        msg = self.bot.send_message(
            message.chat.id,
            "🔍 Enter user ID:"
        )
        self.admin_states[message.from_user.id] = 'waiting_for_user_id'
    
    def handle_broadcast(self, message: Message) -> None:
        """Handle broadcast"""
        if not self.is_admin(message.from_user.id):
            return
        
        msg = self.bot.send_message(
            message.chat.id,
            "📢 Enter broadcast message:"
        )
        self.admin_states[message.from_user.id] = 'waiting_for_broadcast'
    
    def handle_ban_user(self, message: Message) -> None:
        """Handle banning user"""
        if not self.is_admin(message.from_user.id):
            return
        
        msg = self.bot.send_message(
            message.chat.id,
            "🚫 Enter user ID to ban:"
        )
        self.admin_states[message.from_user.id] = 'waiting_for_ban_user'
    
    def handle_unban_user(self, message: Message) -> None:
        """Handle unbanning user"""
        if not self.is_admin(message.from_user.id):
            return
        
        msg = self.bot.send_message(
            message.chat.id,
            "✅ Enter user ID to unban:"
        )
        self.admin_states[message.from_user.id] = 'waiting_for_unban_user'
    
    def handle_top_referrers(self, message: Message) -> None:
        """Handle showing top referrers"""
        if not self.is_admin(message.from_user.id):
            return
        
        try:
            top_users = self.user_service.get_top_referrers(10)
            
            text = "🏆 **Top 10 Referrers**\n\n"
            for i, user in enumerate(top_users, 1):
                text += f"{i}. {user.name or user.username or f'User {user.id}'} - {user.referrals} referrals\n"
            
            self.bot.send_message(
                message.chat.id,
                text,
                parse_mode='Markdown'
            )
        except Exception as e:
            bot_logger.error(f"Error in handle_top_referrers: {e}")
            self.bot.send_message(message.chat.id, "❌ An error occurred.")
    
    def handle_users_csv(self, message: Message) -> None:
        """Export users to CSV"""
        if not self.is_admin(message.from_user.id):
            return
        
        try:
            users = self.user_service.get_all_users()
            filename = f"users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'User ID', 'Username', 'Name', 'Points', 'Free Videos',
                    'Unlock Videos', 'Referrals', 'Videos Watched', 'Banned', 'Join Date'
                ])
                
                for user in users:
                    writer.writerow([
                        user.id, user.username, user.name, user.points,
                        user.free_videos_left, user.videos_remaining,
                        user.referrals, len(user.videos_watched), user.is_banned, user.join_date
                    ])
            
            with open(filename, 'rb') as f:
                self.bot.send_document(message.chat.id, f, caption=f"📁 Users Export: {len(users)} users")
            
            os.remove(filename)
        except Exception as e:
            bot_logger.error(f"Error in handle_users_csv: {e}")
            self.bot.send_message(message.chat.id, "❌ An error occurred.")
    
    def handle_referral_csv(self, message: Message) -> None:
        """Export referrals to CSV"""
        if not self.is_admin(message.from_user.id):
            return
        
        try:
            users = self.user_service.get_all_users()
            filename = f"referrals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['User ID', 'Username', 'Name', 'Referrals', 'Points Earned'])
                
                for user in sorted(users, key=lambda u: u.referrals, reverse=True):
                    if user.referrals > 0:
                        writer.writerow([
                            user.id, user.username, user.name,
                            user.referrals, user.referrals
                        ])
            
            with open(filename, 'rb') as f:
                self.bot.send_document(
                    message.chat.id, f,
                    caption=f"📁 Referral Export: {sum(1 for u in users if u.referrals > 0)} active referrers"
                )
            
            os.remove(filename)
        except Exception as e:
            bot_logger.error(f"Error in handle_referral_csv: {e}")
            self.bot.send_message(message.chat.id, "❌ An error occurred.")
    
    def handle_backup(self, message: Message) -> None:
        """Handle database backup"""
        if not self.is_admin(message.from_user.id):
            return
        
        try:
            backup_file = self.db.backup()
            self.bot.send_message(message.chat.id, f"✅ Backup created: {backup_file}")
        except Exception as e:
            bot_logger.error(f"Error in handle_backup: {e}")
            self.bot.send_message(message.chat.id, "❌ Backup failed.")
