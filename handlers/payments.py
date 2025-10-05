from aiogram import types
from config import CRYPTOBOT_API_KEY
import requests

CRYPTOBOT_API = "https://pay.crypt.bot/api/"

def create_invoice(amount, currency, user_id):
    data = {
        "asset": currency,
        "amount": str(amount),
        "description": f"Пополнение баланса (user_id {user_id})",
        "hidden_message": str(user_id)
    }
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_API_KEY}
    r = requests.post(CRYPTOBOT_API + "createInvoice", json=data, headers=headers)
    r.raise_for_status()
    result = r.json()["result"]
    return result["invoice_id"], result["pay_url"]

async def payment_entry(message: types.Message):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("CryptoBot (TON, USDT, BTC) +3%", callback_data="pay_cryptobot"))
    await message.answer("💸 Выберите способ пополнения баланса:", reply_markup=kb)

async def cryptobot_sum_select(cb: types.CallbackQuery):
    kb = types.InlineKeyboardMarkup(row_width=2)
    amounts = [100, 200, 500, 1000]
    for amt in amounts:
        invoice_amt = round(amt * 1.03, 2)  # Сумма с +3%
        btn = f"{amt}₽ ➔ {invoice_amt}₽ (+3%)"
        kb.add(types.InlineKeyboardButton(btn, callback_data=f"cryptobot_pay_{amt}"))
    kb.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="pay_cancel"))
    await cb.message.edit_text(
        "💵 <b>Выберите сумму пополнения.\nВНИМАНИЕ: на баланс зачисляется ровно выбранная сумма, к оплате будет +3%!</b>",
        reply_markup=kb, parse_mode="HTML"
    )

async def cryptobot_pay(cb: types.CallbackQuery):
    orig_amt = int(cb.data.split("_")[-1])
    pay_amt = round(orig_amt * 1.03, 2)
    invoice_id, pay_url = create_invoice(pay_amt, "TON", cb.from_user.id)
    await cb.message.answer(
        f"🔗 <b>Ссылка для оплаты:</b>\n"
        f"<a href='{pay_url}'>Оплатить {pay_amt} TON</a>\n\n"
        f"После оплаты именно <b>{orig_amt} TON</b> зачисляется на ваш баланс.",
        parse_mode="HTML"
    )

async def cancel_pay(cb: types.CallbackQuery):
    await cb.message.edit_text("Пополнение отменено.")

# --- Регистрация хендлеров в main.py
# dp.register_message_handler(payment_entry, text="💸 Пополнить баланс")
# dp.register_callback_query_handler(cryptobot_sum_select, lambda c: c.data == "pay_cryptobot")
# dp.register_callback_query_handler(cryptobot_pay, lambda c: c.data.startswith("cryptobot_pay_"))
# dp.register_callback_query_handler(cancel_pay, lambda c: c.data == "pay_cancel")
