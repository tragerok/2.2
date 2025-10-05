from aiogram import types
from keyboards.main_menu import get_main_menu
from utils.db import get_user, update_balance
from utils.locale import L

def register(dp):
    @dp.message_handler(lambda msg: msg.text in [L("main_menu_topup", "ru"), L("main_menu_topup", "en")])
    async def balance(message: types.Message):
        user = get_user(message.from_user.id)
        lang = user.get('lang', 'ru')
        # update_balance(message.from_user.id, 10) # пример если надо пополнение
        reply = L("balance_text", lang).format(balance=user.get('balance', 0))
        await message.answer(reply, reply_markup=get_main_menu(message.from_user.id), parse_mode="HTML")
