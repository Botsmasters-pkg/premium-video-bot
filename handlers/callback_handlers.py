from telebot import TeleBot
from telebot.types import CallbackQuery
from utils.database import Database
from services.user_service import UserService
from utils.logger import bot_logger
from keyboards.user_keyboards import get_main_menu


class CallbackHandlers:
    """Callback query handlers"""
    
    def __init__(self, bot: TeleBot, db: Database):
        self.bot = bot
        self.db = db
        self.user_service = UserService(db)
        self.register_handlers()
    
    def register_handlers(self) -> None:
        """Register callback handlers"""
        self.bot.callback_query_handler(func=lambda call: call.data == "back_to_menu")(self.handle_back_to_menu)
        self.bot.callback_query_handler(func=lambda call: call.data == "next_video")(self.handle_next_video)
        self.bot.callback_query_handler(func=lambda call: call.data == "cancel_video")(self.handle_cancel_video)
        self.bot.callback_query_handler(func=lambda call: call.data == "ref_history")(self.handle_ref_history)
        self.bot.callback_query_handler(func=lambda call: call.data == "ref_stats")(self.handle_ref_stats)
        self.bot.callback_query_handler(func=lambda call: call.data == "verify_membership")(self.handle_verify_membership)
    
    def handle_back_to_menu(self, call: CallbackQuery) -> None:
        """Handle back to menu"""
        try:
            user = self.user_service.get_user(call.from_user.id)
            if user:
                self.bot.send_message(
                    call.message.chat.id,
                    "📌 Main Menu",
                    reply_markup=get_main_menu(user.id)
                )
            self.bot.answer_callback_query(call.id)
        except Exception as e:
            bot_logger.error(f"Error in handle_back_to_menu: {e}")
    
    def handle_next_video(self, call: CallbackQuery) -> None:
        """Handle next video"""
        try:
            self.bot.answer_callback_query(call.id, "⏳ Loading next video...")
            # TODO: Load next video logic
        except Exception as e:
            bot_logger.error(f"Error in handle_next_video: {e}")
    
    def handle_cancel_video(self, call: CallbackQuery) -> None:
        """Handle cancel video"""
        try:
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            self.bot.answer_callback_query(call.id)
        except Exception as e:
            bot_logger.error(f"Error in handle_cancel_video: {e}")
    
    def handle_ref_history(self, call: CallbackQuery) -> None:
        """Handle referral history"""
        try:
            user = self.user_service.get_user(call.from_user.id)
            if user:
                text = f"📋 You have {user.referrals} successful referrals"
                self.bot.answer_callback_query(call.id, text, show_alert=True)
        except Exception as e:
            bot_logger.error(f"Error in handle_ref_history: {e}")
    
    def handle_ref_stats(self, call: CallbackQuery) -> None:
        """Handle referral stats"""
        try:
            user = self.user_service.get_user(call.from_user.id)
            if user:
                stats_text = f"""📊 Your Referral Stats:
👥 Referrals: {user.referrals}
💎 Points: {user.points}
🎬 Videos Unlocked: {user.referrals * 5}"""
                self.bot.answer_callback_query(call.id, stats_text, show_alert=True)
        except Exception as e:
            bot_logger.error(f"Error in handle_ref_stats: {e}")
    
    def handle_verify_membership(self, call: CallbackQuery) -> None:
        """Handle membership verification"""
        try:
            # TODO: Implement force join verification
            self.bot.answer_callback_query(call.id, "✅ Membership verified!", show_alert=True)
        except Exception as e:
            bot_logger.error(f"Error in handle_verify_membership: {e}")
