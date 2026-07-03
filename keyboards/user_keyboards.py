from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import List
from config import BOT_USERNAME


def get_main_menu(user_id: int) -> ReplyKeyboardMarkup:
    """Get main menu keyboard"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    
    # Add standard buttons
    markup.add(KeyboardButton("🎬 Premium Video"))
    markup.add(
        KeyboardButton("👤 My Profile"),
        KeyboardButton("👥 My Referral")
    )
    markup.add(KeyboardButton("💎 My Points"))
    markup.add(
        KeyboardButton("📢 Updates Channel"),
        KeyboardButton("📞 Contact Admin")
    )
    
    return markup


def get_profile_menu() -> InlineKeyboardMarkup:
    """Get profile inline menu"""
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅ Back", callback_data="back_to_menu"))
    return markup


def get_referral_menu() -> InlineKeyboardMarkup:
    """Get referral inline menu"""
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📋 History", callback_data="ref_history"),
        InlineKeyboardButton("📊 Stats", callback_data="ref_stats")
    )
    markup.add(InlineKeyboardButton("⬅ Back", callback_data="back_to_menu"))
    return markup


def get_video_menu() -> InlineKeyboardMarkup:
    """Get video selection menu"""
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("▶️ Next Video", callback_data="next_video"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel_video")
    )
    return markup


def get_force_join_menu(channels: List[str]) -> InlineKeyboardMarkup:
    """Get force join verification menu"""
    markup = InlineKeyboardMarkup()
    
    if channels:
        for i, channel in enumerate(channels):
            channel_name = channel.replace("-100", "@").lstrip("@")
            markup.add(
                InlineKeyboardButton(
                    f"Join: {channel_name}",
                    url=f"https://t.me/{channel_name}"
                )
            )
        markup.add(
            InlineKeyboardButton(
                "✅ I Joined",
                callback_data="verify_membership"
            )
        )
    
    return markup


def get_admin_custom_buttons(buttons: List[dict]) -> ReplyKeyboardMarkup:
    """Add admin custom buttons to menu"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    
    # Add buttons in rows of 2
    for i in range(0, len(buttons), 2):
        row = []
        for j in range(2):
            if i + j < len(buttons):
                button = buttons[i + j]
                if button.get('is_active', True):
                    row.append(KeyboardButton(button['label']))
        if row:
            markup.add(*row)
    
    return markup
