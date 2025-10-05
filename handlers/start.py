from aiogram import types
from keyboards.main_menu import get_main_menu
from keyboards.language import get_language_keyboard
from utils.locale import L
from utils.db import get_user, set_lang
import psycopg2
from config import DB_CONFIG

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

def create_user(user_id, lang):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tg (id, lang, balance, status, created_at, updated_at)
        VALUES (%s, %s, 0, 'active', NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """, (user_id, lang))
    conn.commit()
    cur.close()
    conn.close()

def register(dp):
    @dp.message_handler(commands=['start'])
    async def start_command(message: types.Message):
        user_id = message.from_user.id
        info = get_user(user_id)
        
        # Если пользователь не существует — показать выбор языка
        if not info:
            await message.answer(
                "🇷🇺 Выберите язык / 🇬🇧 Choose language:",
                reply_markup=get_language_keyboard()
            )
        else:
            # Пользователь уже есть — показать приветствие
            lang = "ru"
            if 'lang' in info and info['lang'] in ['ru', 'en']:
                lang = info['lang']
            await message.answer(L("start_text", lang), reply_markup=get_main_menu(user_id), parse_mode="HTML")
    
    @dp.callback_query_handler(lambda cb: cb.data.startswith("set_lang_"))
    async def set_language_start(cb: types.CallbackQuery):
        user_id = cb.from_user.id
        info = get_user(user_id)
        lang_code = cb.data.split("_")[-1]
        
        # Если пользователь новый — создать его с выбранным языком
        if not info:
            create_user(user_id, lang_code)
            info = get_user(user_id)
        else:
            # Если пользователь уже есть — обновить язык
            set_lang(user_id, lang_code)
            info = get_user(user_id)
        
        # Получить актуальный язык
        updated_lang = info.get('lang', 'ru')
        
        # Показать приветствие на выбранном языке
        await cb.message.edit_text(
            L("start_text", updated_lang),
            reply_markup=get_main_menu(user_id),
            parse_mode="HTML"
        )
        await cb.answer()
