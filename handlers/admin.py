from aiogram import types
from aiogram.dispatcher import FSMContext
from utils.db import (
    get_user, get_user_by_id, get_users_page, get_balance,
    update_balance, get_total_users, get_active_subscribers, set_balance, get_licenses_for_user,
    get_all_licenses, block_user_by_id, unblock_user_by_id,
    log_admin_action, get_stats, get_all_tariffs, get_tariff_by_id, update_tariff_price
)

ADMIN_IDS = [405261700]  # <-- твой id

def register(dp):
    @dp.message_handler(commands=["admin"])
    async def admin_panel(message: types.Message, state: FSMContext):
        if message.from_user.id not in ADMIN_IDS:
            await message.reply("Нет прав.")
            return
        await admin_menu(message, state)

    async def admin_menu(message_or_cb, state, edit=False):
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("Все пользователи", "Поиск пользователя", "Тарифы", "Статистика", "Выйти из админки")
        if isinstance(message_or_cb, types.CallbackQuery):
            if edit:
                await message_or_cb.message.edit_text("Админ-панель:", reply_markup=None)
                await message_or_cb.message.answer("Админ-панель:", reply_markup=kb)
            else:
                await message_or_cb.message.answer("Админ-панель:", reply_markup=kb)
        else:
            await message_or_cb.answer("Админ-панель:", reply_markup=kb)
        await state.finish()

    @dp.message_handler(lambda msg: msg.text == "Все пользователи")
    async def all_users(message: types.Message, state: FSMContext):
        await state.update_data(page=1)
        await send_users_page(message, 1)

    async def send_users_page(message_or_cb, page):
        # Пагинация на 10 пользователей
        users = get_users_page(offset=(page-1)*10, limit=10)
        total_users = get_total_users()
        active_subs = get_active_subscribers()

        header = f"Страница {page} (всего: {total_users}, с подпиской: {active_subs}):"
        kb = types.InlineKeyboardMarkup()
        for u in users:
            kb.add(types.InlineKeyboardButton(f"ID: {u['id']}", callback_data=f"userpanel_{u['id']}"))
        if page > 1:
            kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"page_{page-1}"))
        if (page)*10 < total_users:
            kb.add(types.InlineKeyboardButton("➡️ Вперед", callback_data=f"page_{page+1}"))
            kb.add(types.InlineKeyboardButton("Меню", callback_data="admin_back"))
        if isinstance(message_or_cb, types.Message):
            await message_or_cb.answer(header, reply_markup=kb)
        else:
            try:
                await message_or_cb.message.edit_text(header, reply_markup=kb)
            except Exception:
                pass

    @dp.callback_query_handler(lambda cb: cb.data.startswith("page_"))
    async def handle_page(cb: types.CallbackQuery, state: FSMContext):
        page = int(cb.data.split("_")[1])
        await state.update_data(page=page)
        await send_users_page(cb, page)

    @dp.message_handler(lambda msg: msg.text.lower() == "поиск пользователя")
    async def ask_search_user(message: types.Message, state: FSMContext):
        await message.answer("Введи ID пользователя:")
        await state.set_state("admin_search_id")

    @dp.message_handler(state="admin_search_id")
    async def process_search_user(message: types.Message, state: FSMContext):
        try:
            user_id = int(message.text.strip())
            print("SEARCH_USER DBG:", user_id)
            user = get_user_by_id(user_id)
            if not user:
                await message.answer("Пользователь не найден.")
            else:
                licenses = get_licenses_for_user(user_id)
                text = (
                    f"ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ\n"
                    f"ID: {user['id']}\n"
                    f"Баланс: {user['balance']}$\n"
                    f"Заблокирован: {user.get('blocked', False)}\n"
                    f"Язык: {user.get('lang', '-')}\n\n"
                    f"Лицензии:\n"
                )
                if not licenses:
                    text += "Нет лицензий.\n"
                else:
                    for lic in licenses:
                        text += (
                            f"{lic.get('id')}: {lic.get('program_name')} | {lic.get('tariff_name')} | "
                            f"{lic.get('hwid','-')} | до {(lic.get('valid_until') or '').strftime('%Y-%m-%d') if lic.get('valid_until') else '-'} | {lic.get('tariff_price','-')}$\n"
                        )
                kb = types.InlineKeyboardMarkup()
                kb.add(types.InlineKeyboardButton("Изменить баланс", callback_data=f"setbal_{user_id}"))
                kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="admin_back"))
                blk = "Разблокировать" if user.get("blocked") else "Заблокировать"
                kb.add(types.InlineKeyboardButton(blk, callback_data=f"{'unblock' if user.get('blocked') else 'block'}_{user_id}"))
                await message.answer(text, reply_markup=kb)
            await state.finish()
        except Exception as e:
            await message.answer(f"Ошибка! Введи числовой ID. {e}")
            await state.finish()
            return

    @dp.callback_query_handler(lambda cb: cb.data == "admin_back", state="*")
    async def admin_back(cb: types.CallbackQuery, state: FSMContext):
        await cb.message.delete()
        await admin_menu(cb, state, edit=False)

    @dp.callback_query_handler(lambda cb: cb.data.startswith("userpanel_"))
    async def user_panel(cb: types.CallbackQuery, state: FSMContext):
        uid = int(cb.data.split("_")[1])
        user = get_user(uid)
        licenses = get_licenses_for_user(uid)
        text = (
            f"ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ\n"
            f"ID: {user['id']}\n"
            f"Баланс: {user['balance']}$\n"
            f"Заблокирован: {user.get('blocked', False)}\n"
            f"Язык: {user.get('lang', '-')}\n\n"
            f"Лицензии:\n"
        )
        if not licenses:
            text += "Нет лицензий.\n"
        else:
            for lic in licenses:
                text += (
                    f"{lic.get('hwid','-')} | до {(lic.get('valid_until') or '').strftime('%Y-%m-%d') if lic.get('valid_until') else '-'} | {lic.get('tariff_price','-')}$\n"
                )
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("Изменить баланс", callback_data=f"setbal_{uid}"))
        kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="admin_back"))
        blk = "Разблокировать" if user.get("blocked") else "Заблокировать"
        kb.add(types.InlineKeyboardButton(blk, callback_data=f"{'unblock' if user.get('blocked') else 'block'}_{uid}"))
        await cb.message.edit_text(text, reply_markup=kb)

    @dp.callback_query_handler(lambda cb: cb.data.startswith("setbal_"))
    async def set_balance_handler(cb: types.CallbackQuery, state: FSMContext):
        uid = int(cb.data.split("_")[1])
        await state.update_data(user_id=uid)
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="admin_back"))
        await cb.message.edit_text("Введи новое значение баланса:", reply_markup=kb)
        await state.set_state("admin_set_sum")

    @dp.message_handler(state="admin_set_sum")
    async def balance_sum(message: types.Message, state: FSMContext):
        if message.text.strip() == "⬅️ Назад":
            await admin_menu(message, state)
            return
        data = await state.get_data()
        uid = data.get('user_id')
        try:
            target = int(message.text)
        except:
            await message.answer("Ошибка — введи целое число!")
            return
        old_balance = get_balance(uid)
        set_balance(uid, target)
        log_admin_action(message.from_user.id, uid, old_balance, target)
        await message.answer(f"Баланс пользователя {uid} был {old_balance}$, стал {target}$")
        await state.finish()
        await admin_menu(message, state)

    @dp.callback_query_handler(lambda cb: cb.data.startswith("block_"))
    async def blocked(cb: types.CallbackQuery, state: FSMContext):
        uid = int(cb.data.split("_")[1])
        block_user_by_id(uid)
        await cb.message.edit_text(f"Пользователь {uid} заблокирован.", reply_markup=None)
        await admin_menu(cb, state)

    @dp.callback_query_handler(lambda cb: cb.data.startswith("unblock_"))
    async def unblocked(cb: types.CallbackQuery, state: FSMContext):
        uid = int(cb.data.split("_")[1])
        unblock_user_by_id(uid)
        await cb.message.edit_text(f"Пользователь {uid} разблокирован.", reply_markup=None)
        await admin_menu(cb, state)

    @dp.message_handler(lambda msg: msg.text == "Тарифы")
    async def all_tariffs(message: types.Message):
        tariffs = get_all_tariffs()
        kb = types.InlineKeyboardMarkup()
        for t in tariffs:
            kb.add(types.InlineKeyboardButton(
                f"{t['name']} ({t['days']} дней) — {t['price']}$", callback_data=f"tariff_{t['id']}"
            ))
        kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="admin_back"))
        await message.answer("Выбери тариф для редактирования:", reply_markup=kb)

    @dp.callback_query_handler(lambda cb: cb.data.startswith("tariff_"))
    async def tariff_panel(cb: types.CallbackQuery, state: FSMContext):
        tid = int(cb.data.split("_")[1])
        tariff = get_tariff_by_id(tid)
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("Изменить цену", callback_data=f"editprice_{tid}"))
        kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="admin_back"))
        await cb.message.edit_text(
            f"Тариф: {tariff['name']}\nДней: {tariff['days']}\nЦена: {tariff['price']}",
            reply_markup=kb
        )

    @dp.callback_query_handler(lambda cb: cb.data.startswith("editprice_"))
    async def edit_tariff_price(cb: types.CallbackQuery, state: FSMContext):
        tid = int(cb.data.split("_")[1])
        await state.update_data(tariff_id=tid)
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="admin_back"))
        await cb.message.edit_text("Введи новую цену для тарифа:", reply_markup=kb)
        await state.set_state("edit_tariff_price")

    @dp.message_handler(state="edit_tariff_price")
    async def set_tariff_price(message: types.Message, state: FSMContext):
        data = await state.get_data()
        tid = data.get('tariff_id')
        try:
            price = int(message.text)
        except:
            await message.answer("Ошибка — введи число!")
            return
        update_tariff_price(tid, price)
        await message.answer(f"Цена тарифа ID {tid} обновлена на {price}$")
        await state.finish()

    @dp.message_handler(lambda msg: msg.text == "Статистика")
    async def stats(message: types.Message, state: FSMContext):
        day_count, day_money = get_stats(1)
        week_count, week_money = get_stats(7)
        month_count, month_money = get_stats(30)
        text = (
            "Статистика:\n"
            f"Сегодня: {day_count} / {day_money}$\n"
            f"7 дней: {week_count} / {week_money}$\n"
            f"Месяц: {month_count} / {month_money}$"
        )
        await message.answer(text)

    @dp.message_handler(lambda msg: msg.text == "Выйти из админки")
    async def exit_admin(message: types.Message, state: FSMContext):
        await message.answer("🚪 Выход из админ-панели", reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
