from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_admin_menu() -> ReplyKeyboardMarkup:
    """Get admin menu keyboard"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    
    markup.add(
        KeyboardButton("➕ Upload Video"),
        KeyboardButton("🎞 Video Stats")
    )
    markup.add(
        KeyboardButton("🗑 Delete Video"),
        KeyboardButton("📊 Statistics")
    )
    markup.add(
        KeyboardButton("➕ Add Points"),
        KeyboardButton("➖ Remove Points")
    )
    markup.add(
        KeyboardButton("📊 User Points"),
        KeyboardButton("📢 Broadcast")
    )
    markup.add(
        KeyboardButton("🚫 Ban User"),
        KeyboardButton("✅ Unban User")
    )
    markup.add(
        KeyboardButton("➕ Add Admin"),
        KeyboardButton("🗑 Remove Admin")
    )
    markup.add(
        KeyboardButton("🔍 Search User"),
        KeyboardButton("📩 DM User")
    )
    markup.add(
        KeyboardButton("🏆 Top Referrers"),
        KeyboardButton("🔎 Referral Details")
    )
    markup.add(
        KeyboardButton("📁 Users CSV"),
        KeyboardButton("📁 Referral CSV")
    )
    markup.add(
        KeyboardButton("💾 Backup Database"),
        KeyboardButton("⚙️ Custom Buttons")
    )
    markup.add(
        KeyboardButton("🔗 Force Join"),
        KeyboardButton("⬅ User Menu")
    )
    
    return markup


def get_custom_buttons_menu() -> ReplyKeyboardMarkup:
    """Get custom buttons management menu"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    
    markup.add(
        KeyboardButton("➕ Add Button"),
        KeyboardButton("📝 Edit Button")
    )
    markup.add(
        KeyboardButton("🗑 Delete Button"),
        KeyboardButton("⬆️ Reorder Buttons")
    )
    markup.add(
        KeyboardButton("🔄 Enable/Disable"),
        KeyboardButton("⬅ Back to Admin")
    )
    
    return markup


def get_force_join_menu() -> ReplyKeyboardMarkup:
    """Get force join management menu"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    
    markup.add(
        KeyboardButton("➕ Add Channel"),
        KeyboardButton("🗑 Remove Channel")
    )
    markup.add(
        KeyboardButton("📋 View Channels"),
        KeyboardButton("🔄 Enable/Disable")
    )
    markup.add(KeyboardButton("⬅ Back to Admin"))
    
    return markup


def get_broadcast_menu() -> InlineKeyboardMarkup:
    """Get broadcast control menu"""
    markup = InlineKeyboardMarkup()
    
    markup.add(
        InlineKeyboardButton("⏸ Pause", callback_data="broadcast_pause"),
        InlineKeyboardButton("▶️ Resume", callback_data="broadcast_resume")
    )
    markup.add(
        InlineKeyboardButton("📊 Report", callback_data="broadcast_report"),
        InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")
    )
    
    return markup
