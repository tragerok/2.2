from aiogram import types
from keyboards.main_menu import get_main_menu
from utils.db import get_user, get_licenses_for_user
from utils.locale import L

def register(dp):
    @dp.message_handler(lambda msg: msg.text in [L("main_menu_profile", "ru"), L("main_menu_profile", "en")])
    async def profile_command(message: types.Message):
        user_id = message.from_user.id
        user = get_user(user_id)
        lang = user.get('lang', 'ru')
        text = f"{L('profile_title', lang)}\n"
        text += f"{L('profile_id', lang)} <code>{user_id}</code>\n"
        text += f"{L('profile_balance', lang)} <b>{user.get('balance', 0)}$</b>\n"

        licenses = get_licenses_for_user(user_id)
        if licenses:
            text += f"\n{L('profile_licenses', lang)}:\n"
            for lic in licenses:
                text += (
                    f"🆔 {lic.get('program_name', '')}\n"
                    f"🚀 {L('until', lang)}: {lic.get('valid_until', '')}\n"
                    f"🔑 HWID: {lic.get('hwid', '')}\n\n"
                )
        else:
            text += f"\n{L('profile_no_licenses', lang)}\n"

        await message.answer(text, parse_mode="HTML", reply_markup=get_main_menu(user_id))
