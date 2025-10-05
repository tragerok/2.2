from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_language_keyboard(lang="ru"):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("Русский 🇷🇺", callback_data="set_lang_ru"),
        InlineKeyboardButton("English 🇬🇧", callback_data="set_lang_en")
    )
    return kb
