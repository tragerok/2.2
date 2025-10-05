from aiogram import types
from keyboards.main_menu import get_main_menu
from utils.locale import L
from utils.db import get_user

def register(dp):
    @dp.message_handler(commands=['start'])
    async def start_command(message: types.Message):
        user_id = message.from_user.id
        info = get_user(user_id)
        lang = "ru"
        if info and 'lang' in info and info['lang'] in ['ru', 'en']:
            lang = info['lang']
        await message.answer(L("start_text", lang), reply_markup=get_main_menu(user_id), parse_mode="HTML")
