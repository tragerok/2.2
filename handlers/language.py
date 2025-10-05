from aiogram import types
from keyboards.main_menu import get_main_menu
from keyboards.language import get_language_keyboard
from utils.db import get_user, set_lang
from utils.locale import L

def register(dp):
    @dp.message_handler(lambda msg: msg.text in [L("main_menu_language", "ru"), L("main_menu_language", "en")])
    async def choose_language(message: types.Message):
        user = get_user(message.from_user.id)
        lang = user.get('lang', 'ru')
        await message.answer(
            "Выберите язык:" if lang == "ru" else "Choose language:",
            reply_markup=get_language_keyboard(lang)
        )

    @dp.callback_query_handler(lambda cb: cb.data.startswith("set_lang_"))
    async def set_language_cb(cb: types.CallbackQuery):
        lang_code = cb.data.split("_")[-1]
        set_lang(cb.from_user.id, lang_code)
        # Перечитываем пользователя после обновления языка
        user = get_user(cb.from_user.id)
        updated_lang = user.get('lang', 'ru')
        await cb.message.edit_text(
            "Язык изменён!" if updated_lang == "ru" else "Language updated!",
            reply_markup=get_main_menu(cb.from_user.id)
        )
        await cb.answer()
