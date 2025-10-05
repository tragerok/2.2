from aiogram import types
from keyboards.main_menu import get_main_menu
from config import SUPPORT_TAGS
from utils.db import get_user
from utils.locale import L

def register(dp):
    @dp.message_handler(lambda msg: msg.text in [L("main_menu_support", "ru"), L("main_menu_support", "en")])
    async def contacts(message: types.Message):
        user = get_user(message.from_user.id)
        lang = user.get('lang', 'ru')
        reply = (
            "📋 <b>Техническая поддержка</b>\n"
            "Если возникли вопросы или нужна помощь — пишите сюда:\n"
        ) if lang == "ru" else (
            "📋 <b>Support</b>\n"
            "If you have questions or need help — contact us:\n"
        )
        reply += " ".join(SUPPORT_TAGS)
        await message.answer(reply, reply_markup=get_main_menu(message.from_user.id), parse_mode="HTML", disable_web_page_preview=True)
