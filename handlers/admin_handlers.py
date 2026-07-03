from telebot import TeleBot
from telebot.types import Message
from config import ADMIN_IDS, OWNER_ID
from utils.database import Database
from services.user_service import UserService
from services.video_service import VideoService
from services.payment_service import PaymentService
from keyboards.admin_keyboards import get_admin_menu
from utils.logger import bot_logger, error_logger
from models.payment import PaymentStatus, PaymentMethod
import csv
from datetime import datetime
import os
import uuid


class AdminHandlers:
    """Admin message handlers"""
    
    def __init__(self, bot: TeleBot, db: Database):
        self.bot = bot
        self.db = db
        self.user_service = UserService(db)
        self.video_service = VideoService(db)
        self.payment_service = PaymentService(db)
        self.admin_states = {}  # Track admin states for multi-step operations
        self.pending_videos = {}  # Track videos being uploaded
        self.register_handlers()
    
    def register_handlers(self) -> None:
        """Register all admin handlers"""
        self.bot.message_handler(commands=['admin'])(self.handle_admin_panel)
        self.bot.message_handler(regexp=r'⬅ User Menu')(self.handle_user_menu)
        self.bot.message_handler(regexp=r'➕ Upload Video')(self.handle_upload_video)
        self.bot.message_handler(content_types=['video'])(self.handle_video_file)
        self.bot.message_handler(commands=['done'])(self.handle_upload_done)
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
        self.bot.message_handler(regexp=r'💳 Payments')(self.handle_payments)
        self.bot.message_handler(regexp=r'🔗 Force Join')(self.handle_force_join)
        self.bot.message_handler(func=lambda m: self.is_admin(m.from_user.id))(self.handle_admin_text)
    
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
        """Handle video upload initiation"""
        if not self.is_admin(message.from_user.id):
            return
        
        self.admin_states[message.from_user.id] = 'waiting_for_video'
        self.pending_videos[message.from_user.id] = []
        
        msg = self.bot.send_message(
            message.chat.id,
            "📹 **Upload Video**\n\n"
            "Send video file(s). You can send multiple videos in sequence.\n\n"
            "After each video, you can add a caption.\n\n"
            "Send /done when finished uploading all videos.",
            parse_mode='Markdown'
        )
        bot_logger.info(f"Admin {message.from_user.id} started video upload")
    
    def handle_video_file(self, message: Message) -> None:
        """Handle video file upload"""
        try:
            if not self.is_admin(message.from_user.id):
                return
            
            if message.from_user.id not in self.admin_states or \
               self.admin_states[message.from_user.id] != 'waiting_for_video':
                self.bot.send_message(
                    message.chat.id,
                    "❌ Use '📹 Upload Video' button first."
                )
                return
            
            # Get video information
            video = message.video
            if not video:
                self.bot.send_message(message.chat.id, "❌ Invalid video file.")
                return
            
            # Check for duplicate
            if self.video_service.get_video_by_unique_id(video.file_unique_id):
                self.bot.send_message(
                    message.chat.id,
                    "⚠️ This video already exists. Skipping duplicate."
                )
                return
            
            # Store video temporarily
            video_data = {
                'file_id': video.file_id,
                'file_unique_id': video.file_unique_id,
                'caption': message.caption or '',
                'duration': video.duration,
                'uploaded_by': message.from_user.id
            }
            
            if message.from_user.id not in self.pending_videos:
                self.pending_videos[message.from_user.id] = []
            
            self.pending_videos[message.from_user.id].append(video_data)
            
            self.bot.send_message(
                message.chat.id,
                f"✅ Video {len(self.pending_videos[message.from_user.id])} received.\n\n"
                f"📌 Duration: {video.duration}s\n"
                f"📝 Caption: {video_data['caption'] or '(None)'}\n\n"
                f"Send next video or /done to finish."
            )
            
            bot_logger.info(f"Admin {message.from_user.id} uploaded video {video.file_unique_id}")
        
        except Exception as e:
            error_logger.error(f"Error in handle_video_file: {e}")
            self.bot.send_message(message.chat.id, f"❌ Error: {str(e)}")
    
    def handle_upload_done(self, message: Message) -> None:
        """Handle upload completion"""
        try:
            if not self.is_admin(message.from_user.id):
                return
            
            if message.from_user.id not in self.pending_videos:
                self.bot.send_message(message.chat.id, "❌ No videos to upload.")
                return
            
            videos = self.pending_videos[message.from_user.id]
            if not videos:
                self.bot.send_message(message.chat.id, "❌ No videos uploaded.")
                return
            
            # Save all videos to database
            saved_count = 0
            for video_data in videos:
                try:
                    success = self.video_service.add_video(
                        video_data['file_id'],
                        video_data['file_unique_id'],
                        video_data['caption'],
                        message.from_user.id
                    )
                    if success:
                        saved_count += 1
                except Exception as e:
                    error_logger.error(f"Failed to save video: {e}")
            
            # Clear pending videos
            del self.pending_videos[message.from_user.id]
            self.admin_states[message.from_user.id] = None
            
            self.bot.send_message(
                message.chat.id,
                f"✅ **Upload Complete**\n\n"
                f"📊 Videos saved: {saved_count}/{len(videos)}\n\n"
                f"Total videos in database: {len(self.video_service.get_videos())}",
                parse_mode='Markdown'
            )
            
            bot_logger.info(f"Admin {message.from_user.id} completed upload: {saved_count} videos")
        
        except Exception as e:
            error_logger.error(f"Error in handle_upload_done: {e}")
            self.bot.send_message(message.chat.id, f"❌ Error: {str(e)}")
    
    def handle_video_stats(self, message: Message) -> None:
        """Handle video statistics"""
        if not self.is_admin(message.from_user.id):
            return
        
        try:
            stats = self.video_service.get_video_stats()
            videos = self.video_service.get_videos()
            
            stats_text = f"""🎞 **Video Statistics**

📊 Total Videos: `{stats.get('total_videos', 0)}`
📅 Last Uploaded: `{stats.get('last_uploaded', 'N/A')}`

📋 Recent Videos:
"""
            
            for i, video in enumerate(videos[-10:], 1):
                caption = video.caption[:30] if video.caption else "(No caption)"
                stats_text += f"\n{i}. {caption}... (ID: {video.file_unique_id[:10]}...)"
            
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
        
        try:
            videos = self.video_service.get_videos()
            if not videos:
                self.bot.send_message(message.chat.id, "❌ No videos to delete.")
                return
            
            text = "🎬 **Videos List**\n\n"
            for i, video in enumerate(videos):
                caption = video.caption[:30] if video.caption else "(No caption)"
                text += f"{i}. {caption}...\n"
            
            text += "\n\n📝 Reply with video index to delete (0-based)"
            
            self.bot.send_message(message.chat.id, text, parse_mode='Markdown')
            self.admin_states[message.from_user.id] = 'waiting_for_delete_index'
        
        except Exception as e:
            bot_logger.error(f"Error in handle_delete_video: {e}")
            self.bot.send_message(message.chat.id, "❌ An error occurred.")
    
    def handle_statistics(self, message: Message) -> None:
        """Handle general statistics"""
        if not self.is_admin(message.from_user.id):
            return
        
        try:
            users = self.user_service.get_all_users()
            active_users = self.user_service.get_active_users()
            total_points = sum(u.points for u in users)
            total_referrals = sum(u.referrals for u in users)
            videos = self.video_service.get_videos()
            
            # Payment statistics
            all_payments = self.payment_service.get_all_payments()
            approved_payments = [p for p in all_payments if p.status == PaymentStatus.APPROVED.value]
            pending_payments = [p for p in all_payments if p.status == PaymentStatus.PENDING.value]
            
            total_revenue = sum(p.amount for p in approved_payments)
            
            stats_text = f"""📊 **Global Statistics**

👥 Users:
  • Total: `{len(users)}`
  • Active: `{len(active_users)}`
  • Banned: `{len(users) - len(active_users)}`

💎 Points:
  • Total: `{total_points}`
  • Referrals: `{total_referrals}`

🎬 Content:
  • Videos: `{len(videos)}`

💰 Payments:
  • Total Revenue: `₹{total_revenue}`
  • Approved: `{len(approved_payments)}`
  • Pending: `{len(pending_payments)}`
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
            "📝 Enter user ID and points (format: `user_id points`)",
            parse_mode='Markdown'
        )
        self.admin_states[message.from_user.id] = 'waiting_for_add_points'
    
    def handle_remove_points(self, message: Message) -> None:
        """Handle removing points"""
        if not self.is_admin(message.from_user.id):
            return
        
        msg = self.bot.send_message(
            message.chat.id,
            "📝 Enter user ID and points (format: `user_id points`)",
            parse_mode='Markdown'
        )
        self.admin_states[message.from_user.id] = 'waiting_for_remove_points'
    
    def handle_user_points(self, message: Message) -> None:
        """Handle checking user points"""
        if not self.is_admin(message.from_user.id):
            return
        
        msg = self.bot.send_message(
            message.chat.id,
            "🔍 Enter user ID:",
            parse_mode='Markdown'
        )
        self.admin_states[message.from_user.id] = 'waiting_for_user_id'
    
    def handle_broadcast(self, message: Message) -> None:
        """Handle broadcast"""
        if not self.is_admin(message.from_user.id):
            return
        
        msg = self.bot.send_message(
            message.chat.id,
            "📢 Enter broadcast message:",
            parse_mode='Markdown'
        )
        self.admin_states[message.from_user.id] = 'waiting_for_broadcast'
    
    def handle_ban_user(self, message: Message) -> None:
        """Handle banning user"""
        if not self.is_admin(message.from_user.id):
            return
        
        msg = self.bot.send_message(
            message.chat.id,
            "🚫 Enter user ID to ban:",
            parse_mode='Markdown'
        )
        self.admin_states[message.from_user.id] = 'waiting_for_ban_user'
    
    def handle_unban_user(self, message: Message) -> None:
        """Handle unbanning user"""
        if not self.is_admin(message.from_user.id):
            return
        
        msg = self.bot.send_message(
            message.chat.id,
            "✅ Enter user ID to unban:",
            parse_mode='Markdown'
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
                name = user.name or user.username or f'User {user.id}'
                text += f"{i}. {name} - {user.referrals} referrals\n"
            
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
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
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
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
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
                    caption=f"📁 Referral Export: {sum(1 for u in users if u.referrals > 0)} referrers"
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
    
    def handle_payments(self, message: Message) -> None:
        """Handle payment management"""
        if not self.is_admin(message.from_user.id):
            return
        
        try:
            all_payments = self.payment_service.get_all_payments()
            pending = [p for p in all_payments if p.status == PaymentStatus.PENDING.value]
            
            if not pending:
                self.bot.send_message(message.chat.id, "✅ No pending payments.")
                return
            
            text = "💳 **Pending Payments**\n\n"
            for i, payment in enumerate(pending[:10], 1):
                user = self.user_service.get_user(payment.user_id)
                user_name = user.name if user else f"User {payment.user_id}"
                text += f"{i}. {user_name}\n"
                text += f"   Amount: ₹{payment.amount}\n"
                text += f"   Method: {payment.method.upper()}\n"
                text += f"   ID: {payment.payment_id}\n\n"
            
            self.bot.send_message(message.chat.id, text, parse_mode='Markdown')
        
        except Exception as e:
            bot_logger.error(f"Error in handle_payments: {e}")
            self.bot.send_message(message.chat.id, "❌ An error occurred.")
    
    def handle_force_join(self, message: Message) -> None:
        """Handle force join management"""
        if not self.is_admin(message.from_user.id):
            return
        
        try:
            from keyboards.admin_keyboards import get_force_join_menu
            self.bot.send_message(
                message.chat.id,
                "🔗 **Force Join Channels**",
                parse_mode='Markdown',
                reply_markup=get_force_join_menu()
            )
        except Exception as e:
            bot_logger.error(f"Error in handle_force_join: {e}")
    
    def handle_admin_text(self, message: Message) -> None:
        """Handle admin text input for states"""
        if not self.is_admin(message.from_user.id):
            return
        
        state = self.admin_states.get(message.from_user.id)
        
        if state == 'waiting_for_delete_index':
            try:
                index = int(message.text)
                if self.video_service.delete_video(index):
                    self.bot.send_message(message.chat.id, "✅ Video deleted.")
                else:
                    self.bot.send_message(message.chat.id, "❌ Invalid video index.")
                self.admin_states[message.from_user.id] = None
            except ValueError:
                self.bot.send_message(message.chat.id, "❌ Invalid input.")
        
        elif state == 'waiting_for_add_points':
            try:
                parts = message.text.split()
                user_id = int(parts[0])
                points = int(parts[1])
                
                if self.user_service.add_points(user_id, points):
                    self.bot.send_message(message.chat.id, f"✅ Added {points} points to user {user_id}.")
                else:
                    self.bot.send_message(message.chat.id, "❌ User not found.")
                self.admin_states[message.from_user.id] = None
            except (ValueError, IndexError):
                self.bot.send_message(message.chat.id, "❌ Invalid format. Use: user_id points")
        
        elif state == 'waiting_for_remove_points':
            try:
                parts = message.text.split()
                user_id = int(parts[0])
                points = int(parts[1])
                
                if self.user_service.remove_points(user_id, points):
                    self.bot.send_message(message.chat.id, f"✅ Removed {points} points from user {user_id}.")
                else:
                    self.bot.send_message(message.chat.id, "❌ Failed to remove points.")
                self.admin_states[message.from_user.id] = None
            except (ValueError, IndexError):
                self.bot.send_message(message.chat.id, "❌ Invalid format. Use: user_id points")
        
        elif state == 'waiting_for_user_id':
            try:
                user_id = int(message.text)
                user = self.user_service.get_user(user_id)
                
                if user:
                    text = f"""👤 **User Points**

User ID: `{user.id}`
Name: `{user.name}`
Points: `{user.points}`
Free Videos: `{user.free_videos_left}`
Unlock Videos: `{user.videos_remaining}`
Referrals: `{user.referrals}`
"""
                    self.bot.send_message(message.chat.id, text, parse_mode='Markdown')
                else:
                    self.bot.send_message(message.chat.id, "❌ User not found.")
                self.admin_states[message.from_user.id] = None
            except ValueError:
                self.bot.send_message(message.chat.id, "❌ Invalid user ID.")
        
        elif state == 'waiting_for_broadcast':
            # TODO: Implement broadcast
            self.bot.send_message(message.chat.id, "📢 Broadcast feature coming soon.")
            self.admin_states[message.from_user.id] = None
        
        elif state == 'waiting_for_ban_user':
            try:
                user_id = int(message.text)
                if self.user_service.ban_user(user_id):
                    self.bot.send_message(message.chat.id, f"✅ User {user_id} banned.")
                else:
                    self.bot.send_message(message.chat.id, "❌ User not found.")
                self.admin_states[message.from_user.id] = None
            except ValueError:
                self.bot.send_message(message.chat.id, "❌ Invalid user ID.")
        
        elif state == 'waiting_for_unban_user':
            try:
                user_id = int(message.text)
                if self.user_service.unban_user(user_id):
                    self.bot.send_message(message.chat.id, f"✅ User {user_id} unbanned.")
                else:
                    self.bot.send_message(message.chat.id, "❌ User not found.")
                self.admin_states[message.from_user.id] = None
            except ValueError:
                self.bot.send_message(message.chat.id, "❌ Invalid user ID.")
