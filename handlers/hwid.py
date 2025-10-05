from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from utils.db import get_licenses_for_user, set_hwid

class HWIDState(StatesGroup):
    select_license = State()
    enter_hwid = State()

def register(dp):
    @dp.message_handler(lambda msg: msg.text.lower() == "активировать hwid")
    async def choose_license(message: types.Message):
        licenses = get_licenses_for_user(message.from_user.id)
        free_licenses = [lic for lic in licenses if not lic["hwid"]]
        if not free_licenses:
            await message.answer("Нет лицензий для активации HWID.")
            return
        kb = types.InlineKeyboardMarkup()
        for lic in free_licenses:
            txt = f"{lic['program_name']} (до {lic['valid_until'].strftime('%Y-%m-%d')})"
            kb.add(types.InlineKeyboardButton(txt, callback_data=f"hwid_{lic['id']}"))
        await message.answer("Выберите лицензию для HWID:", reply_markup=kb)
        await HWIDState.select_license.set()

    @dp.callback_query_handler(lambda cb: cb.data.startswith("hwid_"), state=HWIDState.select_license)
    async def ask_hwid(cb: types.CallbackQuery, state: FSMContext):
        lic_id = int(cb.data.split("_")[-1])
        await state.update_data(license_id=lic_id)
        await cb.message.edit_text("Введите HWID для выбранной лицензии:")
        await HWIDState.enter_hwid.set()

    @dp.message_handler(state=HWIDState.enter_hwid)
    async def finish_hwid(message: types.Message, state: FSMContext):
        hwid = message.text.strip()
        data = await state.get_data()
        set_hwid(data["license_id"], hwid)
        await message.answer(f"HWID {hwid} успешно активирован для лицензии!")
        await state.finish()
