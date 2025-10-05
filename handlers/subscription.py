from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.main_menu import get_main_menu
from keyboards.subscription import get_programs_keyboard, get_tariffs_keyboard, get_hwid_keyboard
from utils.db import get_user, get_balance, update_balance, get_all_programs, get_tariffs_for_program, add_license, get_tariff_by_id
from utils.locale import L
from datetime import datetime, timedelta

class LicenseState(StatesGroup):
    choose_program = State()
    choose_tariff = State()
    enter_hwid = State()

def register(dp):
    @dp.message_handler(lambda msg: msg.text in [L("main_menu_buy_license", "ru"), L("main_menu_buy_license", "en")])
    async def start_license(message: types.Message):
        user_id = message.from_user.id
        user = get_user(user_id)
        lang = user.get('lang', 'ru')
        programs = get_all_programs()
        if not programs:
            await message.answer("Нет доступных программ." if lang == "ru" else "No available programs.")
            return
        kb = get_programs_keyboard(programs, lang)
        await message.answer("Выберите программу:" if lang == "ru" else "Choose program:", reply_markup=kb)
        await LicenseState.choose_program.set()

    @dp.callback_query_handler(lambda cb: cb.data.startswith("sub_prog_"), state=LicenseState.choose_program)
    async def program_select_cb(cb: types.CallbackQuery, state: FSMContext):
        program_id = int(cb.data.replace("sub_prog_", ""))
        user = get_user(cb.from_user.id)
        lang = user.get('lang', 'ru')
        tariffs = get_tariffs_for_program(program_id)
        kb = get_tariffs_keyboard(tariffs, lang)
        await cb.message.edit_text("Выберите тариф:" if lang == "ru" else "Choose tariff:", reply_markup=kb)
        await state.set_state(LicenseState.choose_tariff.state)
        await state.update_data(program_id=program_id)
        await cb.answer()

    @dp.callback_query_handler(lambda cb: cb.data.startswith("tariff_"), state=LicenseState.choose_tariff)
    async def tariff_select_cb(cb: types.CallbackQuery, state: FSMContext):
        tariff_id = int(cb.data.replace("tariff_", ""))
        user = get_user(cb.from_user.id)
        lang = user.get('lang', 'ru')
        await cb.message.edit_text(
            "Введите HWID (идентификатор устройства):" if lang == "ru" else "Enter your HWID:",
            reply_markup=get_hwid_keyboard(lang)
        )
        await state.set_state(LicenseState.enter_hwid.state)
        await state.update_data(tariff_id=tariff_id)
        await cb.answer()

    @dp.message_handler(state=LicenseState.enter_hwid)
    async def enter_hwid_step(message: types.Message, state: FSMContext):
        data = await state.get_data()
        program_id = data.get('program_id')
        tariff_id = data.get('tariff_id')

        from utils.db import get_tariff_by_id
        tariff = get_tariff_by_id(tariff_id)
        hwid = message.text
        valid_until = datetime.now() + timedelta(days=tariff['days'])

        tariff = get_tariff_by_id(tariff_id)
        price = tariff['price']
        balance = get_balance(message.from_user.id)
        if balance < price:
            await message.answer("Недостаточно средств!", reply_markup=get_main_menu(message.from_user.id))
            await state.finish()
            return

        update_balance(message.from_user.id, balance - price)
        add_license(message.from_user.id, program_id, hwid, valid_until, tariff_id)
        user = get_user(message.from_user.id)
        lang = user.get('lang', 'ru')
        await message.answer(L("buy_success", lang), reply_markup=get_main_menu(message.from_user.id))
        await state.finish()

    @dp.callback_query_handler(lambda cb: "back" in cb.data, state="*")
    async def sub_back_callback(cb: types.CallbackQuery, state: FSMContext):
        await cb.message.answer("Главное меню.", reply_markup=get_main_menu(cb.from_user.id))
        await state.finish()
        await cb.answer()
