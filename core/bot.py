import telebot
import time
import sys
from config import BOT_TOKEN, POLL_TIMEOUT, LONG_POLLING_TIMEOUT
from utils.logger import bot_logger, error_logger
from utils.database import Database
from handlers.user_handlers import UserHandlers
from handlers.admin_handlers import AdminHandlers
from handlers.callback_handlers import CallbackHandlers


class PremiumVideoBot:
    """Main bot class"""
    
    def __init__(self):
        self.bot = telebot.TeleBot(BOT_TOKEN)
        self.db = Database()
        
        # Initialize handlers
        self.user_handlers = UserHandlers(self.bot, self.db)
        self.admin_handlers = AdminHandlers(self.bot, self.db)
        self.callback_handlers = CallbackHandlers(self.bot, self.db)
        
        bot_logger.info("Premium Video Bot initialized")
    
    def start(self) -> None:
        """Start bot with restart loop"""
        while True:
            try:
                bot_logger.info("Starting polling...")
                self.bot.infinity_polling(
                    skip_pending=True,
                    timeout=POLL_TIMEOUT,
                    long_polling_timeout=LONG_POLLING_TIMEOUT
                )
            except Exception as e:
                error_logger.error(f"Polling error: {e}")
                bot_logger.info("Restarting in 10 seconds...")
                time.sleep(10)
            except KeyboardInterrupt:
                bot_logger.info("Bot stopped by user")
                break


def main():
    """Main entry point"""
    try:
        bot = PremiumVideoBot()
        bot.start()
    except Exception as e:
        error_logger.critical(f"Critical error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
