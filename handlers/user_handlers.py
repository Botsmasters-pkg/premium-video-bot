from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from config import BOT_USERNAME
from utils.database import Database
from services.user_service import UserService
from services.video_service import VideoService
from keyboards.user_keyboards import (
    get_main_menu, get_profile_menu, get_referral_menu, 
    get_video_menu, get_force_join_menu
)
from utils.logger import bot_logger


class UserHandlers:
    """User message handlers"""
    
    def __init__(self, bot: TeleBot, db: Database):
        self.bot = bot
        self.db = db
        self.user_service = UserService(db)
        self.video_service = VideoService(db)
        self.register_handlers()
    
    def register_handlers(self) -> None:
        """Register all user handlers"""
        self.bot.message_handler(commands=['start'])(self.handle_start)
        self.bot.message_handler(regexp=r'🎬 Premium Video')(self.handle_watch_video)
        self.bot.message_handler(regexp=r'👤 My Profile')(self.handle_profile)
        self.bot.message_handler(regexp=r'👥 My Referral')(self.handle_referral)
        self.bot.message_handler(regexp=r'💎 My Points')(self.handle_points)
        self.bot.message_handler(regexp=r'📢 Updates Channel')(self.handle_updates)
        self.bot.message_handler(regexp=r'📞 Contact Admin')(self.handle_contact)
    
    def handle_start(self, message: Message) -> None:
        """Handle /start command"""
        try:
            user = self.user_service.get_or_create_user(
                message.from_user.id,
                message.from_user.username or "",
                message.from_user.first_name or ""
            )
            
            # Check for referral
            args = message.text.split()
            if len(args) > 1 and args[1].startswith('ref_'):
                try:
                    ref_user_id = int(args[1].replace('ref_', ''))
                    if ref_user_id != user.id:
                        self.user_service.add_referral(ref_user_id)
                        bot_logger.info(f"Referral: {message.from_user.id} -> {ref_user_id}")
                except ValueError:
                    pass
            
            welcome_text = f"""
👋 Welcome to Premium Video Bot!

🎬 Watch unlimited premium videos
💎 Earn points through referrals
👥 Share your referral link and get rewards

Let's get started!
            """
            
            self.bot.send_message(
                message.chat.id,
                welcome_text,
                reply_markup=get_main_menu(user.id)
            )
        except Exception as e:
            bot_logger.error(f"Error in handle_start: {e}")
            self.bot.send_message(message.chat.id, "❌ An error occurred. Please try again.")
    
    def handle_watch_video(self, message: Message) -> None:
        """Handle watch video button"""
        try:
            user = self.user_service.get_user(message.from_user.id)
            if not user:
                self.bot.send_message(message.chat.id, "❌ User not found.")
                return
            
            # Check force join requirement
            if self.db.is_force_join_enabled():
                channels = self.db.get_force_join_channels()
                if channels:
                    # TODO: Verify membership before sending video
                    pass
            
            # Get next video
            video = self.video_service.get_next_video(user)
            if not video:
                self.bot.send_message(
                    message.chat.id,
                    "🎥 No videos available at the moment. Please try again later or earn points through referrals."
                )
                return
            
            # Update user
            self.user_service.update_user(user)
            
            # Send video
            caption = f"{video.caption}\n\n📊 Videos Watched: {len(user.videos_watched)}"
            self.bot.send_video(
                message.chat.id,
                video.file_id,
                caption=caption,
                reply_markup=get_video_menu()
            )
        except Exception as e:
            bot_logger.error(f"Error in handle_watch_video: {e}")
            self.bot.send_message(message.chat.id, "❌ An error occurred while fetching the video.")
    
    def handle_profile(self, message: Message) -> None:
        """Handle profile button"""
        try:
            user = self.user_service.get_user(message.from_user.id)
            if not user:
                self.bot.send_message(message.chat.id, "❌ User not found.")
                return
            
            profile_text = f"""
👤 **Your Profile**

👤 User ID: `{user.id}`
💎 Current Points: `{user.points}`
🎁 Free Videos Left: `{user.free_videos_left}`
🎬 Unlock Videos: `{user.videos_remaining}`
👥 Total Referrals: `{user.referrals}`
🎥 Videos Watched: `{len(user.videos_watched)}`
📅 Join Date: `{user.join_date}`
            """
            
            self.bot.send_message(
                message.chat.id,
                profile_text,
                parse_mode='Markdown',
                reply_markup=get_profile_menu()
            )
        except Exception as e:
            bot_logger.error(f"Error in handle_profile: {e}")
            self.bot.send_message(message.chat.id, "❌ An error occurred.")
    
    def handle_referral(self, message: Message) -> None:
        """Handle referral button"""
        try:
            user = self.user_service.get_user(message.from_user.id)
            if not user:
                self.bot.send_message(message.chat.id, "❌ User not found.")
                return
            
            referral_link = f"https://t.me/{BOT_USERNAME}?start=ref_{user.id}"
            referral_text = f"""
👥 **Your Referral**

🔗 Referral Link:
`{referral_link}`

📊 Your Stats:
👥 Total Referrals: `{user.referrals}`
💎 Points Earned: `{user.referrals}`
🎬 Videos Unlocked: `{user.referrals * 5}`

🎁 Earn 1 Point for every successful referral!
1 Point = 5 Videos
            """
            
            self.bot.send_message(
                message.chat.id,
                referral_text,
                parse_mode='Markdown',
                reply_markup=get_referral_menu()
            )
        except Exception as e:
            bot_logger.error(f"Error in handle_referral: {e}")
            self.bot.send_message(message.chat.id, "❌ An error occurred.")
    
    def handle_points(self, message: Message) -> None:
        """Handle points button"""
        try:
            user = self.user_service.get_user(message.from_user.id)
            if not user:
                self.bot.send_message(message.chat.id, "❌ User not found.")
                return
            
            points_text = f"""
💎 **Your Points**

💎 Current Points: `{user.points}`
🎬 Remaining Videos: `{user.videos_remaining}`
🎁 Free Videos: `{user.free_videos_left}`

📈 How to Earn Points:
👥 1 Referral = 1 Point
🎬 1 Point = 5 Videos

🔗 Share your referral link to earn points!
            """
            
            self.bot.send_message(
                message.chat.id,
                points_text,
                parse_mode='Markdown'
            )
        except Exception as e:
            bot_logger.error(f"Error in handle_points: {e}")
            self.bot.send_message(message.chat.id, "❌ An error occurred.")
    
    def handle_updates(self, message: Message) -> None:
        """Handle updates channel button"""
        self.bot.send_message(
            message.chat.id,
            "📢 Follow our updates channel for latest news and announcements!\n\n[Updates Channel](https://t.me/your_updates_channel)",
            parse_mode='Markdown'
        )
    
    def handle_contact(self, message: Message) -> None:
        """Handle contact admin button"""
        self.bot.send_message(
            message.chat.id,
            "📞 Contact Admin:\n\n@admin_username\n\nWe're here to help!"
        )
